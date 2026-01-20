# Model registry

El archivo `models/registry.yml` define:
- `models`: lista de modelos (id, provider, parámetros).
- `presets`: parámetros reutilizables.

Recomendación: crea ids estables (por ejemplo `openai_gpt_xxx_strict`) y versiona cambios.

## Comparaciones por proveedor (OpenAI, Gemini, Claude, DeepSeek)

Este repo soporta dos rutas:

1) **LiteLLM (recomendado para comparar proveedores con una sola interfaz)**
   - Provider en el registry: `litellm`
   - Requiere: `pip install litellm`
   - Model strings típicos (ejemplos):
     - OpenAI: `openai/gpt-4o-mini`
     - Claude (Anthropic): `anthropic/claude-3-5-sonnet`
     - Gemini (Google): `gemini/gemini-1.5-pro`
     - DeepSeek: `deepseek/deepseek-chat`

2) **OpenAI SDK (para OpenAI y endpoints compatibles con la API de OpenAI, por ejemplo DeepSeek)**
   - Provider en el registry: `openai`
   - Requiere: `pip install openai`
   - Soporta seleccionar credenciales por modelo con:
     - `api_key_env` (por defecto `OPENAI_API_KEY`)
     - `base_url_env` (por defecto `OPENAI_BASE_URL`, opcional)

### Variables de entorno típicas

- OpenAI:
  - `OPENAI_API_KEY`
  - (opcional) `OPENAI_BASE_URL`

- Claude (Anthropic):
  - `ANTHROPIC_API_KEY`

- Gemini (Google):
  - `GOOGLE_API_KEY` o `GEMINI_API_KEY` (depende de cómo tengas configurado LiteLLM)

- DeepSeek (OpenAI-compatible):
  - `DEEPSEEK_API_KEY`
  - `DEEPSEEK_BASE_URL` (consulta documentación oficial para la URL exacta)

### Ejemplo de ejecución para comparar modelos

Ejecuta la misma suite con varios modelos (cada comando produce un run en `runs/`):

```bash
python tools/run_suite.py --model openai_gpt_4o_mini_strict --suite programming_general
python tools/run_suite.py --model claude_sonnet_litellm --suite programming_general
python tools/run_suite.py --model gemini_pro_litellm --suite programming_general
python tools/run_suite.py --model deepseek_chat_openai_compat --suite programming_general
```

Luego agrega resultados:

```bash
python tools/aggregate.py
```
