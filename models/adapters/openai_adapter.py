from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from .base import BaseAdapter, GenResult


def _get_env(name: str) -> Optional[str]:
    v = os.getenv(name)
    return v if v and v.strip() else None


class OpenAIAdapter(BaseAdapter):
    """Adapter OpenAI (y endpoints compatibles con la API de OpenAI).

    Uso típico:
    - OpenAI: define OPENAI_API_KEY (y opcionalmente OPENAI_BASE_URL).
    - DeepSeek u otro compatible: define DEEPSEEK_API_KEY + DEEPSEEK_BASE_URL y registra
      un modelo en `models/registry.yml` indicando `api_key_env` y `base_url_env`.

    Nota:
    - Este repo no fija dependencias de terceros por defecto. Si usas este adapter:
      `pip install openai`.
    """

    def __init__(self) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError("Instala el paquete 'openai' para usar OpenAIAdapter") from e

        self._OpenAI = OpenAI

    def generate(self, *, system: str, user: str, params: Dict[str, Any]) -> GenResult:
        model = params.get("model")
        if not model:
            raise ValueError("params.model es requerido para OpenAIAdapter")

        # Permite configurar credenciales por modelo (ideal para comparar proveedores)
        api_key_env = str(params.get("api_key_env") or "OPENAI_API_KEY")
        base_url_env = str(params.get("base_url_env") or "OPENAI_BASE_URL")

        api_key = _get_env(api_key_env)
        if not api_key:
            raise RuntimeError(f"Falta variable de entorno {api_key_env}")

        # base_url es opcional (solo necesario para endpoints compatibles)
        base_url = params.get("base_url") or _get_env(base_url_env)

        temperature = float(params.get("temperature", 0.0))
        top_p = float(params.get("top_p", 1.0))
        max_tokens = int(params.get("max_tokens", 1200))

        client = self._OpenAI(api_key=api_key, base_url=base_url) if base_url else self._OpenAI(api_key=api_key)

        t0 = time.time()
        resp = client.chat.completions.create(
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

        text = resp.choices[0].message.content or ""
        usage = {
            "input_tokens": getattr(resp.usage, "prompt_tokens", None),
            "output_tokens": getattr(resp.usage, "completion_tokens", None),
            "usd_estimate": None,
        }
        return GenResult(text=text, usage=usage, latency_ms=latency)
