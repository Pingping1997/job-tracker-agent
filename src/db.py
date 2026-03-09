import sqlite3
from pathlib import Path

DB_PATH = Path("data/jobs.db")


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization TEXT NOT NULL,
        title TEXT,
        location TEXT,
        posted_date TEXT,
        url TEXT UNIQUE,
        summary TEXT,
        matched_keywords TEXT,
        relevance_score INTEGER DEFAULT 0,
        first_seen TEXT,
        last_seen TEXT
    )
    """)

    conn.commit()
    conn.close()


def upsert_job(job: dict) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO jobs (
        organization, title, location, posted_date, url, summary,
        matched_keywords, relevance_score, first_seen, last_seen
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ON CONFLICT(url) DO UPDATE SET
        title = excluded.title,
        location = excluded.location,
        posted_date = excluded.posted_date,
        summary = excluded.summary,
        matched_keywords = excluded.matched_keywords,
        relevance_score = excluded.relevance_score,
        last_seen = datetime('now')
    """, (
        job["organization"],
        job.get("title", ""),
        job.get("location", ""),
        job.get("posted_date", ""),
        job["url"],
        job.get("summary", ""),
        job.get("matched_keywords", ""),
        job.get("relevance_score", 0),
    ))

    conn.commit()
    conn.close()