import sqlite3


def init_db():
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    # 創建 messages 表
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
    # 新增：創建 users 表
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


# 新增：儲存或更新使用者的函數
def save_or_update_user(conn, user_id, first_name, last_name, username):
    cursor = conn.cursor()
    # 當 user_id 衝突時（即使用者已存在），則更新其名稱和使用者名稱
    # 這是處理使用者改名情況的關鍵
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
