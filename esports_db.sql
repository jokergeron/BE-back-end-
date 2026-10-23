-- =====================================================
-- Sistem Manajemen Turnamen Esports
-- Skema database PostgreSQL (5 tabel)
-- =====================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    captain_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_teams_captain FOREIGN KEY (captain_id) REFERENCES users(id)
);

CREATE TABLE tournaments (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    format VARCHAR(255) NOT NULL,
    max_teams INT NOT NULL,
    start_date DATE NOT NULL,
    status VARCHAR(255) NOT NULL DEFAULT 'open',
    CONSTRAINT fk_tournaments_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    tournament_id INT NOT NULL,
    team_id INT NOT NULL,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(255) NOT NULL DEFAULT 'pending',
    CONSTRAINT fk_reg_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    CONSTRAINT fk_reg_team FOREIGN KEY (team_id) REFERENCES teams(id),
    CONSTRAINT uq_reg UNIQUE (tournament_id, team_id)
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    tournament_id INT NOT NULL,
    team_a_id INT NOT NULL,
    team_b_id INT NOT NULL,
    winner_team_id INT,
    round INT NOT NULL,
    score_team_a INT NOT NULL DEFAULT 0,
    score_team_b INT NOT NULL DEFAULT 0,
    match_date TIMESTAMP NOT NULL,
    CONSTRAINT fk_matches_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    CONSTRAINT fk_matches_team_a FOREIGN KEY (team_a_id) REFERENCES teams(id),
    CONSTRAINT fk_matches_team_b FOREIGN KEY (team_b_id) REFERENCES teams(id),
    CONSTRAINT fk_matches_winner FOREIGN KEY (winner_team_id) REFERENCES teams(id)
);
