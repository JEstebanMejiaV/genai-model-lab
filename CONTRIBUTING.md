# Contribuir

## Convenciones
- Cada tarea debe incluir: `task.yml`, `prompt.md`, `cases.jsonl`, `evaluator.py`.
- Si cambias criterios de evaluación, considera versionar la tarea (por ejemplo `*_v2`).

## Checklist para PR
- La tarea corre con `--model mock` (o provee un mock route).
- El evaluador es determinista.
- El prompt define claramente el formato de salida.
