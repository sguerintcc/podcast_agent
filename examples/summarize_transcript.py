"""Summarize a transcript using the echo LLM client."""

from __future__ import annotations

import logging

from podcast_agent.llm import EchoLLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAMPLE_TRANSCRIPT = """
Welcome to the show! Today we explore how to automate podcast workflows,
including feed monitoring, transcript retrieval, and summarization.
""".strip()


def main() -> None:
    llm = EchoLLMClient()
    result = llm.summarize_and_tag(SAMPLE_TRANSCRIPT, title="Automation for Podcasters")
    logger.info("Summary: %s", result.summary)
    logger.info("Tags: %s", ", ".join(result.tags))


if __name__ == "__main__":
    main()
