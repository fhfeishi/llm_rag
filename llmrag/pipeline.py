from __future__ import annotations

from .indexer import build_index
from .llm import LLMClient
from .loaders import load_file
from .models import Answer, LoadedDocument, RagIndex
from .retriever import build_context, retrieve


class LlmRag:
    def __init__(self, model: str | None = None):
        self.llm = LLMClient(model) if model else None

    def load(self, path: str) -> LoadedDocument:
        return load_file(path)

    def index_file(self, path: str, summarize: bool = True) -> RagIndex:
        document = self.load(path)
        return build_index(document, llm=self.llm, summarize=summarize)

    def retrieve(self, query: str, index: RagIndex, top_k: int = 5):
        return retrieve(query, index, llm=self.llm, top_k=top_k)

    def answer(self, query: str, index: RagIndex, top_k: int = 5) -> Answer:
        retrieval = self.retrieve(query, index, top_k=top_k)
        context = build_context(retrieval)
        if not self.llm:
            text = context[:1000] if context else "No LLM configured and no context found."
            return Answer(query=query, answer=text, retrieval=retrieval, context=context)

        prompt = f"""
                Answer the query using only the provided context.
                If the context is insufficient, say what is missing.
                
                Query: {query}
                
                Context:
                {context}
                
                Return a concise answer.
                """
        return Answer(
            query=query,
            answer=self.llm.complete(prompt).strip(),
            retrieval=retrieval,
            context=context,
        )
