from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from tools.utils import read_jsonl, read_text, sha256_text, write_jsonl


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_registry() -> Dict[str, Any]:
    path = REPO_ROOT / "models" / "registry.yml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_model(model_id: str) -> Dict[str, Any]:
    reg = load_registry()
    presets = reg.get("presets", {})
    for m in reg.get("models", []):
        if m.get("id") == model_id:
            preset_name = m.get("preset")
            preset = presets.get(preset_name, {}) if preset_name else {}
            params = dict(preset)
            params.update(m.get("params", {}) or {})
            return {
                "id": model_id,
                "provider": m.get("provider"),
                "params": params,
            }
    raise ValueError(f"Modelo no encontrado en registry.yml: {model_id}")


def build_adapter(provider: str):
    if provider == "mock":
        from models.adapters.mock_adapter import MockAdapter

        return MockAdapter()
    if provider == "openai":
        from models.adapters.openai_adapter import OpenAIAdapter

        return OpenAIAdapter()
    if provider == "litellm":
        from models.adapters.litellm_adapter import LiteLLMAdapter

        return LiteLLMAdapter()

    raise ValueError(f"Provider no soportado: {provider}")


def iter_tasks_for_suite(suite: str) -> List[Path]:
    tasks_dir = REPO_ROOT / "suites" / suite / "tasks"
    if not tasks_dir.exists():
        raise ValueError(f"Suite no encontrada: {suite}")
    return sorted([p for p in tasks_dir.iterdir() if p.is_dir()])


def load_task_config(task_dir: Path) -> Dict[str, Any]:
    cfg_path = task_dir / "task.yml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def import_evaluator(task_dir: Path):
    ev_path = task_dir / "evaluator.py"
    spec = importlib.util.spec_from_file_location(f"evaluator_{task_dir.name}", ev_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"No se pudo cargar evaluator: {ev_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    if not hasattr(module, "evaluate"):
        raise RuntimeError("evaluator.py debe exponer una función evaluate(case, model_output, workdir)")
    return module.evaluate


def git_commit() -> Optional[str]:
    head = REPO_ROOT / ".git" / "HEAD"
    if not head.exists():
        return None
    try:
        ref = head.read_text(encoding="utf-8").strip()
        if ref.startswith("ref:"):
            ref_path = REPO_ROOT / ".git" / ref.split(" ", 1)[1]
            return ref_path.read_text(encoding="utf-8").strip()
        return ref
    except Exception:
        return None


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Runner de suites para comparar modelos")
    ap.add_argument("--model", required=True, help="Id del modelo en models/registry.yml")
    ap.add_argument("--suite", required=True, help="Nombre de suite (carpeta en suites/)")
    ap.add_argument("--tasks", nargs="*", default=None, help="Lista de task ids (por defecto todas)")
    ap.add_argument("--max-cases", type=int, default=None, help="Limita cantidad de casos por tarea")
    ap.add_argument("--system", default="Eres un asistente útil y preciso.", help="System prompt")

    args = ap.parse_args()

    model_cfg = resolve_model(args.model)
    adapter = build_adapter(model_cfg["provider"])

    suite = args.suite
    task_dirs = iter_tasks_for_suite(suite)

    selected = set(args.tasks) if args.tasks else None

    now = dt.datetime.utcnow()
    date_dir = REPO_ROOT / "runs" / now.strftime("%Y-%m-%d")
    run_id = now.strftime("%H%M%S") + f"_{args.model}_{suite}"
    out_dir = date_dir / run_id
    ensure_dir(out_dir)
    ensure_dir(out_dir / "artifacts")

    meta = {
        "run_id": run_id,
        "timestamp_utc": now.isoformat() + "Z",
        "git_commit": git_commit(),
        "model": {"id": model_cfg["id"], "provider": model_cfg["provider"], "params": model_cfg["params"]},
        "suite": suite,
        "tasks": [],
        "aggregates": {},
    }

    all_results: List[Dict[str, Any]] = []

    for tdir in task_dirs:
        cfg = load_task_config(tdir)
        task_id = cfg.get("id")
        if selected is not None and task_id not in selected:
            continue

        prompt_tpl = read_text(str(tdir / cfg.get("prompt")))
        cases = read_jsonl(str(tdir / cfg.get("cases")))
        if args.max_cases is not None:
            cases = cases[: args.max_cases]

        evaluate = import_evaluator(tdir)

        meta["tasks"].append({"id": task_id, "name": cfg.get("name"), "cases": len(cases)})

        for case in cases:
            case_id = case.get("case_id")
            # Prompt con variables
            user_prompt = prompt_tpl.format(**case)
            input_hash = sha256_text(user_prompt)

            t0 = time.time()
            gen = adapter.generate(system=args.system, user=user_prompt, params=model_cfg["params"])
            latency_ms = int((time.time() - t0) * 1000)

            # Evaluación
            workdir = out_dir / "artifacts" / task_id / str(case_id)
            ensure_dir(workdir)
            ev = evaluate(case, gen.text, str(workdir))

            row = {
                "suite": suite,
                "task_id": task_id,
                "case_id": case_id,
                "input_hash": input_hash,
                "prompt": user_prompt,
                "raw_output": gen.text,
                "usage": gen.usage,
                "latency_ms": gen.latency_ms if gen.latency_ms is not None else latency_ms,
                "scores": ev.get("scores", {}),
                "pass_fail": ev.get("pass_fail"),
                "notes": ev.get("notes"),
            }
            all_results.append(row)

    # Guardar artifacts
    (out_dir / "run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(str(out_dir / "results.jsonl"), all_results)

    print(f"Run guardado en: {out_dir}")
    print(f"Resultados: {len(all_results)} casos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
