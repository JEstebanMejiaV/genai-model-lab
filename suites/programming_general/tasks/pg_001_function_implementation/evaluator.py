from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from tools.utils import extract_code


TESTS = """
import pytest
from solution import is_palindrome

@pytest.mark.parametrize(
    "s, expected",
    [
        ("Anita lava la tina", True),
        ("abc", False),
        ("A man, a plan, a canal: Panama", True),
        ("", True),
        (" ", True),
        (None, False),
        ("No 'x' in Nixon", True),
    ],
)
def test_is_palindrome(s, expected):
    assert is_palindrome(s) is expected
"""


def evaluate(case: Dict[str, Any], model_output: str, workdir: str) -> Dict[str, Any]:
    wd = Path(workdir)
    code = extract_code(model_output)
    (wd / "solution.py").write_text(code, encoding="utf-8")
    (wd / "test_solution.py").write_text(TESTS, encoding="utf-8")

    # Ejecuta pytest
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(wd),
            capture_output=True,
            text=True,
            timeout=20,
        )
        passed = proc.returncode == 0
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    except Exception as e:
        passed = False
        out = f"Evaluator error: {e}"

    (wd / "pytest_output.txt").write_text(out, encoding="utf-8")

    return {
        "pass_fail": passed,
        "scores": {
            "correctness": 2 if passed else 0,
            "score_total": 2 if passed else 0,
        },
        "notes": "pytest ejecutado; ver pytest_output.txt",
    }
