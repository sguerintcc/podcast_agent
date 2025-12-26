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
    duration_seconds: int | None = None
    is_probable_podcast: bool = True


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
            duration_seconds = _parse_duration(
                getattr(entry, "itunes_duration", None) or getattr(entry, "duration", None)
            )
            is_podcast = _looks_like_podcast(entry, duration_seconds)
            if not is_podcast:
                continue
            episode_id = getattr(entry, "id", None) or getattr(entry, "guid", None) or entry.link
            episodes.append(
                Episode(
                    feed_url=feed_url,
                    episode_id=str(episode_id),
                    title=entry.title,
                    link=entry.link,
                    published=published,
                    duration_seconds=duration_seconds,
                    is_probable_podcast=is_podcast,
                )
            )
        return episodes

    def newest_first(self, episodes: Iterable[Episode]) -> List[Episode]:
        return sorted(
            episodes,
            key=lambda ep: ep.published or dt.datetime.min,
            reverse=True,
        )


def _parse_duration(raw: object) -> int | None:
    """Return a duration in seconds if it can be parsed from RSS fields."""

    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return int(raw)

    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return None

        if raw.isdigit():
            return int(raw)

        if raw.startswith("PT"):
            # Very small ISO-8601 subset (e.g., PT5M, PT1H30M)
            total = 0
            number = ""
            for ch in raw[2:]:
                if ch.isdigit():
                    number += ch
                    continue
                if ch in {"H", "M", "S"} and number:
                    value = int(number)
                    if ch == "H":
                        total += value * 3600
                    elif ch == "M":
                        total += value * 60
                    else:
                        total += value
                    number = ""
            return total or None

        if ":" in raw:
            parts = raw.split(":")
            if all(part.isdigit() for part in parts):
                seconds = 0
                for part in parts:
                    seconds = seconds * 60 + int(part)
                return seconds
    return None


def _looks_like_podcast(entry: object, duration_seconds: int | None) -> bool:
    """Best-effort guess to keep full podcast items and drop shorts."""

    title = getattr(entry, "title", "")
    lower_title = title.lower()
    link = getattr(entry, "link", "").lower()

    if "shorts" in link or "#shorts" in lower_title or lower_title.endswith(" short"):
        return False

    if duration_seconds is not None:
        if duration_seconds < 7 * 60:
            return False
        if duration_seconds >= 10 * 60:
            return True

    short_markers = (
        "trailer",
        "preview",
        "promo",
        "clip",
        "short",
        "teaser",
        "minisode",
        "bonus",
    )
    if any(marker in lower_title for marker in short_markers):
        return False

    description = getattr(entry, "summary", "") or getattr(entry, "description", "")
    if isinstance(description, str) and "#shorts" in description.lower():
        return False

    return True
