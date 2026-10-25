-- =====================================================
-- Seed Data untuk Sistem Manajemen Turnamen Esports
-- Jalankan file ini di SQL Editor Supabase setelah esports_db.sql
-- Idempoten: Aman dieksekusi berulang kali (ON CONFLICT DO NOTHING)
-- =====================================================

-- 1. Insert Users (Organizer & Kapten Tim)
INSERT INTO users (id, username, email, password) VALUES
(1, 'admin_esports', 'admin@esports.org', 'pbkdf2_admin_hash_secret'),
(2, 'faker_t1', 'faker@t1.gg', 'pbkdf2_faker_hash_secret'),
(3, 'boaster_fnc', 'boaster@fnatic.com', 'pbkdf2_boaster_hash_secret'),
(4, 'f0rsaken_prx', 'f0rsaken@prx.gg', 'pbkdf2_prx_hash_secret'),
(5, 'lemon_rrq', 'lemon@rrq.id', 'pbkdf2_lemon_hash_secret')
ON CONFLICT (id) DO NOTHING;

-- 2. Insert Teams
INSERT INTO teams (id, name, captain_id) VALUES
(1, 'T1 Esports', 2),
(2, 'Fnatic', 3),
(3, 'Paper Rex', 4),
(4, 'RRQ Hoshi', 5)
ON CONFLICT (id) DO NOTHING;

-- 3. Insert Tournaments
INSERT INTO tournaments (id, user_id, name, format, max_teams, start_date, status) VALUES
(1, 1, 'Valorant Champions 2026', 'Double Elimination', 16, '2026-11-01', 'open'),
(2, 1, 'MPL Indonesia Season 18', 'Round Robin', 8, '2026-11-15', 'open'),
(3, 1, 'League of Legends Worlds 2026', 'Swiss Stage', 16, '2026-12-01', 'open'),
(4, 1, 'Community Shield Cup 2026', 'Single Elimination', 8, '2026-12-20', 'open')
ON CONFLICT (id) DO NOTHING;

-- 4. Insert Registrations
INSERT INTO registrations (id, tournament_id, team_id, status) VALUES
(1, 1, 2, 'approved'),
(2, 1, 3, 'approved'),
(3, 2, 4, 'approved')
ON CONFLICT (id) DO NOTHING;

-- 5. Insert Matches
INSERT INTO matches (id, tournament_id, team_a_id, team_b_id, winner_team_id, round, score_team_a, score_team_b, match_date) VALUES
(1, 1, 2, 3, 3, 1, 1, 2, '2026-11-02 18:00:00')
ON CONFLICT (id) DO NOTHING;

-- 6. Sinkronisasi sequence SERIAL PostgreSQL agar INSERT data baru selanjutnya tidak terjadi tabrakan primary key
SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1));
SELECT setval(pg_get_serial_sequence('teams', 'id'), COALESCE((SELECT MAX(id) FROM teams), 1));
SELECT setval(pg_get_serial_sequence('tournaments', 'id'), COALESCE((SELECT MAX(id) FROM tournaments), 1));
SELECT setval(pg_get_serial_sequence('registrations', 'id'), COALESCE((SELECT MAX(id) FROM registrations), 1));
SELECT setval(pg_get_serial_sequence('matches', 'id'), COALESCE((SELECT MAX(id) FROM matches), 1));

