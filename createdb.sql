CREATE TABLE meme
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    created DATETIME,
    meme_type VARCHAR(32),
    comment TEXT,
    file_size INTEGER,
    file_id TEXT,
    file_unique_id TEXT UNIQUE
);
