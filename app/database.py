import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()

async def db_start():
    with db:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, 
                    tag TEXT, 
                    city TEXT, 
                    path_to_tg TEXT, 
                    time_zone TEXT
                    )
                """)
        db.commit()

async def add_user(user_id):
    with db:
        cur.execute("INSERT OR IGNORE INTO (user_id) VALUES (?)", (user_id),)
        db.commit()

async def update_user(user_id, field, value):
    with db:
        cur.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        db.commit()

async def get_user(user_id):
    with db:
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()
