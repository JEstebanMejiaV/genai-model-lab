from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from tools.utils import read_jsonl


REPO_ROOT = Path(__file__).resolve().parents[1]


def iter_results_files(runs_dir: Path) -> List[Path]:
    return sorted(runs_dir.glob("**/results.jsonl"))


def safe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description="Agrega runs y construye un leaderboard simple")
    ap.add_argument("--runs-dir", default=str(REPO_ROOT / "runs"), help="Directorio de runs")
    ap.add_argument("--out-csv", default=str(REPO_ROOT / "reports" / "leaderboard.csv"))
    ap.add_argument("--out-md", default=str(REPO_ROOT / "reports" / "leaderboard.md"))
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    results_files = iter_results_files(runs_dir)

    # Agregación: promedio de score_total por (model_id, suite)
    agg: Dict[str, Dict[str, Any]] = {}

    for rf in results_files:
        # Inferir model_id y suite desde la ruta del run
        run_dir = rf.parent
        meta_path = run_dir / "run_meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        model_id = meta.get("model", {}).get("id")
        suite = meta.get("suite")
        key = f"{model_id}::{suite}"

        rows = read_jsonl(str(rf))
        if not rows:
            continue

        total = 0.0
        n = 0
        pass_n = 0
        for r in rows:
            scores = r.get("scores", {})
            # Convención: si existe score_total úsalo, si no suma scores numéricos
            if "score_total" in scores:
                s = safe_float(scores.get("score_total"))
            else:
                s = sum(safe_float(v) for v in scores.values())
            total += s
            n += 1
            if r.get("pass_fail") is True:
                pass_n += 1

        if key not in agg:
            agg[key] = {
                "model_id": model_id,
                "suite": suite,
                "cases": 0,
                "avg_score": 0.0,
                "pass_rate": 0.0,
            }

        agg[key]["cases"] += n
        # promedio simple ponderado por casos
        prev_cases = agg[key]["cases"] - n
        prev_avg = agg[key]["avg_score"]
        agg[key]["avg_score"] = ((prev_avg * prev_cases) + total) / max(1, prev_cases + n)

        prev_pr = agg[key]["pass_rate"]
        agg[key]["pass_rate"] = ((prev_pr * prev_cases) + pass_n) / max(1, prev_cases + n)

    rows_out = sorted(agg.values(), key=lambda x: (x["suite"], -x["avg_score"], -x["pass_rate"]))

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["suite", "model_id", "cases", "avg_score", "pass_rate"])
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    md_lines = ["# Leaderboard\n", "| Suite | Model | Cases | Avg score | Pass rate |\n", "|---|---:|---:|---:|---:|\n"]
    for r in rows_out:
        md_lines.append(
            f"| {r['suite']} | {r['model_id']} | {r['cases']} | {r['avg_score']:.3f} | {r['pass_rate']:.3f} |\n"
        )
    out_md.write_text("".join(md_lines), encoding="utf-8")

    print(f"CSV: {out_csv}")
    print(f"MD:  {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
