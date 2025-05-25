import sqlite3

def get_db():
    return sqlite3.connect("chatbot_app.db")

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        is_admin INTEGER DEFAULT 0
    )''')

    # Series table
    c.execute('''CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )''')

    # Videos table
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        script TEXT,
        series_id INTEGER,
        series_number INTEGER,
        video_url TEXT,
        FOREIGN KEY(series_id) REFERENCES series(id)
    )''')

    # Saved videos table
    c.execute('''CREATE TABLE IF NOT EXISTS user_saved_videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        video_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(video_id) REFERENCES videos(id)
    )''')

    conn.commit()
    conn.close()