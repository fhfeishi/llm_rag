from __future__ import annotations

import uuid

from .llm import LLMClient
from .models import LoadedDocument, RagIndex, TreeNode


def build_index(document: LoadedDocument, llm: LLMClient | None = None, summarize: bool = True) -> RagIndex:
    children = []
    for part in document.parts:
        summary = _summarize_part(part.text, llm) if summarize and part.text and llm else _first_lines(part.text)
        children.append(
            TreeNode(
                id=part.id,
                title=part.title or part.id,
                summary=summary,
                text=part.text,
                source_part_ids=[part.id],
                metadata=part.metadata,
            )
        )

    root_summary = _summarize_children(document.title, children, llm) if summarize and llm else ""
    root = TreeNode(
        id="root",
        title=document.title,
        summary=root_summary,
        source_part_ids=[part.id for part in document.parts],
        children=children,
        metadata=document.metadata,
    )
    return RagIndex(
        id=str(uuid.uuid4()),
        title=document.title,
        source=document.source,
        root=root,
        metadata={"part_count": len(document.parts)},
    )


def flatten_nodes(node: TreeNode, include_root: bool = False) -> list[TreeNode]:
    nodes = [node] if include_root else []
    for child in node.children:
        nodes.append(child)
        nodes.extend(flatten_nodes(child, include_root=False))
    return nodes


def tree_for_prompt(index: RagIndex) -> list[dict]:
    return [
        {
            "id": node.id,
            "title": node.title,
            "summary": node.summary,
            "metadata": node.metadata,
        }
        for node in flatten_nodes(index.root)
    ]


def _summarize_part(text: str, llm: LLMClient) -> str:
    prompt = f"""
Summarize this document part for retrieval.
Keep the summary factual and compact.

Text:
{text[:12000]}

Return only the summary.
"""
    return llm.complete(prompt).strip()


def _summarize_children(title: str, children: list[TreeNode], llm: LLMClient) -> str:
    child_summaries = "\n".join(f"- {node.title}: {node.summary}" for node in children)
    prompt = f"""
Create a compact document-level summary for retrieval.

Document title: {title}
Sections:
{child_summaries}

Return only the summary.
"""
    return llm.complete(prompt).strip()


def _first_lines(text: str, limit: int = 500) -> str:
    return " ".join(text.split())[:limit]
