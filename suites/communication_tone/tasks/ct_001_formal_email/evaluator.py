from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def evaluate(case: Dict[str, Any], model_output: str, workdir: str) -> Dict[str, Any]:
    wd = Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)
    wd.joinpath("output.txt").write_text(model_output, encoding="utf-8")

    text = model_output.strip()

    # Heurísticas simples
    has_saludo = "cordial saludo" in text.lower() or "estimad" in text.lower()
    has_cierre = "atentamente" in text.lower() or "cordialmente" in text.lower()
    has_date = case.get("new_date") in text
    wc = word_count(text)
    length_ok = 120 <= wc <= 220

    score = 0
    score += 1 if has_saludo else 0
    score += 1 if has_cierre else 0
    score += 1 if has_date else 0
    score += 1 if length_ok else 0

    # Normaliza a 0-2 para score_total
    score_total = 2 if score >= 3 else (1 if score == 2 else 0)

    return {
        "pass_fail": score_total >= 1,
        "scores": {
            "tone_formality": 1 if has_saludo and has_cierre else 0,
            "requirements": score_total,
            "score_total": score_total,
        },
        "notes": f"wc={wc}, saludo={has_saludo}, cierre={has_cierre}, fecha={has_date}",
    }
