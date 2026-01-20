# GenAI Model Lab

Repositorio para **probar, comparar y registrar** el desempeño de modelos de IA generativa (LLMs) a medida que vayan saliendo.

## Qué incluye (v1)
- Runner de suites y tareas con registro auditable por ejecución (runs).
- 3 tareas de ejemplo (programación, datos/SQL, tono comunicacional) con evaluadores automáticos.
- Reportes básicos (leaderboard) a partir de los runs.
- Workflows de GitHub Actions (smoke en PR y ejecución programada).

## Requisitos
- Python 3.10+

Instalación:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar un smoke test (modelo mock)
```bash
python tools/run_suite.py --model mock --suite programming_general --tasks pg_001_function_implementation --max-cases 1
```

## Ejecutar todas las suites con modelo mock
```bash
python tools/run_suite.py --model mock --suite programming_general
python tools/run_suite.py --model mock --suite data_programming
python tools/run_suite.py --model mock --suite communication_tone
```

## Probar con un proveedor real
Este repo trae adapters para **OpenAI SDK** y **LiteLLM**. Con LiteLLM puedes comparar proveedores (OpenAI, Claude, Gemini, DeepSeek) con una interfaz única.

### Opción A: LiteLLM (recomendado para comparar proveedores)
1. Instala:

```bash
pip install litellm
```

2. Configura claves en el entorno (según el proveedor):
- OpenAI: `OPENAI_API_KEY`
- Claude: `ANTHROPIC_API_KEY`
- Gemini: `GOOGLE_API_KEY` o `GEMINI_API_KEY` (según tu setup de LiteLLM)
- DeepSeek: `DEEPSEEK_API_KEY`

3. Usa los modelos ya registrados en `models/registry.yml`:

```bash
python tools/run_suite.py --model openai_gpt_4o_mini_litellm --suite programming_general
python tools/run_suite.py --model claude_sonnet_litellm --suite programming_general
python tools/run_suite.py --model gemini_pro_litellm --suite programming_general
python tools/run_suite.py --model deepseek_chat_litellm --suite programming_general
```

### Opción B: OpenAI SDK (OpenAI y endpoints compatibles, por ejemplo DeepSeek)
1. Instala:

```bash
pip install openai
```

2. Configura variables:
- OpenAI: `OPENAI_API_KEY`
- DeepSeek: `DEEPSEEK_API_KEY` 
`DEEPSEEK_BASE_URL` 

3. Ejecuta:

```bash
python tools/run_suite.py --model openai_gpt_4o_mini_strict --suite programming_general
python tools/run_suite.py --model deepseek_chat_openai_compat --suite programming_general
```

### Construir el leaderboard
Luego de correr varios modelos/suites:

```bash
python tools/aggregate.py
```

## Estructura
- `suites/`: suites y tareas. Cada tarea vive en una carpeta con `task.yml`, `prompt.md`, `cases.jsonl` y `evaluator.py`.
- `models/`: adapters y registry de modelos.
- `runs/`: salidas por ejecución (metadatos, resultados y artifacts).
- `tools/`: runner y agregadores de reportes.

## Seguridad (importante)
Algunas tareas (por ejemplo programación) ejecutan código generado por el modelo para correr tests. **No ejecutes suites de terceros sin revisar el contenido**.

## Cómo agregar una tarea nueva
Ver `docs/experiment_protocol.md` y usa como referencia una carpeta de tarea existente en `suites/*/tasks/*`.
