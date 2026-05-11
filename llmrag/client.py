from __future__ import annotations

from pathlib import Path

from .config import RagConfig
from .indexer import build_index
from .llm import LLMClient
from .loaders import load_file
from .models import Answer, LoadedDocument, OutputFormat, RagIndex, RetrievalResult
from .renderers import render_answer, render_index
from .retriever import build_context, retrieve
from .storage import load_index, save_index


class LlmRagClient:
    """Friendly facade for indexing files and asking questions."""

    def __init__(self, model: str | None = None, config: RagConfig | None = None, **overrides):
        data = config.model_dump() if config else {}
        if model is not None:
            data["model"] = model
        data.update({key: value for key, value in overrides.items() if value is not None})
        self.config = RagConfig(**data)
        self.llm = LLMClient(self.config.model, temperature=self.config.temperature) if self.config.model else None
        self.indexes: dict[str, RagIndex] = {}

    def load(self, path: str | Path) -> LoadedDocument:
        return load_file(path)

    def index_file(self, path: str | Path, *, summarize: bool | None = None) -> RagIndex:
        document = self.load(path)
        index = build_index(
            document,
            llm=self.llm,
            summarize=self.config.summarize if summarize is None else summarize,
        )
        self.indexes[index.id] = index
        return index

    def add_index(self, index: RagIndex) -> RagIndex:
        self.indexes[index.id] = index
        return index

    def get_index(self, index_id: str | None = None) -> RagIndex:
        if index_id:
            return self.indexes[index_id]
        if not self.indexes:
            raise ValueError("No index loaded. Call index_file() or load_index() first.")
        return next(reversed(self.indexes.values()))

    def retrieve(self, query: str, index: RagIndex | str | None = None, *, top_k: int | None = None) -> RetrievalResult:
        active_index = self._resolve_index(index)
        return retrieve(query, active_index, llm=self.llm, top_k=top_k or self.config.top_k)

    def ask(self, query: str, index: RagIndex | str | None = None, *, top_k: int | None = None) -> Answer:
        active_index = self._resolve_index(index)
        retrieval = self.retrieve(query, active_index, top_k=top_k)
        context = build_context(retrieval, max_chars=self.config.max_context_chars)
        if not self.llm:
            fallback = context[:1200] if context else "No LLM configured and no relevant context found."
            return Answer(query=query, answer=fallback, retrieval=retrieval, context=context)

        prompt = f"""
Answer the user query using only the provided context.
If the context is insufficient, say what is missing.

Query: {query}

Context:
{context}

Return a clear, concise answer.
"""
        answer = self.llm.complete(prompt).strip()
        return Answer(query=query, answer=answer, retrieval=retrieval, context=context)

    def save_index(self, index: RagIndex | str | None = None, path: str | Path | None = None) -> Path:
        active_index = self._resolve_index(index)
        target = Path(path) if path else self._default_index_path(active_index)
        return save_index(active_index, target)

    def load_index(self, path: str | Path) -> RagIndex:
        index = load_index(path)
        self.indexes[index.id] = index
        return index

    def render_index(self, index: RagIndex | str | None = None, output_format: OutputFormat | str = OutputFormat.markdown) -> str:
        return render_index(self._resolve_index(index), output_format)

    def render_answer(self, answer: Answer, output_format: OutputFormat | str = OutputFormat.markdown) -> str:
        return render_answer(answer, output_format)

    def _resolve_index(self, index: RagIndex | str | None) -> RagIndex:
        if isinstance(index, RagIndex):
            return index
        return self.get_index(index)

    def _default_index_path(self, index: RagIndex) -> Path:
        if not self.config.workspace:
            return Path(f"{index.id}.llmrag.json")
        self.config.workspace.mkdir(parents=True, exist_ok=True)
        return self.config.workspace / f"{index.id}.llmrag.json"
