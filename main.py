from __future__ import annotations

import logging
import pathlib
from typing import Optional

from podcast_agent.config import Config, load_config_from_env
from podcast_agent.feeds import RSSFeedMonitor
from podcast_agent.llm import EchoLLMClient, OpenAILLMClient
from podcast_agent.pipeline import PodcastPipeline
from podcast_agent.storage import Storage
from podcast_agent.transcript import TranscriptClient, YouTubeTranscriptClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_llm_client(config: Config) -> OpenAILLMClient | EchoLLMClient:
    if config.llm.provider.lower() == "openai":
        if not config.llm.model:
            raise ValueError("OpenAI provider requires a model name in config")
        return OpenAILLMClient(model=config.llm.model, system_prompt=config.llm.system_prompt)
    logger.warning("Using echo LLM client; summaries will be placeholders")
    return EchoLLMClient()


def build_transcript_client() -> TranscriptClient:
    return YouTubeTranscriptClient()


def load_config(path: Optional[str] = None) -> Config:
    default_path = pathlib.Path(path or "config.json")
    if not default_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {default_path}. "
            "Create one using config.example.json as a template."
        )
    return load_config_from_env(default_path)


def main(config_path: Optional[str] = None) -> None:
    config = load_config(config_path)
    storage = Storage(pathlib.Path(config.database_path))
    pipeline = PodcastPipeline(
        feed_monitor=RSSFeedMonitor(),
        transcript_client=build_transcript_client(),
        llm_client=build_llm_client(config),
        storage=storage,
    )
    pipeline.run_once(config.feed_urls, language=config.youtube_language)


if __name__ == "__main__":
    main()
