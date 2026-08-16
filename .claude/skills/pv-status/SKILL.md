---
name: pv-status
description: Recopila y presenta el estado actual del proyecto según el framework pv-* — totales de elementos por tipo (todo/change/fix/fast) y por estado (carpetas de {changesDir}). Devuelve el informe como respuesta de chat; no escribe ningún fichero salvo que el usuario lo pida explícitamente. Trigger: /pv-status, o cuando el usuario pide un resumen/vista general del estado del proyecto, cuántos changes/fixes hay pendientes, etc. Acepta argumentos opcionales para listados filtrados: `todo` (solo ideas de `{changesDir}/todo/`) o el nombre de cualquier otra carpeta de estado existente (p.ej. `closed`, `implemented`, `inProgress`).
argument-hint: "[todo|<estado>]"
model: claude-haiku-4-5
effort: medium
metadata:
  version: 0.9.2
  uses: []
---

# pv-status

Da una vista general del estado del proyecto dentro del framework `pv-*`, basada exclusivamente en el contenido de `{changesDir}` (sus subcarpetas de estado: `todo`, `inProgress`, `implemented`, `closed`, o cualquier otra que exista).

Esta skill es de solo lectura: no crea, mueve ni modifica ninguna carpeta o fichero de `{changesDir}`. El informe se entrega como respuesta de chat; **no se escribe en ningún fichero salvo que el usuario lo pida explícitamente** (ver paso 4).

## 0. Cargar el contexto del proyecto

Lee `.claude/pv-context.json` en la raíz del repo. Si no existe, o le falta la sección `framework`, no continúes: dile al usuario que primero debe ejecutar la skill `pv-init` para inicializar el framework, y detente ahí.

```
Este proyecto todavía no tiene el framework `pv-*` inicializado (o le falta configuración). Ejecuta primero `/pv-init` antes de volver a invocarme.
```

## 1. Detectar el modo de invocación

Antes de ejecutar ningún script, mira cómo se invocó la skill — cada modo usa un script distinto y **solo uno** se ejecuta:

- Argumento `todo` (`/pv-status todo`, o "solo las ideas de todo"/"lista los todos") → ve a **1.b**.
- Argumento con el nombre de una carpeta de estado existente en `{changesDir}` distinta de `todo` (p.ej. `/pv-status closed`, `/pv-status implemented`, `/pv-status inProgress`, o "la lista completa de lo que está en `<estado>`") → ve a **1.c**.
- Sin argumento, o cualquier otro caso (informe general) → ve a **2**.

No ejecutes `collect_status.py` directamente en ningún modo: es un módulo interno que `list_todo.py` y `render_status.py` importan y reutilizan por su cuenta, no un script pensado para invocarse desde la skill — su salida JSON no aporta nada que la skill deba mostrar o reformatear.

Los tres scripts (`list_todo.py`, `filter_status.py`, `render_status.py`) aceptan también un flag `--terminal` que cambia la salida a texto plano sin markdown, ajustado a 70 columnas. Es de uso exclusivo de `pv.py` (el menú de terminal del framework); esta skill, invocada desde el chat, **nunca** debe pasar `--terminal` — el markdown por defecto es siempre el formato correcto para una respuesta de chat.

## 1.b Modo `todo`: solo listar ideas

Ejecuta directamente [`scripts/list_todo.py`](scripts/list_todo.py) — no ejecutes `collect_status.py` para este modo, no hace falta:

```
python .claude/skills/pv-status/scripts/list_todo.py
```

El script ya aplica internamente la plantilla [`STATUS.todo.template.md`](STATUS.todo.template.md) e imprime por stdout el listado en markdown listo para mostrar (código + texto completo sin truncar de la sección `## Idea` de cada `description.md`, marcando explícitamente las ideas sin esa sección, o el mensaje de "sin ideas" si `todo/` está vacía) — no es JSON, no vuelvas a aplicar la plantilla tú ni reformatees nada.

Tu respuesta en el chat debe ser **exactamente** el stdout del script, sin añadir nada antes ni después (nada de "Aquí tienes el listado:", resúmenes, ni comentarios propios). No lo guardes en fichero salvo que el usuario lo pida (paso 4).

## 1.c Modo `<estado>`: listado filtrado de una carpeta de estado

Ejecuta directamente [`scripts/filter_status.py`](scripts/filter_status.py) con el nombre de esa carpeta como argumento — no ejecutes `collect_status.py` para este modo, no hace falta:

```
python .claude/skills/pv-status/scripts/filter_status.py <estado>
```

Si el estado indicado no existe como carpeta de `{changesDir}`, el script falla con un mensaje que lista los estados disponibles — tu respuesta debe ser exactamente ese mensaje de error, tal cual, sin improvisar una lista propia.

El script ya aplica internamente la plantilla [`STATUS.filtered.template.md`](STATUS.filtered.template.md) e imprime por stdout el informe en markdown listo para mostrar (tabla Código/Tipo/Descripción/Fecha, o el mensaje de "sin entradas" si el estado está vacío) — no es JSON, no vuelvas a aplicar la plantilla tú ni reformatees nada.

Tu respuesta en el chat debe ser **exactamente** el stdout del script, sin añadir nada antes ni después (nada de "Aquí tienes el informe:", resúmenes, ni comentarios propios). No lo guardes en fichero salvo que el usuario lo pida (paso 4).

## 2. Generar el informe

Toda la mecánica de recopilar y mapear los datos a la plantilla [`STATUS.template.md`](STATUS.template.md) (tabla de totales, las tres listas de "En progreso", cambios fast, ideas de `todo/`, avisos) la hace, de forma determinista y gratis en tokens, el script [`scripts/render_status.py`](scripts/render_status.py) — no repitas tú ese mapeo campo a campo, no redactes las listas a mano, y no ejecutes `collect_status.py` antes: `render_status.py` recopila los datos internamente por su cuenta, no depende de nada del paso 1. Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-status/scripts/render_status.py
```

El script recopila los datos de `{changesDir}` por su cuenta (misma lógica que `collect_status.py`) y aplica el mapeo completo (incluida la regla de la columna Fast solo en `implemented`/`closed`, las tres listas de "En progreso" con sus casos vacíos, y omitir por completo las secciones de "Cambios fast implementados"/"Avisos" cuando no aplican) e imprime por stdout el informe en markdown ya listo — no es JSON, no vuelvas a aplicar la plantilla tú ni reformatees nada.

Por defecto la sección **"Cambios fast implementados" se omite**, aunque existan entradas fast (el total de la columna Fast en la tabla sigue mostrándose). Solo inclúyela si el usuario la pide explícitamente en este turno (p.ej. "enséñame también los fast", "detalla los cambios fast"), añadiendo el flag `--show-fast`:

```
python .claude/skills/pv-status/scripts/render_status.py --show-fast
```

No inventes datos que no estén en la salida del script (p.ej. no le asignes un tipo a una entrada `unknown` solo por adivinarlo del nombre de la carpeta).

## 3. Presentar el informe

Tu respuesta en el chat debe ser **exactamente** el stdout del script ejecutado en el paso 2, sin añadir nada antes ni después (nada de "Aquí tienes el informe:", resúmenes, comentarios propios, ni texto adicional fuera del markdown que imprimió el script). No lo guardes en ningún fichero en este paso.

## 4. Guardar en fichero (solo si el usuario lo pide)

Si el usuario, en este mismo turno o en uno posterior, pide explícitamente que el informe se guarde (p.ej. "guárdalo", "déjalo en un fichero"), y no ha indicado ninguna ruta concreta, pregúntale dónde quiere guardarlo (p.ej. `{changesDir}/STATUS.md` u otra ruta de su elección) antes de escribir nada — no asumas una ruta por defecto.
