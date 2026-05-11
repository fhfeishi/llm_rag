from __future__ import annotations

import json
from pathlib import Path

from .models import RagIndex


def save_index(index: RagIndex, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(index.model_dump_json(indent=2), encoding="utf-8")
    return target


def load_index(path: str | Path) -> RagIndex:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return RagIndex.model_validate(data)
