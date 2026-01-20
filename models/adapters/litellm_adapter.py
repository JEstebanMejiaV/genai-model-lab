from __future__ import annotations

import time
from typing import Any, Dict

from .base import BaseAdapter, GenResult


class LiteLLMAdapter(BaseAdapter):
    """Adapter de ejemplo con LiteLLM.

    Requiere: pip install litellm
    Configura credenciales según el provider que uses.
    """

    def __init__(self) -> None:
        try:
            import litellm  # type: ignore
        except Exception as e:
            raise RuntimeError("Instala 'litellm' para usar LiteLLMAdapter") from e

        self._litellm = litellm

    def generate(self, *, system: str, user: str, params: Dict[str, Any]) -> GenResult:
        model = params.get("model")
        if not model:
            raise ValueError("params.model es requerido para LiteLLMAdapter")

        temperature = float(params.get("temperature", 0.0))
        top_p = float(params.get("top_p", 1.0))
        max_tokens = int(params.get("max_tokens", 1200))

        t0 = time.time()
        resp = self._litellm.completion(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        latency = int((time.time() - t0) * 1000)

        choice0 = resp["choices"][0]
        text = choice0["message"]["content"] or ""
        usage = resp.get("usage", {})
        # Normaliza algunos campos comunes
        usage_norm = {
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "usd_estimate": usage.get("total_cost"),
        }
        return GenResult(text=text, usage=usage_norm, latency_ms=latency)
