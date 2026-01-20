# Protocolo de experimentos

## Qué debe registrar cada run
- Identificador de run y fecha
- Commit (git hash)
- Modelo (provider, nombre)
- Parámetros (temperature, top_p, max_tokens)
- Suite y tareas ejecutadas
- Métricas (por tarea y agregado)

## Cómo se define una tarea
Cada tarea vive en una carpeta con:
- `task.yml`: metadatos
- `prompt.md`: prompt con placeholders (Python format)
- `cases.jsonl`: casos (variables por caso)
- `evaluator.py`: función `evaluate(case, model_output, workdir)`

## Buenas prácticas
- Mantén datasets pequeños.
- Documenta claramente el output esperado (por ejemplo "solo SQL").
- Si ejecutas código generado, hazlo en un directorio temporal y captura logs.
