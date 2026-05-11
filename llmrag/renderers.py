from __future__ import annotations

import html
import json
from typing import Any

from pydantic import BaseModel

from .models import Answer, OutputFormat, RagIndex


def render(obj: BaseModel | dict[str, Any], output_format: OutputFormat | str = OutputFormat.json) -> str:
    fmt = OutputFormat(output_format)
    data = _dump(obj)
    if fmt == OutputFormat.json:
        return json.dumps(data, ensure_ascii=False, indent=2)
    if fmt == OutputFormat.markdown:
        return _markdown(data)
    if fmt == OutputFormat.html:
        return _html(data)
    raise ValueError(f"Unsupported output format: {output_format}")


def render_answer(answer: Answer, output_format: OutputFormat | str = OutputFormat.markdown) -> str:
    fmt = OutputFormat(output_format)
    if fmt == OutputFormat.json:
        return render(answer, fmt)
    if fmt == OutputFormat.html:
        return _answer_html(answer)
    return _answer_markdown(answer)


def render_index(index: RagIndex, output_format: OutputFormat | str = OutputFormat.markdown) -> str:
    return render(index, output_format)


def _dump(obj: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    return obj


def _markdown(data: dict[str, Any]) -> str:
    return "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"


def _html(data: dict[str, Any]) -> str:
    body = html.escape(json.dumps(data, ensure_ascii=False, indent=2))
    return f"<pre>{body}</pre>"


def _answer_markdown(answer: Answer) -> str:
    sources = "\n".join(
        f"- `{hit.node_id}` {hit.node.title if hit.node else ''}: {hit.reason}"
        for hit in answer.retrieval.hits
    )
    return f"# Answer\n\n{answer.answer}\n\n## Sources\n\n{sources or '- No sources'}\n"


def _answer_html(answer: Answer) -> str:
    source_items = "".join(
        f"<li><code>{html.escape(hit.node_id)}</code> {html.escape(hit.node.title if hit.node else '')}: {html.escape(hit.reason)}</li>"
        for hit in answer.retrieval.hits
    )
    return f"<h1>Answer</h1><p>{html.escape(answer.answer)}</p><h2>Sources</h2><ul>{source_items}</ul>"
