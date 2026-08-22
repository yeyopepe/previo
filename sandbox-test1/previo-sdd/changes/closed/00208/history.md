# Prompt history — 00208

Historical information about the analysis process, not current information. Records, verbatim and without rephrasing, the successive prompts with which the user raised and expanded this entry — they can be incomplete or contradictory with each other, since they reflect how the request evolved session by session, not the final result (that lives in `description.md`).

**Exclusive use of `pv-new` and `pv-fix`.** No other skill in the framework (`pv-how`, `pv-do`, `pv-status`, etc.) should read this file or take it into account: the source of truth for what's being asked is always `description.md`.

## 2026-08-14 — initial session

en las propiedades de todos elementos, pestaña general, hay que crear una nueva sección llamada "Ayuda jugador" y meter ahí dentro el check "mostrar tooltip" y un cuadro de texto llamado "Tooltip".
Esta sección "Ayudar jugador" debe estar debajo de la sección General.
El comportamiento es el siguiente:
- Si está marcado "mostrar tooltip" y hay un texto en "tooltip", se usa ese texto para mostrar al usuario.
- Si está marcado "mostrar tooltip" y no hay un texto en "tooltip", se usa el id para mostrar al usuario (comportamiento actual)

## 2026-08-14 — session 2

Respuesta a la lista de dudas de alcance planteada por `ms-new`:

1. "Multilinea y soporte para html básico" (respecto al campo "Tooltip", en vez del `<input>` de una línea propuesto).
8. "Los mazos deben tener el mismo comportamiento, solo que el valor por defecto de su tooltip es 'Pulsa para sacar la primera carta' y el check se marca por defecto al crear nuevos mazos." (en vez de dejar "Mazo" fuera de alcance, como se había propuesto).

Pregunta de aclaración: "¿Un mazo ya existente (guardado antes de este cambio, sin los campos nuevos) debe seguir mostrando su tooltip por defecto tras el cambio, o se aplica la regla general (ausencia = desmarcado, deja de mostrarlo)?"
Respuesta: "Regla general, sin excepción".
