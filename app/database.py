import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()

async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "city TEXT, "
                "path_to_tg TEXT, "
                "time_zone TEXT"
                )
    db.commit()
