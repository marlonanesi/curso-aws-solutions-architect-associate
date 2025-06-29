import aiosqlite

DB_PATH = "notificacoes.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mensagem TEXT NOT NULL,
                lida INTEGER DEFAULT 0,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def salvar_notificacao(mensagem: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO notificacoes (mensagem) VALUES (?)", (mensagem,))
        await db.commit()

async def listar_notificacoes():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT mensagem FROM notificacoes ORDER BY id DESC LIMIT 10")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
