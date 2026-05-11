from __future__ import annotations

import shutil
import os
from pathlib import Path

from pydantic import BaseModel

from .client import LlmRagClient


class IndexPathRequest(BaseModel):
    path: str
    model: str | None = None
    local_base_url: str | None = None
    summarize: bool = False


class AskRequest(BaseModel):
    query: str
    index_id: str | None = None
    model: str | None = None
    local_base_url: str | None = None
    top_k: int = 5
    output: str = "markdown"


def create_app(workspace: str | Path = ".llmrag_api"):
    try:
        from fastapi import FastAPI, File, HTTPException, UploadFile
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError("FastAPI server requires: fastapi uvicorn python-multipart") from exc

    workspace_path = Path(workspace)
    uploads_dir = workspace_path / "uploads"
    indexes_dir = workspace_path / "indexes"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="llmrag API", version="0.1.0")
    client = LlmRagClient(workspace=indexes_dir)

    @app.get("/health")
    def health():
        return {"status": "ok", "workspace": str(workspace_path)}

    @app.get("/", response_class=HTMLResponse)
    def home():
        return _home_html()

    @app.post("/indexes/path")
    def index_path(request: IndexPathRequest):
        path = Path(request.path).expanduser()
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        active_client = _client_for_model(request.model, indexes_dir, request.local_base_url)
        index = active_client.index_file(path, summarize=request.summarize)
        saved = active_client.save_index(index)
        client.add_index(index)
        return {"index_id": index.id, "title": index.title, "saved_to": str(saved)}

    @app.post("/indexes/upload")
    def upload_index(
        file: UploadFile = File(...),
        model: str | None = None,
        local_base_url: str | None = None,
        summarize: bool = False,
    ):
        target = uploads_dir / Path(file.filename or "upload.bin").name
        with target.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        active_client = _client_for_model(model, indexes_dir, local_base_url)
        index = active_client.index_file(target, summarize=summarize)
        saved = active_client.save_index(index)
        client.add_index(index)
        return {"index_id": index.id, "title": index.title, "saved_to": str(saved), "uploaded_to": str(target)}

    @app.post("/ask")
    def ask(request: AskRequest):
        active_client = _client_for_model(request.model, indexes_dir, request.local_base_url)
        if request.index_id:
            index = client.get_index(request.index_id)
            active_client.add_index(index)
        else:
            index = client.get_index()
            active_client.add_index(index)
        answer = active_client.ask(request.query, index, top_k=request.top_k)
        return {
            "index_id": index.id,
            "title": index.title,
            "answer": answer.answer,
            "rendered": active_client.render_answer(answer, request.output),
            "retrieval": answer.retrieval.model_dump(mode="json"),
        }

    @app.get("/indexes")
    def indexes():
        return [
            {"index_id": index.id, "title": index.title, "source": str(index.source.path)}
            for index in client.indexes.values()
        ]

    return app


def _client_for_model(model: str | None, workspace: Path, local_base_url: str | None = None) -> LlmRagClient:
    return LlmRagClient(model=model, local_base_url=local_base_url, workspace=workspace) if model else LlmRagClient(workspace=workspace)


def _home_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>llmrag quickstart</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 32px; line-height: 1.45; max-width: 960px; }
    input, textarea, button { font: inherit; }
    input, textarea { width: 100%; box-sizing: border-box; padding: 8px; margin: 6px 0 14px; }
    textarea { min-height: 90px; }
    button { padding: 8px 12px; cursor: pointer; }
    pre { background: #f6f6f6; padding: 12px; overflow: auto; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>llmrag quickstart</h1>
  <label>Local file path</label>
  <input id="path" placeholder="D:\\path\\to\\document.pdf" />
  <label>Model, optional</label>
  <input id="model" placeholder="deepseek/deepseek-v4-flash" />
  <label>Local base URL, optional</label>
  <input id="localBaseUrl" placeholder="http://127.0.0.1:8080/v1" />
  <button onclick="indexPath()">Index path</button>
  <p id="index"></p>
  <label>Question</label>
  <textarea id="query">What is this document about?</textarea>
  <button onclick="ask()">Ask</button>
  <pre id="output"></pre>
  <script>
    let indexId = null;
    async function indexPath() {
      const res = await fetch('/indexes/path', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          path: document.getElementById('path').value,
          model: document.getElementById('model').value || null,
          local_base_url: document.getElementById('localBaseUrl').value || null,
          summarize: Boolean(document.getElementById('model').value)
        })
      });
      const data = await res.json();
      indexId = data.index_id;
      document.getElementById('index').textContent = JSON.stringify(data);
    }
    async function ask() {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          index_id: indexId,
          query: document.getElementById('query').value,
          model: document.getElementById('model').value || null,
          local_base_url: document.getElementById('localBaseUrl').value || null
        })
      });
      const data = await res.json();
      document.getElementById('output').textContent = data.rendered || JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>"""


app = create_app(os.getenv("LLMRAG_WORKSPACE", ".llmrag_api"))
