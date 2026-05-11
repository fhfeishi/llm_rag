from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RagConfig(BaseModel):
    model: str | None = None
    temperature: float = 0
    summarize: bool = True
    top_k: int = 5
    max_context_chars: int = 16000
    workspace: Path | None = None
    metadata: dict = Field(default_factory=dict)
