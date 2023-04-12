CREATE OR REPLACE FUNCTION update_updated_at_column()   
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified = now();
    RETURN NEW;   
END;
$$ language 'plpgsql';


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE watchlist (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    imdb_id TEXT NOT NULL,
    watched BOOL NOT NULL,
    rating SMALLINT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER watchlist_updated_at_refresh BEFORE UPDATE ON watchlist FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

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