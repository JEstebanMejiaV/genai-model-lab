from __future__ import annotations

import time
from typing import Any, Dict

from .base import BaseAdapter, GenResult


class MockAdapter(BaseAdapter):
    """Adapter determinista para CI y demos.

    Genera respuestas correctas para las tareas de ejemplo incluidas en este repo.
    """

    def generate(self, *, system: str, user: str, params: Dict[str, Any]) -> GenResult:
        t0 = time.time()
        text = self._route(user)
        latency = int((time.time() - t0) * 1000)
        return GenResult(text=text, usage={"input_tokens": None, "output_tokens": None, "usd_estimate": None}, latency_ms=latency)

    def _route(self, user: str) -> str:
        # Tarea: palindrome
        if "is_palindrome" in user and "Función" in user:
            return (
                "```python\n"
                "import re\n\n"
                "def is_palindrome(s: str) -> bool:\n"
                "    if s is None:\n"
                "        return False\n"
                "    cleaned = re.sub(r'[^0-9a-zA-Z]+', '', s).lower()\n"
                "    return cleaned == cleaned[::-1]\n"
                "```\n"
            )

        # Tarea: SQL
        if "Escribe UNA consulta SQL" in user and "SQLite" in user:
            return "SELECT program, SUM(amount) AS total_amount FROM calls WHERE strftime('%Y', call_date) = '2012' GROUP BY program ORDER BY program;"

        # Tarea: email formal
        if "Redacta un correo" in user and "Cordial" in user:
            return (
                "Cordial saludo,\n\n"
                "Le informo que, debido a una contingencia operativa, la entrega se ha reprogramado para el {new_date}. "
                "Lamentamos los inconvenientes y ya estamos ejecutando el plan de mitigación para evitar recurrencias.\n\n"
                "Agradecemos su comprensión. Si requiere información adicional, por favor indíquenoslo.\n\n"
                "Atentamente,\n"
                "Equipo de Soporte\n"
            )

        # Fallback
        return "No se encontró una ruta mock para esta tarea."
