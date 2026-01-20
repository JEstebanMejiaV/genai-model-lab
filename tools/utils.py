from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: str, rows: Iterable[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(text: str) -> str:
    """Extrae el primer bloque de código; si no existe, devuelve el texto completo."""
    m = CODE_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip() + "\n"
    return text.strip() + "\n"


def extract_sql(text: str) -> str:
    """Extrae SQL desde bloque o desde el texto, intentando quedarnos con una sentencia."""
    raw = extract_code(text)
    # Toma hasta el primer ';' si existe
    semi = raw.find(";")
    if semi != -1:
        return raw[: semi + 1].strip()
    return raw.strip()
