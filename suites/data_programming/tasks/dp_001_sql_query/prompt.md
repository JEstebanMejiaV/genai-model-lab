Eres un asistente experto en SQL.

## Contexto
Vas a escribir UNA consulta SQL para SQLite.

Tabla: `calls`
Columnas:
- `call_date` (TEXT, formato YYYY-MM-DD)
- `program` (TEXT)
- `amount` (REAL)

## Tarea
Calcula el **importe total** (`SUM(amount)`) por `program` para el año **2012**.

## Restricciones de salida
- Responde con **solo** la consulta SQL.
- Debe retornar columnas: `program`, `total_amount`
- Ordena por `program` ascendente.
