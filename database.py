import aiosqlite

DB_NAME = "valentines.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT,
            last_name TEXT,
            group_name TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS valentines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            recipient_fullname TEXT,
            recipient_id INTEGER,
            message TEXT,
            delivered INTEGER DEFAULT 0
        )
        """)

        await db.commit()


async def add_user(telegram_id, first_name, last_name, group_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (telegram_id, first_name, last_name, group_name)
        VALUES (?, ?, ?, ?)
        """, (telegram_id, first_name, last_name, group_name))
        await db.commit()


async def get_user_by_telegram_id(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return await cursor.fetchone()


async def get_user_by_fullname(fullname):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT * FROM users 
        WHERE first_name || ' ' || last_name = ?
        """, (fullname,))
        return await cursor.fetchone()


async def save_valentine(sender_id, recipient_fullname, recipient_id, message, delivered):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO valentines 
        (sender_id, recipient_fullname, recipient_id, message, delivered)
        VALUES (?, ?, ?, ?, ?)
        """, (sender_id, recipient_fullname, recipient_id, message, delivered))
        await db.commit()


async def get_pending_valentines(recipient_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT id, message FROM valentines
        WHERE recipient_id = ? AND delivered = 0
        """, (recipient_id,))
        return await cursor.fetchall()


async def mark_delivered(valentine_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        UPDATE valentines SET delivered = 1 WHERE id = ?
        """, (valentine_id,))
        await db.commit()
