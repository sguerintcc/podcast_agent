from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path
from typing import Iterable

from podcast_agent.feeds import Episode


class Storage:
    """Handles persistence of episodes, transcripts, and summaries."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_url TEXT NOT NULL,
                    episode_id TEXT NOT NULL,
                    title TEXT,
                    link TEXT,
                    published TEXT,
                    transcript TEXT,
                    summary TEXT,
                    tags TEXT,
                    processed_at TEXT,
                    UNIQUE(feed_url, episode_id)
                )
                """
            )

    def is_processed(self, feed_url: str, episode_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT 1 FROM episodes WHERE feed_url=? AND episode_id=? AND summary IS NOT NULL",
                (feed_url, episode_id),
            )
            return cur.fetchone() is not None

    def save_episode(
        self,
        episode: Episode,
        *,
        transcript: str,
        summary: str,
        tags: Iterable[str],
    ) -> None:
        tag_str = ",".join(tags)
        processed_at = dt.datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO episodes (feed_url, episode_id, title, link, published, transcript, summary, tags, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(feed_url, episode_id) DO UPDATE SET
                    title=excluded.title,
                    link=excluded.link,
                    published=excluded.published,
                    transcript=excluded.transcript,
                    summary=excluded.summary,
                    tags=excluded.tags,
                    processed_at=excluded.processed_at
                """,
                (
                    episode.feed_url,
                    episode.episode_id,
                    episode.title,
                    episode.link,
                    episode.published.isoformat() if episode.published else None,
                    transcript,
                    summary,
                    tag_str,
                    processed_at,
                ),
            )

    def list_missing(self, feed_url: str) -> list[tuple[str, str]]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT episode_id, title FROM episodes WHERE feed_url=? AND summary IS NULL",
                (feed_url,),
            )
            return cur.fetchall()

    def fetch_all(self) -> list[Episode]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT feed_url, episode_id, title, link, published FROM episodes"
            )
            return [
                Episode(
                    feed_url=row[0],
                    episode_id=row[1],
                    title=row[2],
                    link=row[3],
                    published=dt.datetime.fromisoformat(row[4]) if row[4] else None,
                )
                for row in cur.fetchall()
            ]
