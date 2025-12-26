"""Fetch a transcript for a YouTube video using YouTubeTranscriptClient."""

from __future__ import annotations

import logging

from podcast_agent.transcript import YouTubeTranscriptClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Provide a YouTube URL that has captions enabled.
VIDEO_URL = "https://www.youtube.com/watch?v=VIDEO_ID"
DEFAULT_LANGUAGE = "en"


def main() -> None:
    transcript_client = YouTubeTranscriptClient()
    transcript = transcript_client.fetch_transcript(VIDEO_URL, language=DEFAULT_LANGUAGE)
    logger.info("Transcript preview:\n%s...", transcript[:500])


if __name__ == "__main__":
    main()
