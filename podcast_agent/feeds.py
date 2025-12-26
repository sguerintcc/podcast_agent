from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List

import feedparser


@dataclass
class Episode:
    feed_url: str
    episode_id: str
    title: str
    link: str
    published: dt.datetime | None


class RSSFeedMonitor:
    """Fetches episodes from an RSS feed."""

    def __init__(self, *, user_agent: str = "podcast-agent/0.1") -> None:
        self._user_agent = user_agent

    def fetch_episodes(self, feed_url: str) -> List[Episode]:
        parsed = feedparser.parse(feed_url, request_headers={"User-Agent": self._user_agent})
        episodes: List[Episode] = []
        for entry in parsed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed is not None:
                published = dt.datetime(*entry.published_parsed[:6])
            episode_id = getattr(entry, "id", None) or getattr(entry, "guid", None) or entry.link
            episodes.append(
                Episode(
                    feed_url=feed_url,
                    episode_id=str(episode_id),
                    title=entry.title,
                    link=entry.link,
                    published=published,
                )
            )
        return episodes

    def newest_first(self, episodes: Iterable[Episode]) -> List[Episode]:
        return sorted(
            episodes,
            key=lambda ep: ep.published or dt.datetime.min,
            reverse=True,
        )
