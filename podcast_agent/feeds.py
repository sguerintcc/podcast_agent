from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Iterable, List

import feedparser
import yt_dlp


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


class YouTubeChannelMonitor:
    """Fetch episodes from a YouTube channel using yt-dlp.

    This monitor uses yt-dlp so it can walk a channel's uploads playlist and
    return the full video history without requiring YouTube Data API keys.
    """

    def __init__(self, *, user_agent: str = "podcast-agent/0.1", max_videos: int | None = None) -> None:
        self._user_agent = user_agent
        self._base_options: dict = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": False,
            "lazy_playlist": False,
            "cachedir": False,
        }
        # yt-dlp reads playlistend as the maximum number of entries to fetch.
        if max_videos is not None:
            self._base_options["playlistend"] = max_videos

    def fetch_episodes(self, channel_url: str) -> List[Episode]:
        options = {
            **self._base_options,
            "http_headers": {"User-Agent": self._user_agent},
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(channel_url, download=False)

        if info is None:
            return []

        entries = info.get("entries") if isinstance(info, dict) else None
        if entries is None:
            entries = [info]

        episodes: List[Episode] = []
        for entry in entries:
            if not entry:
                continue

            entry_dict = entry if isinstance(entry, dict) else {}

            duration_seconds = entry_dict.get("duration")
            published = _extract_published(entry_dict)

            lookup = SimpleNamespace(
                title=entry_dict.get("title", ""),
                link=(entry_dict.get("webpage_url") or entry_dict.get("url") or ""),
                summary=entry_dict.get("description", ""),
            )

            is_podcast = _looks_like_podcast(lookup, duration_seconds)
            if not is_podcast:
                continue

            episode_id = str(entry_dict.get("id") or entry_dict.get("url"))
            episodes.append(
                Episode(
                    feed_url=channel_url,
                    episode_id=episode_id,
                    title=entry_dict.get("title", ""),
                    link=(entry_dict.get("webpage_url") or entry_dict.get("url") or ""),
                    published=published,
                    duration_seconds=duration_seconds,
                    is_probable_podcast=is_podcast,
                )
            )

        return episodes


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


def _extract_published(entry: dict) -> dt.datetime | None:
    """Parse published timestamp from yt-dlp entries when available."""

    timestamp = entry.get("timestamp")
    if timestamp is not None:
        try:
            return dt.datetime.fromtimestamp(float(timestamp), tz=dt.timezone.utc)
        except (OverflowError, ValueError, OSError):
            return None

    upload_date = entry.get("upload_date")
    if isinstance(upload_date, str) and len(upload_date) == 8 and upload_date.isdigit():
        try:
            return dt.datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return None

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
