from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class GenResult:
    text: str
    usage: Dict[str, Any]
    latency_ms: Optional[int] = None


class BaseAdapter:
    """Interfaz mínima para adapters."""

    def generate(self, *, system: str, user: str, params: Dict[str, Any]) -> GenResult:
        raise NotImplementedError
