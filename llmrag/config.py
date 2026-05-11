from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RagConfig(BaseModel):
    model: str | None = None
    local_base_url: str | None = None
    api_key: str = "local"
    temperature: float = 0
    timeout: float = 120
    summarize: bool = True
    top_k: int = 5
    max_context_chars: int = 16000
    workspace: Path | None = None
    metadata: dict = Field(default_factory=dict)
