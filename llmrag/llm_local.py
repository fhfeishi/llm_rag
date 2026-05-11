from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .llm import extract_json


@dataclass(frozen=True)
class LocalLLMEndpoint:
    """OpenAI-compatible local chat-completions endpoint."""

    base_url: str = "http://127.0.0.1:8080/v1"
    api_key: str = "local"
    timeout: float = 120

    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"


class LocalLLMClient:
    """Minimal client for local OpenAI-compatible LLM servers.

    Works with llama.cpp `llama-server`, vLLM's OpenAI API server, and other
    local runtimes exposing `/v1/chat/completions`.
    """

    def __init__(
        self,
        model: str = "local-model",
        base_url: str = "http://127.0.0.1:8080/v1",
        api_key: str = "local",
        temperature: float = 0,
        max_retries: int = 2,
        timeout: float = 120,
    ):
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.endpoint = LocalLLMEndpoint(base_url=base_url, api_key=api_key, timeout=timeout)

    def complete(self, prompt: str, messages: list[dict[str, Any]] | None = None) -> str:
        payload_messages = list(messages or [])
        payload_messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": payload_messages,
            "temperature": self.temperature,
            "stream": False,
        }
        data = self._post_json(payload)
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected local LLM response: {data}") from exc

    async def acomplete(self, prompt: str, messages: list[dict[str, Any]] | None = None) -> str:
        return await asyncio.to_thread(self.complete, prompt, messages)

    def complete_json(self, prompt: str) -> Any:
        return extract_json(self.complete(prompt))

    def healthcheck(self) -> bool:
        try:
            self.complete("Reply with only: ok")
            return True
        except Exception:
            return False

    def _post_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.endpoint.api_key}",
        }
        request = urllib.request.Request(
            self.endpoint.chat_completions_url,
            data=body,
            headers=headers,
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(request, timeout=self.endpoint.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    time.sleep(1)
        raise RuntimeError(
            "Local LLM request failed. Ensure your local OpenAI-compatible "
            f"server is running at {self.endpoint.base_url}."
        ) from last_error
