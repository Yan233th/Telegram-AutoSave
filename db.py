import sqlite3


def init_db():
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER,
        sender_id INTEGER,
        date TEXT,
        message TEXT,
        type TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT
    )
    """)
    conn.commit()
    return conn


def save_message(conn, msg_id, chat_id, sender_id, date, text, mtype):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO messages (id, chat_id, sender_id, date, message, type) VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, chat_id, sender_id, str(date), text, mtype),
    )
    conn.commit()


def save_or_update_user(conn, user_id, first_name, last_name, username):
    cursor = conn.cursor()
    # When user_id conflicts (i.e., user already exists), update their name and username
    cursor.execute(
        """
        INSERT INTO users (id, first_name, last_name, username) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            username = excluded.username
        """,
        (user_id, first_name, last_name or "", username or ""),
    )
    conn.commit()
