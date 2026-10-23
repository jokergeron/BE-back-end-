import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# In-memory mock data jika belum terhubung ke database cloud
MOCK_USERS = [
    {"id": 1, "username": "admin_esports", "email": "admin@esports.org"},
    {"id": 2, "username": "faker_t1", "email": "faker@t1.gg"},
    {"id": 3, "username": "boaster_fnc", "email": "boaster@fnatic.com"},
    {"id": 4, "username": "f0rsaken_prx", "email": "f0rsaken@prx.gg"},
    {"id": 5, "username": "lemon_rrq", "email": "lemon@rrq.id"}
]

MOCK_TEAMS = [
    {"id": 1, "name": "T1 Esports", "captain_id": 2, "captain_name": "faker_t1"},
    {"id": 2, "name": "Fnatic", "captain_id": 3, "captain_name": "boaster_fnc"},
    {"id": 3, "name": "Paper Rex", "captain_id": 4, "captain_name": "f0rsaken_prx"},
    {"id": 4, "name": "RRQ Hoshi", "captain_id": 5, "captain_name": "lemon_rrq"}
]

MOCK_TOURNAMENTS = [
    {
        "id": 1,
        "name": "Valorant Champions 2026",
        "format": "Double Elimination",
        "max_teams": 16,
        "start_date": "2026-11-01",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
    },
    {
        "id": 2,
        "name": "MPL Indonesia Season 18",
        "format": "Round Robin",
        "max_teams": 8,
        "start_date": "2026-11-15",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
    },
    {
        "id": 3,
        "name": "League of Legends Worlds 2026",
        "format": "Swiss Stage",
        "max_teams": 16,
        "start_date": "2026-12-01",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
    }
]

MOCK_REGISTRATIONS = [
    {"id": 1, "tournament_id": 1, "team_id": 2, "team_name": "Fnatic", "status": "approved"},
    {"id": 2, "tournament_id": 1, "team_id": 3, "team_name": "Paper Rex", "status": "approved"},
    {"id": 3, "tournament_id": 2, "team_id": 4, "team_name": "RRQ Hoshi", "status": "approved"}
]

MOCK_MATCHES = [
    {
        "id": 1,
        "tournament_id": 1,
        "tournament_name": "Valorant Champions 2026",
        "round": 1,
        "team_a_name": "Fnatic",
        "team_b_name": "Paper Rex",
        "score_team_a": 1,
        "score_team_b": 2,
        "winner_name": "Paper Rex",
        "match_date": "2026-11-02 18:00:00"
    }
]

def get_db_connection():
    """Mengembalikan koneksi PostgreSQL jika DATABASE_URL tersedia."""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"[DB Warning] Gagal terhubung ke database: {e}. Menggunakan in-memory fallback.")
        return None
