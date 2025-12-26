"""Run the podcast pipeline with static components for quick testing."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

from podcast_agent.feeds import Episode, RSSFeedMonitor
from podcast_agent.llm import EchoLLMClient
from podcast_agent.pipeline import PodcastPipeline
from podcast_agent.storage import Storage
from podcast_agent.transcript import StaticTranscriptClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Sample feed data used for the demo pipeline.
FEED_URL = "https://example.com/demo-feed.xml"
DEMO_EPISODES: List[Episode] = [
    Episode(
        feed_url=FEED_URL,
        episode_id="demo-001",
        title="Automation for Podcasters",
        link="https://youtu.be/dQw4w9WgXcQ",
        published=None,
    ),
    Episode(
        feed_url=FEED_URL,
        episode_id="demo-002",
        title="Scaling Your Podcast Stack",
        link="https://youtu.be/dQw4w9WgXcQ",
        published=None,
    ),
]


class StaticFeedMonitor(RSSFeedMonitor):
    """A feed monitor that returns pre-defined episodes for demonstration."""

    def __init__(self, episodes: Iterable[Episode]):
        super().__init__()
        self._episodes = list(episodes)

    def fetch_episodes(self, feed_url: str) -> List[Episode]:
        return [ep for ep in self._episodes if ep.feed_url == feed_url]


SAMPLE_TRANSCRIPT = """
Welcome to the demo episode. This transcript is static and reused for each item.
The pipeline will echo a placeholder summary and tag for illustration purposes.
""".strip()


def main() -> None:
    storage = Storage(Path("examples/demo.db"))
    pipeline = PodcastPipeline(
        feed_monitor=StaticFeedMonitor(DEMO_EPISODES),
        transcript_client=StaticTranscriptClient(SAMPLE_TRANSCRIPT),
        llm_client=EchoLLMClient(),
        storage=storage,
    )
    pipeline.run_once([FEED_URL])
    logger.info("Stored %d episodes in %s", len(storage.fetch_all()), storage.db_path)


if __name__ == "__main__":
    main()
