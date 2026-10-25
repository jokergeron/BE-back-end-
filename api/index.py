import urllib.parse
from flask import Flask, jsonify, request, make_response

try:
    from api.db import (
        get_db_connection,
        MOCK_TOURNAMENTS,
        MOCK_TEAMS,
        MOCK_USERS,
        MOCK_REGISTRATIONS,
        MOCK_MATCHES
    )
except ImportError:
    from db import (
        get_db_connection,
        MOCK_TOURNAMENTS,
        MOCK_TEAMS,
        MOCK_USERS,
        MOCK_REGISTRATIONS,
        MOCK_MATCHES
    )

app = Flask(__name__)
app.url_map.strict_slashes = False

class VercelPathMiddleware:
    """Memperbaiki routing WSGI di serverless Vercel."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
        if '__path' in qs and qs['__path']:
            target_path = qs['__path'][0]
            if not target_path.startswith('/'):
                target_path = '/' + target_path
            environ['PATH_INFO'] = target_path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        res = make_response('', 204)
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return res

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
    return response

def register_route(rule, **options):
    def decorator(f):
        app.route(rule, **options)(f)
        if rule.startswith('/api/'):
            app.route(rule[4:], **options)(f)
        elif rule == '/api':
            app.route('/', **options)(f)
        elif not rule.startswith('/api') and rule != '/':
            app.route('/api' + rule, **options)(f)
        return f
    return decorator


# --- 1. Root & Health ---
@register_route('/')
def root():
    return jsonify({
        "status": "success",
        "service": "Esports Tournament Management REST API",
        "version": "1.0.0",
        "message": "Sistem Manajemen Turnamen Esports REST API siap digunakan",
        "endpoints": {
            "health": "/api/health",
            "tournaments": "/api/tournaments",
            "teams": "/api/teams",
            "matches": "/api/matches",
            "registrations": "/api/registrations"
        }
    }), 200

@register_route('/api/health')
def health_check():
    conn = get_db_connection()
    db_status = "connected" if conn else "fallback_mock_data"
    if conn:
        conn.close()
    return jsonify({
        "status": "healthy",
        "service": "Esports Tournament API",
        "database": db_status
    }), 200


# --- 2. Teams (Master Data) ---
@register_route('/api/teams')
def get_teams():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT t.id, t.name, t.captain_id, u.username AS captain_name, t.created_at
                FROM teams t
                LEFT JOIN users u ON t.captain_id = u.id
                ORDER BY t.id ASC;
            """)
            teams = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "total": len(teams), "data": teams}), 200
        except Exception:
            conn.close()

    return jsonify({"status": "success", "total": len(MOCK_TEAMS), "data": MOCK_TEAMS}), 200


# --- 3. Tournaments (Full CRUD) ---
@register_route('/api/tournaments', methods=['GET'])
def get_tournaments():
    status_filter = request.args.get('status', '').strip().lower()
    search = request.args.get('search', '').strip().lower()

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT t.id, t.name, t.format, t.max_teams, t.start_date, t.status,
                       t.user_id AS organizer_id, u.username AS organizer_name
                FROM tournaments t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE 1=1
            """
            params = []
            if status_filter:
                query += " AND LOWER(t.status) = %s"
                params.append(status_filter)
            if search:
                query += " AND LOWER(t.name) LIKE %s"
                params.append(f"%{search}%")
            query += " ORDER BY t.id ASC;"
            cur.execute(query, params)
            tournaments = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "total": len(tournaments), "data": tournaments}), 200
        except Exception:
            conn.close()

    # Fallback mock data
    filtered = MOCK_TOURNAMENTS
    if status_filter:
        filtered = [t for t in filtered if t['status'].lower() == status_filter]
    if search:
        filtered = [t for t in filtered if search in t['name'].lower()]
    return jsonify({"status": "success", "total": len(filtered), "data": filtered}), 200


@register_route('/api/tournaments/<int:tour_id>', methods=['GET'])
def get_tournament_detail(tour_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT t.id, t.name, t.format, t.max_teams, t.start_date, t.status,
                       t.user_id AS organizer_id, u.username AS organizer_name
                FROM tournaments t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.id = %s;
            """, (tour_id,))
            tour = cur.fetchone()
            if not tour:
                cur.close()
                conn.close()
                return jsonify({"status": "error", "message": f"Turnamen dengan ID {tour_id} tidak ditemukan"}), 404

            # Ambil tim yang terdaftar
            cur.execute("""
                SELECT r.id, r.team_id, tm.name AS team_name, r.status, r.registered_at
                FROM registrations r
                JOIN teams tm ON r.team_id = tm.id
                WHERE r.tournament_id = %s;
            """, (tour_id,))
            regs = cur.fetchall()
            cur.close()
            conn.close()
            tour['registered_teams'] = regs
            return jsonify({"status": "success", "data": tour}), 200
        except Exception:
            conn.close()

    # Fallback
    tour = next((t for t in MOCK_TOURNAMENTS if t['id'] == tour_id), None)
    if not tour:
        return jsonify({"status": "error", "message": f"Turnamen dengan ID {tour_id} tidak ditemukan"}), 404
    tour_copy = dict(tour)
    tour_copy['registered_teams'] = [r for r in MOCK_REGISTRATIONS if r['tournament_id'] == tour_id]
    return jsonify({"status": "success", "data": tour_copy}), 200


@register_route('/api/tournaments', methods=['POST'])
def create_tournament():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Request body harus berupa JSON object"}), 400

    name = str(data.get('name', '')).strip()
    fmt = str(data.get('format', 'Single Elimination')).strip()
    max_teams = data.get('max_teams', 16)
    start_date = str(data.get('start_date', '2026-11-01')).strip()
    user_id = data.get('user_id', 1)

    if not name:
        return jsonify({"status": "error", "message": "Field 'name' turnamen wajib diisi"}), 400
    if not isinstance(max_teams, int) or max_teams <= 0:
        return jsonify({"status": "error", "message": "Field 'max_teams' harus berupa integer positif"}), 400

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tournaments (user_id, name, format, max_teams, start_date, status)
                VALUES (%s, %s, %s, %s, %s, 'open')
                RETURNING id, user_id, name, format, max_teams, start_date, status;
            """, (user_id, name, fmt, max_teams, start_date))
            new_tour = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({
                "status": "success",
                "message": "Turnamen berhasil dibuat",
                "data": new_tour
            }), 201
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"status": "error", "message": f"Gagal membuat turnamen: {str(e)}"}), 500

    # Fallback
    new_id = max([t['id'] for t in MOCK_TOURNAMENTS], default=0) + 1
    new_tour = {
        "id": new_id,
        "user_id": user_id,
        "name": name,
        "format": fmt,
        "max_teams": max_teams,
        "start_date": start_date,
        "status": "open",
        "organizer_id": user_id,
        "organizer_name": "admin_esports"
    }
    MOCK_TOURNAMENTS.append(new_tour)
    return jsonify({
        "status": "success",
        "message": "Turnamen berhasil dibuat",
        "data": new_tour
    }), 201


@register_route('/api/tournaments/<int:tour_id>', methods=['PUT'])
def update_tournament(tour_id):
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Request body harus berupa JSON object"}), 400

    if 'max_teams' in data:
        max_teams_val = data['max_teams']
        if not isinstance(max_teams_val, int) or max_teams_val <= 0:
            return jsonify({"status": "error", "message": "Field 'max_teams' harus berupa integer positif"}), 400

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tournaments WHERE id = %s;", (tour_id,))
            existing = cur.fetchone()
            if not existing:
                cur.close()
                conn.close()
                return jsonify({"status": "error", "message": f"Turnamen dengan ID {tour_id} tidak ditemukan"}), 404

            name = data.get('name', existing['name'])
            fmt = data.get('format', existing['format'])
            max_teams = data.get('max_teams', existing['max_teams'])
            status = data.get('status', existing['status'])

            cur.execute("""
                UPDATE tournaments
                SET name = %s, format = %s, max_teams = %s, status = %s
                WHERE id = %s
                RETURNING id, user_id, name, format, max_teams, start_date, status;
            """, (name, fmt, max_teams, status, tour_id))
            updated = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({
                "status": "success",
                "message": "Data turnamen berhasil diperbarui",
                "data": updated
            }), 200
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"status": "error", "message": str(e)}), 500

    # Fallback
    tour = next((t for t in MOCK_TOURNAMENTS if t['id'] == tour_id), None)
    if not tour:
        return jsonify({"status": "error", "message": f"Turnamen dengan ID {tour_id} tidak ditemukan"}), 404

    if 'name' in data and data['name']:
        tour['name'] = str(data['name']).strip()
    if 'format' in data and data['format']:
        tour['format'] = str(data['format']).strip()
    if 'max_teams' in data and isinstance(data['max_teams'], int):
        tour['max_teams'] = data['max_teams']
    if 'status' in data and data['status']:
        tour['status'] = str(data['status']).strip()

    return jsonify({
        "status": "success",
        "message": "Data turnamen berhasil diperbarui",
        "data": tour
    }), 200


@register_route('/api/tournaments/<int:tour_id>', methods=['DELETE'])
def delete_tournament(tour_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tournaments WHERE id = %s;", (tour_id,))
            existing = cur.fetchone()
            if not existing:
                cur.close()
                conn.close()
                return jsonify({"status": "error", "message": f"Turnamen dengan ID {tour_id} tidak ditemukan"}), 404

            # Cek integritas relasional (registrations / matches)
            cur.execute("SELECT COUNT(*) AS count FROM registrations WHERE tournament_id = %s;", (tour_id,))
            reg_count = cur.fetchone()['count']
            if reg_count > 0:
                cur.close()
                conn.close()
                return jsonify({
                    "status": "error",
                    "message": f"Tidak dapat menghapus turnamen ID {tour_id} karena masih terdapat {reg_count} pendaftaran tim aktif (Relational Integrity Conflict)."
                }), 409

            cur.execute("DELETE FROM tournaments WHERE id = %s;", (tour_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({
                "status": "success",
                "message": f"Turnamen ID {tour_id} berhasil dihapus"
            }), 200
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"status": "error", "message": str(e)}), 500

    # Fallback
    tour_idx = next((i for i, t in enumerate(MOCK_TOURNAMENTS) if t['id'] == tour_id), None)
    if tour_idx is None:
        return jsonify({"status": "error", "message": f"Turnamen dengan ID {tour_id} tidak ditemukan"}), 404

    reg_count = sum(1 for r in MOCK_REGISTRATIONS if r['tournament_id'] == tour_id)
    if reg_count > 0:
        return jsonify({
            "status": "error",
            "message": f"Tidak dapat menghapus turnamen ID {tour_id} karena masih terdapat {reg_count} pendaftaran tim aktif (Relational Integrity Conflict)."
        }), 409

    deleted = MOCK_TOURNAMENTS.pop(tour_idx)
    return jsonify({
        "status": "success",
        "message": f"Turnamen '{deleted['name']}' berhasil dihapus"
    }), 200


# --- 4. Matches & Registrations ---
@register_route('/api/matches')
def get_matches():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT m.id, m.tournament_id, tr.name AS tournament_name, m.round,
                       m.team_a_id, ta.name AS team_a_name,
                       m.team_b_id, tb.name AS team_b_name,
                       m.score_team_a, m.score_team_b,
                       m.winner_team_id, tw.name AS winner_name,
                       m.match_date
                FROM matches m
                JOIN tournaments tr ON m.tournament_id = tr.id
                JOIN teams ta ON m.team_a_id = ta.id
                JOIN teams tb ON m.team_b_id = tb.id
                LEFT JOIN teams tw ON m.winner_team_id = tw.id
                ORDER BY m.id ASC;
            """)
            matches = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "total": len(matches), "data": matches}), 200
        except Exception:
            conn.close()

    return jsonify({"status": "success", "total": len(MOCK_MATCHES), "data": MOCK_MATCHES}), 200

@register_route('/api/registrations')
def get_registrations():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id, r.tournament_id, tr.name AS tournament_name,
                       r.team_id, tm.name AS team_name, r.status, r.registered_at
                FROM registrations r
                JOIN tournaments tr ON r.tournament_id = tr.id
                JOIN teams tm ON r.team_id = tm.id
                ORDER BY r.id ASC;
            """)
            regs = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "total": len(regs), "data": regs}), 200
        except Exception:
            conn.close()

    return jsonify({"status": "success", "total": len(MOCK_REGISTRATIONS), "data": MOCK_REGISTRATIONS}), 200


# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint tidak ditemukan (404)"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "message": "HTTP Method tidak diizinkan (405)"}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal Server Error (500)"}), 500
