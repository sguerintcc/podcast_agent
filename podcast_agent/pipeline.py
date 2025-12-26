from __future__ import annotations

import logging
from typing import Iterable

from podcast_agent.feeds import Episode, RSSFeedMonitor
from podcast_agent.llm import LLMClient
from podcast_agent.storage import Storage
from podcast_agent.transcript import TranscriptClient

logger = logging.getLogger(__name__)


class PodcastPipeline:
    def __init__(
        self,
        feed_monitor: RSSFeedMonitor,
        transcript_client: TranscriptClient,
        llm_client: LLMClient,
        storage: Storage,
    ) -> None:
        self.feed_monitor = feed_monitor
        self.transcript_client = transcript_client
        self.llm_client = llm_client
        self.storage = storage

    def run_once(self, feed_urls: Iterable[str], *, language: str = "en") -> None:
        for feed_url in feed_urls:
            logger.info("Checking feed %s", feed_url)
            episodes = self.feed_monitor.newest_first(
                self.feed_monitor.fetch_episodes(feed_url)
            )
            for episode in episodes:
                if self.storage.is_processed(feed_url, episode.episode_id):
                    logger.debug("Episode %s already processed", episode.episode_id)
                    continue
                self._process_episode(episode, language=language)

    def _process_episode(self, episode: Episode, *, language: str) -> None:
        logger.info("Processing episode %s", episode.title)
        transcript = self.transcript_client.fetch_transcript(
            episode.link, language=language
        )
        summary_result = self.llm_client.summarize_and_tag(
            transcript, title=episode.title
        )
        self.storage.save_episode(
            episode,
            transcript=transcript,
            summary=summary_result.summary,
            tags=summary_result.tags,
        )
        logger.info("Stored summary for %s", episode.title)
