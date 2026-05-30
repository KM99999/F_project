# Convenciones del proyecto

> Referencia transversal. Fuente: §10 del documento original.

## Idioma
- Código (variables, funciones, comentarios técnicos): **inglés**.
- Strings de UI, nombres de campos de DB, estados, mensajes al cliente:
  **español**.
- Documentación funcional y comunicación con el cliente: **español**.

## Naming de estados
Siempre snake_case y en español: `unico`, `posible_duplicado`,
`duplicado_confirmado`.

## Prompts a Claude (lineamientos)
- Siempre pedir **JSON estructurado** con esquema fijo.
- Devolver `null` para campos no encontrados. **Nunca inventar.**
- Incluir 1-2 ejemplos few-shot.
- Para manuscritos, pedir confianza por campo (`alta`, `media`, `baja`).
- Modelo: `claude-3-5-sonnet` (mantener el mismo modelo entre ejecuciones para
  consistencia).

## Estructura de carpetas
Ver [stack-tecnologico](stack-tecnologico.md#estructura-sugerida-del-proyecto-10).
