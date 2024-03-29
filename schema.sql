CREATE
OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = now();

RETURN NEW;

END;

$$ language 'plpgsql';

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE titles (
    id SERIAL PRIMARY KEY,
    imdb_id TEXT NOT NULL UNIQUE,
    title TEXT,
    date_released DATE,
    title_type TEXT,
    imdb_rating SMALLINT,
    imdb_rating_count INT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER titles_updated_at_refresh BEFORE
UPDATE
    ON titles FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TABLE title_episodes (
    id SERIAL PRIMARY KEY,
    episode_imdb_id TEXT NOT NULL UNIQUE,
    title_imdb_id TEXT NOT NULL REFERENCES titles(imdb_id) ON DELETE CASCADE,
    season_number SMALLINT NOT NULL,
    episode_number SMALLINT NOT NULL,
    title TEXT,
    date_released DATE,
    imdb_rating SMALLINT,
    imdb_rating_count INT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (title_imdb_id, season_number, episode_number)
);

CREATE TRIGGER title_episodes_updated_at_refresh BEFORE
UPDATE
    ON title_episodes FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TABLE watchlist (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    imdb_id TEXT NOT NULL REFERENCES titles(imdb_id) ON DELETE CASCADE,
    watched BOOL NOT NULL,
    rating SMALLINT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, imdb_id)
);

CREATE TRIGGER watchlist_updated_at_refresh BEFORE
UPDATE
    ON watchlist FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TABLE watchlist_seasons (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    imdb_id TEXT NOT NULL,
    season_number SMALLINT NOT NULL,
    watched BOOL NOT NULL,
    rating SMALLINT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id, imdb_id) REFERENCES watchlist(user_id, imdb_id) ON DELETE CASCADE,
    UNIQUE (user_id, imdb_id, season_number)
);

CREATE TRIGGER watchlist_seasons_updated_at_refresh BEFORE
UPDATE
    ON watchlist_seasons FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TABLE cache (
    id SERIAL PRIMARY KEY,
    api TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    key TEXT NOT NULL,
    response JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (api, endpoint, key)
);

CREATE INDEX cache_api_endpoint_key_idx ON cache (api, endpoint, key);
