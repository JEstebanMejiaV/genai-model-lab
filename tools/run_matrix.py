from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: List[str]) -> int:
    print("\n$ " + " ".join(cmd))
    p = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return int(p.returncode)


def main() -> int:
    ap = argparse.ArgumentParser(description="Ejecuta una misma suite para multiples modelos")
    ap.add_argument("--suite", required=True, help="Nombre de suite (carpeta en suites/)")
    ap.add_argument("--models", nargs="+", required=True, help="Ids de modelos en models/registry.yml")
    ap.add_argument("--tasks", nargs="*", default=None, help="Lista de task ids (por defecto todas)")
    ap.add_argument("--max-cases", type=int, default=None, help="Limita cantidad de casos por tarea")
    ap.add_argument("--system", default="Eres un asistente util y preciso.", help="System prompt")
    ap.add_argument("--aggregate", action="store_true", help="Si se activa, corre aggregate al final")
    args = ap.parse_args()

    base = [sys.executable, "tools/run_suite.py", "--suite", args.suite, "--system", args.system]
    if args.tasks:
        base += ["--tasks", *args.tasks]
    if args.max_cases is not None:
        base += ["--max-cases", str(args.max_cases)]

    rc_any = 0
    for mid in args.models:
        cmd = base + ["--model", mid]
        rc = _run(cmd)
        if rc != 0:
            rc_any = rc

    if args.aggregate:
        rc = _run([sys.executable, "tools/aggregate.py"])
        if rc != 0:
            rc_any = rc

    return rc_any


if __name__ == "__main__":
    raise SystemExit(main())
