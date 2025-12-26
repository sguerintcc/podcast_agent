from __future__ import annotations

import re
from typing import List

from youtube_transcript_api import YouTubeTranscriptApi


class TranscriptClient:
    def fetch_transcript(self, url: str, *, language: str = "en") -> str:
        raise NotImplementedError


class YouTubeTranscriptClient(TranscriptClient):
    """Fetches transcripts for YouTube links using youtube-transcript-api."""

    def __init__(self, *, languages: List[str] | None = None) -> None:
        self.languages = languages or ["en"]

    def fetch_transcript(self, url: str, *, language: str = "en") -> str:
        video_id = self._extract_video_id(url)
        language_list = [language, *self.languages] if language not in self.languages else self.languages
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=language_list)
        return "\n".join(chunk["text"] for chunk in transcript if chunk.get("text"))

    @staticmethod
    def _extract_video_id(url: str) -> str:
        match = re.search(r"v=([\w-]{11})", url)
        if match:
            return match.group(1)
        short_match = re.search(r"youtu\.be/([\w-]{11})", url)
        if short_match:
            return short_match.group(1)
        raise ValueError(f"Could not determine video id from URL: {url}")


class StaticTranscriptClient(TranscriptClient):
    """Simple client used for testing or environments without network access."""

    def __init__(self, transcript: str) -> None:
        self.transcript = transcript

    def fetch_transcript(self, url: str, *, language: str = "en") -> str:
        return self.transcript
