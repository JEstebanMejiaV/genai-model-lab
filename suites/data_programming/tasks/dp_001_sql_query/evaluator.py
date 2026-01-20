from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

from tools.utils import extract_sql, read_text


EXPECTED = [
    ("corporativo", 25.0),
    ("premium", 100.0),
    ("prepago", 20.0),
]


def evaluate(case: Dict[str, Any], model_output: str, workdir: str) -> Dict[str, Any]:
    wd = Path(workdir)
    sql = extract_sql(model_output)
    (wd / "model.sql").write_text(sql, encoding="utf-8")

    conn = sqlite3.connect(":memory:")
    try:
        schema = read_text(str(Path(__file__).parent / "schema.sql"))
        conn.executescript(schema)

        cur = conn.execute(sql)
        rows = cur.fetchall()

        # Normaliza floats
        def norm(rs: List[Tuple[Any, Any]]):
            out = []
            for p, a in rs:
                out.append((str(p), float(a)))
            return out

        got = norm(rows)
        exp = norm(EXPECTED)

        passed = got == exp
        (wd / "got.json").write_text(str(got), encoding="utf-8")

        score = 2 if passed else 0
        return {
            "pass_fail": passed,
            "scores": {"correctness": score, "score_total": score},
            "notes": "Comparación exacta contra EXPECTED",
        }
    except Exception as e:
        return {
            "pass_fail": False,
            "scores": {"correctness": 0, "score_total": 0},
            "notes": f"Error ejecutando SQL: {e}",
        }
    finally:
        conn.close()
