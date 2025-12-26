from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import openai


@dataclass
class SummaryResult:
    summary: str
    tags: List[str]


class LLMClient:
    def summarize_and_tag(self, transcript: str, *, title: str | None = None) -> SummaryResult:
        raise NotImplementedError


class OpenAILLMClient(LLMClient):
    def __init__(self, model: str, system_prompt: str) -> None:
        self.model = model
        self.system_prompt = system_prompt

    def summarize_and_tag(self, transcript: str, *, title: str | None = None) -> SummaryResult:
        prompt = self._build_prompt(transcript, title)
        response = openai.chat.completions.create(
            model=self.model,
            messages=prompt,
            temperature=0.3,
        )
        content = response.choices[0].message.content
        if not content:
            return SummaryResult(summary="", tags=[])
        summary, tags = self._parse_response(content)
        return SummaryResult(summary=summary.strip(), tags=list(tags))

    def _build_prompt(self, transcript: str, title: str | None) -> List[dict]:
        title_prefix = f"Podcast title: {title}\n" if title else ""
        return [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"{title_prefix}Transcript:\n{transcript}\n\n"
                "Provide a 5-7 sentence summary and 3-6 comma-separated tags.",
            },
        ]

    @staticmethod
    def _parse_response(content: str) -> Tuple[str, Iterable[str]]:
        if "Tags:" in content:
            summary_part, tags_part = content.split("Tags:", 1)
            tags = [tag.strip() for tag in tags_part.split(",") if tag.strip()]
            return summary_part.strip(), tags
        return content.strip(), []


class EchoLLMClient(LLMClient):
    def summarize_and_tag(self, transcript: str, *, title: str | None = None) -> SummaryResult:
        preview = transcript[:500]
        summary = f"Summary placeholder for {title or 'episode'}: {preview}"
        return SummaryResult(summary=summary, tags=["placeholder"])
