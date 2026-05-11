from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class FileKind(str, Enum):
    text = "text"
    pdf = "pdf"
    pptx = "pptx"
    xlsx = "xlsx"
    image = "image"
    html = "html"
    code = "code"
    unknown = "unknown"


class OutputFormat(str, Enum):
    json = "json"
    markdown = "markdown"
    html = "html"


class SourceFile(BaseModel):
    path: Path
    kind: FileKind
    mime_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentPart(BaseModel):
    id: str
    text: str = ""
    title: str | None = None
    source_path: Path | None = None
    kind: FileKind = FileKind.unknown
    index: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LoadedDocument(BaseModel):
    source: SourceFile
    title: str
    parts: list[DocumentPart] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        return "\n\n".join(part.text for part in self.parts if part.text)


class TreeNode(BaseModel):
    id: str
    title: str
    summary: str = ""
    text: str = ""
    source_part_ids: list[str] = Field(default_factory=list)
    children: list["TreeNode"] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagIndex(BaseModel):
    id: str
    title: str
    source: SourceFile
    root: TreeNode
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalHit(BaseModel):
    node_id: str
    score: float = 0
    reason: str = ""
    node: TreeNode | None = None


class RetrievalResult(BaseModel):
    query: str
    hits: list[RetrievalHit] = Field(default_factory=list)
    reasoning: str = ""


class Answer(BaseModel):
    query: str
    answer: str
    retrieval: RetrievalResult
    context: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
