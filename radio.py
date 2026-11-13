import os, sqlite3, uuid
from urllib.parse import urlparse

DB_PATH = os.getenv("RADIO_DB_PATH", "/tmp/highrise_radio.sqlite3")

def _connect():
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""CREATE TABLE IF NOT EXISTS tracks (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL,
        requested_by TEXT NOT NULL, position INTEGER NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT NOT NULL
    )""")
    con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('paused','0')")
    con.commit()
    return con

class Radio:
    """SQLite-backed queue shared by the bot and web player in one Railway service."""
    async def add(self, url: str, requested_by: str):
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Only valid HTTP(S) URLs are accepted")
        title = parsed.path.rsplit("/", 1)[-1] or parsed.netloc
        item = {"id": str(uuid.uuid4())[:8], "title": title, "url": url,
                "requested_by": requested_by}
        con = _connect()
        try:
            pos = con.execute("SELECT COALESCE(MAX(position),0)+1 FROM tracks").fetchone()[0]
            con.execute("INSERT INTO tracks VALUES(?,?,?,?,?)",
                        (item["id"], item["title"], item["url"], item["requested_by"], pos))
            con.commit()
        finally:
            con.close()
        return item

    async def current(self):
        con = _connect()
        try:
            row = con.execute("SELECT * FROM tracks ORDER BY position LIMIT 1").fetchone()
            return dict(row) if row else None
        finally:
            con.close()

    async def queue_snapshot(self):
        con = _connect()
        try:
            return [dict(r) for r in con.execute("SELECT * FROM tracks ORDER BY position")]
        finally:
            con.close()

    async def skip(self):
        con = _connect()
        try:
            row = con.execute("SELECT id FROM tracks ORDER BY position LIMIT 1").fetchone()
            if row:
                con.execute("DELETE FROM tracks WHERE id=?", (row["id"],))
                con.commit()
        finally:
            con.close()

    async def set_paused(self, value: bool):
        con = _connect()
        try:
            con.execute("UPDATE settings SET value=? WHERE key='paused'", ("1" if value else "0",))
            con.commit()
        finally:
            con.close()

    async def is_paused(self):
        con = _connect()
        try:
            row = con.execute("SELECT value FROM settings WHERE key='paused'").fetchone()
            return bool(row and row["value"] == "1")
        finally:
            con.close()

    async def clear(self):
        con = _connect()
        try:
            con.execute("DELETE FROM tracks")
            con.commit()
        finally:
            con.close()
