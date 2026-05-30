import sqlite3
import config


def _conn():
    return sqlite3.connect(config.DB_PATH)


def init():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id      INTEGER NOT NULL,
                event_date    TEXT NOT NULL,
                event_title   TEXT,
                fetched_at    TEXT NOT NULL,
                lowest        REAL,
                average       REAL,
                median        REAL,
                highest       REAL,
                listing_count INTEGER
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_event_fetched ON price_snapshots(event_id, fetched_at)")


def insert_snapshot(event_id, event_date, event_title, fetched_at, stats):
    with _conn() as c:
        c.execute("""
            INSERT INTO price_snapshots
                (event_id, event_date, event_title, fetched_at, lowest, average, median, highest, listing_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            event_date,
            event_title,
            fetched_at,
            stats.get("lowest_price"),
            stats.get("average_price"),
            stats.get("median_price"),
            stats.get("highest_price"),
            stats.get("listing_count"),
        ))


def get_snapshots(event_id, since_date=None):
    """Return rows ordered oldest-first, optionally filtered to since_date (YYYY-MM-DD)."""
    with _conn() as c:
        c.row_factory = sqlite3.Row
        if since_date:
            rows = c.execute("""
                SELECT * FROM price_snapshots
                WHERE event_id = ? AND fetched_at >= ?
                ORDER BY fetched_at ASC
            """, (event_id, since_date)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM price_snapshots
                WHERE event_id = ?
                ORDER BY fetched_at ASC
            """, (event_id,)).fetchall()
        return [dict(r) for r in rows]


def get_known_events():
    """Return distinct (event_id, event_date, event_title) we have data for."""
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute("""
            SELECT DISTINCT event_id, event_date, event_title
            FROM price_snapshots
            ORDER BY event_date
        """).fetchall()
        return [dict(r) for r in rows]
