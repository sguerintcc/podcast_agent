from __future__ import annotations

import json
import os
import pathlib
from dataclasses import dataclass, field
from typing import List, Optional


CONFIG_ENV_VAR = "PODCAST_AGENT_CONFIG"


@dataclass
class LLMConfig:
    provider: str = "echo"
    model: Optional[str] = None
    system_prompt: str = (
        "You are a helpful assistant summarizing podcast transcripts. "
        "Provide concise summaries and relevant tags."
    )


@dataclass
class Config:
    feed_urls: List[str] = field(default_factory=list)
    database_path: str = "podcasts.db"
    llm: LLMConfig = field(default_factory=LLMConfig)
    youtube_language: str = "en"

    @classmethod
    def load(cls, path: pathlib.Path) -> "Config":
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        llm_config = LLMConfig(**raw.get("llm", {}))
        return cls(
            feed_urls=raw.get("feed_urls", []),
            database_path=raw.get("database_path", "podcasts.db"),
            llm=llm_config,
            youtube_language=raw.get("youtube_language", "en"),
        )


def load_config_from_env(default_path: pathlib.Path) -> Config:
    env_path = pathlib.Path(os.environ.get(CONFIG_ENV_VAR, default_path))
    return Config.load(env_path)
