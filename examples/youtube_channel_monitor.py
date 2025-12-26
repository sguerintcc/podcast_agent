"""List uploads from a YouTube channel using YouTubeChannelMonitor."""

from __future__ import annotations

import logging

from podcast_agent.feeds import YouTubeChannelMonitor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Replace with any YouTube channel URL or handle URL.
# This example channel posts long-form conversations as well as shorts.
CHANNEL_URL = "https://www.youtube.com/@lexfridman"


def main() -> None:
    monitor = YouTubeChannelMonitor()
    episodes = monitor.fetch_episodes(CHANNEL_URL)
    for episode in monitor.newest_first(episodes):
        logger.info("%s | %s", episode.published or "(no date)", episode.title)
        logger.info("Episode ID: %s", episode.episode_id)
        logger.info("Link: %s\n", episode.link)


if __name__ == "__main__":
    main()
