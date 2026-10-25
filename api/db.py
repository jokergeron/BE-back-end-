import os
import copy
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# In-memory mock data template jika belum terhubung ke database cloud
INITIAL_USERS = [
    {"id": 1, "username": "admin_esports", "email": "admin@esports.org"},
    {"id": 2, "username": "faker_t1", "email": "faker@t1.gg"},
    {"id": 3, "username": "boaster_fnc", "email": "boaster@fnatic.com"},
    {"id": 4, "username": "f0rsaken_prx", "email": "f0rsaken@prx.gg"},
    {"id": 5, "username": "lemon_rrq", "email": "lemon@rrq.id"}
]

INITIAL_TEAMS = [
    {"id": 1, "name": "T1 Esports", "captain_id": 2, "captain_name": "faker_t1", "created_at": "2026-10-01 08:00:00"},
    {"id": 2, "name": "Fnatic", "captain_id": 3, "captain_name": "boaster_fnc", "created_at": "2026-10-01 08:00:00"},
    {"id": 3, "name": "Paper Rex", "captain_id": 4, "captain_name": "f0rsaken_prx", "created_at": "2026-10-01 08:00:00"},
    {"id": 4, "name": "RRQ Hoshi", "captain_id": 5, "captain_name": "lemon_rrq", "created_at": "2026-10-01 08:00:00"}
]

INITIAL_TOURNAMENTS = [
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
    },
    {
        "id": 4,
        "name": "Community Shield Cup 2026",
        "format": "Single Elimination",
        "max_teams": 8,
        "start_date": "2026-12-20",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
    }
]

INITIAL_REGISTRATIONS = [
    {
        "id": 1,
        "tournament_id": 1,
        "tournament_name": "Valorant Champions 2026",
        "team_id": 2,
        "team_name": "Fnatic",
        "status": "approved",
        "registered_at": "2026-10-20 10:00:00"
    },
    {
        "id": 2,
        "tournament_id": 1,
        "tournament_name": "Valorant Champions 2026",
        "team_id": 3,
        "team_name": "Paper Rex",
        "status": "approved",
        "registered_at": "2026-10-20 10:30:00"
    },
    {
        "id": 3,
        "tournament_id": 2,
        "tournament_name": "MPL Indonesia Season 18",
        "team_id": 4,
        "team_name": "RRQ Hoshi",
        "status": "approved",
        "registered_at": "2026-10-21 14:00:00"
    }
]

INITIAL_MATCHES = [
    {
        "id": 1,
        "tournament_id": 1,
        "tournament_name": "Valorant Champions 2026",
        "round": 1,
        "team_a_id": 2,
        "team_a_name": "Fnatic",
        "team_b_id": 3,
        "team_b_name": "Paper Rex",
        "score_team_a": 1,
        "score_team_b": 2,
        "winner_team_id": 3,
        "winner_name": "Paper Rex",
        "match_date": "2026-11-02 18:00:00"
    }
]

MOCK_USERS = copy.deepcopy(INITIAL_USERS)
MOCK_TEAMS = copy.deepcopy(INITIAL_TEAMS)
MOCK_TOURNAMENTS = copy.deepcopy(INITIAL_TOURNAMENTS)
MOCK_REGISTRATIONS = copy.deepcopy(INITIAL_REGISTRATIONS)
MOCK_MATCHES = copy.deepcopy(INITIAL_MATCHES)

def reset_mock_data():
    """Mereset data mock in-memory ke kondisi awal untuk isolasi pengujian."""
    global MOCK_USERS, MOCK_TEAMS, MOCK_TOURNAMENTS, MOCK_REGISTRATIONS, MOCK_MATCHES
    MOCK_USERS.clear()
    MOCK_USERS.extend(copy.deepcopy(INITIAL_USERS))
    MOCK_TEAMS.clear()
    MOCK_TEAMS.extend(copy.deepcopy(INITIAL_TEAMS))
    MOCK_TOURNAMENTS.clear()
    MOCK_TOURNAMENTS.extend(copy.deepcopy(INITIAL_TOURNAMENTS))
    MOCK_REGISTRATIONS.clear()
    MOCK_REGISTRATIONS.extend(copy.deepcopy(INITIAL_REGISTRATIONS))
    MOCK_MATCHES.clear()
    MOCK_MATCHES.extend(copy.deepcopy(INITIAL_MATCHES))

def get_db_connection():
    """Mengembalikan koneksi PostgreSQL jika DATABASE_URL tersedia."""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, connect_timeout=3)
        return conn
    except Exception as e:
        print(f"[DB Warning] Gagal terhubung ke database: {e}. Menggunakan in-memory fallback.")
        return None
