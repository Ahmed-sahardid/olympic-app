CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    age INTEGER NOT NULL,
    experience TEXT DEFAULT 'beginner',
    goals TEXT DEFAULT 'strength',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    program TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

