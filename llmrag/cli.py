from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .client import LlmRagClient
from .models import OutputFormat


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "ask":
        return _ask(args)
    if args.command == "index":
        return _index(args)
    if args.command == "show-index":
        return _show_index(args)

    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llmrag", description="Quick CLI for llmrag.")
    subparsers = parser.add_subparsers(dest="command")

    ask = subparsers.add_parser("ask", help="Index a file or load an index, then answer a query.")
    ask.add_argument("--file", help="File to index before asking.")
    ask.add_argument("--index", help="Existing .llmrag.json index to load.")
    ask.add_argument("--query", required=True, help="Question to answer.")
    ask.add_argument("--model", default=None, help="LiteLLM model name, e.g. deepseek/deepseek-v4-flash.")
    ask.add_argument("--workspace", default=".llmrag", help="Directory for saved indexes.")
    ask.add_argument("--top-k", type=int, default=5, help="Number of nodes to retrieve.")
    ask.add_argument("--output", choices=[item.value for item in OutputFormat], default=OutputFormat.markdown.value)
    ask.add_argument("--no-summarize", action="store_true", help="Skip LLM summaries while indexing.")
    ask.add_argument("--save-index", action="store_true", help="Persist the generated index.")

    index = subparsers.add_parser("index", help="Build and save an index for a file.")
    index.add_argument("--file", required=True, help="File to index.")
    index.add_argument("--model", default=None, help="LiteLLM model name.")
    index.add_argument("--workspace", default=".llmrag", help="Directory for saved indexes.")
    index.add_argument("--no-summarize", action="store_true", help="Skip LLM summaries while indexing.")
    index.add_argument("--output", choices=[item.value for item in OutputFormat], default=OutputFormat.json.value)

    show = subparsers.add_parser("show-index", help="Render an existing index.")
    show.add_argument("--index", required=True, help="Existing .llmrag.json index to load.")
    show.add_argument("--output", choices=[item.value for item in OutputFormat], default=OutputFormat.markdown.value)

    return parser


def _ask(args: argparse.Namespace) -> int:
    if not args.file and not args.index:
        raise SystemExit("Provide either --file or --index.")

    client = LlmRagClient(model=args.model, workspace=Path(args.workspace))
    if args.index:
        index = client.load_index(args.index)
    else:
        index = client.index_file(args.file, summarize=not args.no_summarize)
        if args.save_index:
            saved = client.save_index(index)
            _write_error(f"Saved index: {saved}\n")

    answer = client.ask(args.query, index, top_k=args.top_k)
    _write_output(client.render_answer(answer, args.output))
    return 0


def _index(args: argparse.Namespace) -> int:
    client = LlmRagClient(model=args.model, workspace=Path(args.workspace))
    index = client.index_file(args.file, summarize=not args.no_summarize)
    saved = client.save_index(index)
    _write_error(f"Saved index: {saved}\n")
    _write_output(client.render_index(index, args.output))
    return 0


def _show_index(args: argparse.Namespace) -> int:
    client = LlmRagClient()
    index = client.load_index(args.index)
    _write_output(client.render_index(index, args.output))
    return 0


def _write_output(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


def _write_error(text: str) -> None:
    sys.stderr.buffer.write(text.encode("utf-8", errors="replace"))


if __name__ == "__main__":
    raise SystemExit(main())
