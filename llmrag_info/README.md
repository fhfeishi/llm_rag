# llmrag

`llmrag` is a small, explicit package for LLM-native RAG over files and file trees.

The core idea is deliberately simple:

```text
files -> loaders -> structured tree -> LLM retrieval over the tree -> evidence context -> answer
```

It keeps PageIndex's useful insight, "reason over structure instead of only vector similarity", but exposes a cleaner package API for second-stage development.

## Quick Start

```python
from llmrag import LlmRagClient

client = LlmRagClient(model="deepseek/deepseek-v4-flash", workspace=".llmrag")
index = client.index_file("document.pdf")
answer = client.ask("What are the main conclusions?", index)

print(client.render_answer(answer, "markdown"))
client.save_index(index)
```

Without a model, the package still loads files, builds a simple tree, and uses keyword retrieval as a fallback.

## Main Modules

- `client.py`: high-level API for indexing, asking, rendering, saving, and loading.
- `models.py`: Pydantic models for documents, tree nodes, indexes, retrieval, and answers.
- `loaders.py`: file loading for txt, pdf, pptx, xlsx, jpg/png, html, and code files.
- `indexer.py`: turns loaded document parts into a structured retrieval index.
- `retriever.py`: LLM tree retrieval plus keyword fallback.
- `llm.py`: LiteLLM wrapper for OpenAI-compatible providers.
- `renderers.py`: JSON, Markdown, and HTML output.
- `storage.py`: index persistence.

## File Support

Current loaders support text, Markdown, code, HTML, PDF, PPTX, XLSX, and image file placeholders. Image understanding is intentionally separated from loading so we can add multimodal retrieval without muddying the text path.
