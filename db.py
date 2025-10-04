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
    conn.commit()
    return conn


def save_message(conn, msg_id, chat_id, sender_id, date, text, mtype):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO messages (id, chat_id, sender_id, date, message, type) VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, chat_id, sender_id, str(date), text, mtype),
    )
    conn.commit()
