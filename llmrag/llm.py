from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any


class LLMClient:
    def __init__(self, model: str, temperature: float = 0, max_retries: int = 3):
        self.model = model.removeprefix("litellm/")
        self.temperature = temperature
        self.max_retries = max_retries

    def complete(self, prompt: str, messages: list[dict[str, Any]] | None = None) -> str:
        litellm = _litellm()
        payload = list(messages or [])
        payload.append({"role": "user", "content": prompt})
        for attempt in range(self.max_retries):
            try:
                response = litellm.completion(
                    model=self.model,
                    messages=payload,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                logging.warning("LLM completion failed: %s", exc)
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
        return ""

    async def acomplete(self, prompt: str, messages: list[dict[str, Any]] | None = None) -> str:
        litellm = _litellm()
        payload = list(messages or [])
        payload.append({"role": "user", "content": prompt})
        for attempt in range(self.max_retries):
            try:
                response = await litellm.acompletion(
                    model=self.model,
                    messages=payload,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                logging.warning("Async LLM completion failed: %s", exc)
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1)
        return ""

    def complete_json(self, prompt: str) -> Any:
        return extract_json(self.complete(prompt))


def extract_json(content: str) -> Any:
    text = content.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].rsplit("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def _litellm():
    try:
        import litellm
    except ImportError as exc:
        raise RuntimeError("LLM calls require dependency: litellm") from exc
    litellm.drop_params = True
    return litellm
