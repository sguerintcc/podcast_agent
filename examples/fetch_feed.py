"""List episodes from an RSS feed using RSSFeedMonitor."""

from __future__ import annotations

import logging

from podcast_agent.feeds import RSSFeedMonitor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Replace this with your podcast feed URL (YouTube channel feeds are supported).
FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=YOUR_CHANNEL_ID"


def main() -> None:
    monitor = RSSFeedMonitor()
    episodes = monitor.newest_first(monitor.fetch_episodes(FEED_URL))
    for episode in episodes:
        logger.info("%s | %s", episode.published or "(no date)", episode.title)
        logger.info("Episode ID: %s", episode.episode_id)
        logger.info("Link: %s\n", episode.link)


if __name__ == "__main__":
    main()
