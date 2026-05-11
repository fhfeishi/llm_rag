from __future__ import annotations

import json
import re

from .indexer import flatten_nodes, tree_for_prompt
from .llm import LLMClient
from .models import RagIndex, RetrievalHit, RetrievalResult, TreeNode


def retrieve(query: str, index: RagIndex, llm: LLMClient | None = None, top_k: int = 5) -> RetrievalResult:
    node_map = {node.id: node for node in flatten_nodes(index.root)}
    if llm:
        result = _llm_retrieve(query, index, llm, top_k)
        for hit in result.hits:
            hit.node = node_map.get(hit.node_id)
        return result
    return _keyword_retrieve(query, node_map, top_k)


def build_context(result: RetrievalResult, max_chars: int = 16000) -> str:
    chunks = []
    total = 0
    for hit in result.hits:
        if not hit.node or not hit.node.text:
            continue
        chunk = f"[{hit.node.id}] {hit.node.title}\n{hit.node.text.strip()}"
        if total + len(chunk) > max_chars:
            break
        chunks.append(chunk)
        total += len(chunk)
    return "\n\n".join(chunks)


def _llm_retrieve(query: str, index: RagIndex, llm: LLMClient, top_k: int) -> RetrievalResult:
    prompt = f"""
You are retrieving evidence from a structured document index.
Select the smallest set of nodes likely to answer the query.

Query: {query}

Document tree:
{json.dumps(tree_for_prompt(index), ensure_ascii=False, indent=2)}

Return JSON only:
{{
  "reasoning": "short reason",
  "hits": [
    {{"node_id": "node id", "score": 0.0, "reason": "why this node matters"}}
  ]
}}
Limit hits to {top_k}.
"""
    data = llm.complete_json(prompt)
    return RetrievalResult(
        query=query,
        reasoning=data.get("reasoning", ""),
        hits=[RetrievalHit(**item) for item in data.get("hits", [])[:top_k]],
    )


def _keyword_retrieve(query: str, node_map: dict[str, TreeNode], top_k: int) -> RetrievalResult:
    terms = {term.lower() for term in re.findall(r"\w+", query) if len(term) > 2}
    hits = []
    for node in node_map.values():
        haystack = f"{node.title} {node.summary} {node.text}".lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            hits.append(RetrievalHit(node_id=node.id, score=float(score), reason="keyword match", node=node))
    hits.sort(key=lambda hit: hit.score, reverse=True)
    return RetrievalResult(query=query, hits=hits[:top_k], reasoning="Fallback keyword retrieval.")
