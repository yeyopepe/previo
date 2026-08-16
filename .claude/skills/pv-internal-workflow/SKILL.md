---
name: pv-internal-workflow
description: Proceso compartido, agnóstico al proyecto, con dos acciones internas del framework pv-*: (1) crear una entrada nueva en {changesDir}/inProgress documentando la intención de un fix o change, y (2) mover una entrada existente entre los subestados del flujo (inProgress/implemented) cuando otra skill del framework produce esa transición. Uso interno de las skills pv-new, pv-fix y pv-do.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.1
  uses: []
---

# pv-internal-workflow

Proceso genérico y único punto donde el framework `pv-*` sabe crear y mover las carpetas de `{changesDir}`. Solo lo invocan otras skills del framework — no está pensado para invocación directa por el usuario.

Tiene dos acciones independientes, cada una invocada con un parámetro `action`:

- **`action=create`** — la invocan `pv-new` y `pv-fix`, con `type` (`change`/`fix`/`fast`), la descripción de lo que se pide y el prompt original del usuario tal cual (`promptOriginal`). Dimensiona el alcance funcional y crea la entrada en `{changesDir}/inProgress/`, con `description.md` (información vigente) y `history.md` (historial de prompts, ver más abajo) como ficheros separados. Para `type=fast` (atajo de `pv-fix` para cambios triviales), quien invoca típicamente encadena a continuación `action=move` hacia `implemented` en la misma invocación, sin pasar por `plan.md`.
- **`action=move`** — la invoca `pv-do`, con `xxxx`, `from` y `to` (nombres de subcarpeta de `{changesDir}`: `inProgress` o `implemented`). Mueve la carpeta `{xxxx}` entre esos subestados.

Ninguna de las dos acciones implementa ni analiza técnicamente nada, ni decide **si** debe producirse la transición o confirmación con el usuario — eso ya lo ha resuelto la skill llamante antes de invocar `pv-internal-workflow`. Esta skill solo ejecuta la mecánica de fichero (numerar+crear, o mover) de forma consistente en un único sitio.

## Guardarraíl de invocación — leer antes que nada

Esta skill **no se ejecuta si se ha invocado directamente** (p.ej. el usuario ha escrito `/pv-internal-workflow`, o ha pedido "ejecuta/invoca pv-internal-workflow" en texto plano). Solo debe ejecutarse cuando el propio contenido de `pv-new`, `pv-fix` o `pv-do` te ha instruido a invocarla como parte de su proceso, con la `action` y los parámetros correspondientes ya resueltos por esa skill.

Si te han invocado sin ese contexto (el usuario ha tecleado el comando directamente, o no venías de ninguna de esas tres skills), **detente aquí** y dile al usuario que `pv-internal-workflow` es de uso interno del framework: para documentar o implementar un cambio/fix debe usar la skill correspondiente. No hagas nada más en ese caso.

```
`/pv-internal-workflow` es de uso interno del framework `pv-*` y no se invoca directamente. Para documentar un cambio/fix usa `pv-new`/`pv-fix`, y para implementarlo `/pv-how`/`/pv-do`.
```

## 0. Cargar el contexto del proyecto

Lee `.claude/pv-context.json` en la raíz del repo. Si no existe, o le falta la sección `framework` (o campos suyos que esta acción necesita), no continúes: dile al usuario que primero debe ejecutar la skill `pv-init` para inicializar/completar el framework en este proyecto, y detente ahí — no reimplementes el bootstrap aquí. El esquema completo está en [`../pv-init/schema.json`](../pv-init/schema.json) (léelo primero si no lo has hecho ya en esta sesión, para saber qué campos comprobar).

A partir de aquí, `changesDir` es notación abreviada para `{workFolder}/changes` (subcarpeta de nombre fijo dentro de `framework.workFolder`, que por defecto es `"/"`, la raíz del repo — no un campo propio en `pv-context.json`), y `numberWidth` se refiere al valor de `framework` en ese fichero.

Continúa con la sección de abajo que corresponda a la `action` recibida.

**Formato de la documentación:** al redactar `description.md` (acción `create`), si quien invoca te ha pasado uno o varios diagramas Mermaid ya generados (obtenidos de la skill configurada en `framework.skills.diagrams`, ver `pv-new`/`pv-fix`), insértalos junto con las notas imprescindibles en el punto que corresponda, en vez de repetir en prosa lo que el diagrama ya deja claro. Esta skill no genera diagramas por sí misma ni decide si hacen falta — eso ya lo resolvió quien invoca antes de llamarte.

## Acción `create`

### create.1 Calcular el código de cambio `xxxx`

Cada cambio/fix vive en una subcarpeta numerada bajo alguno de los subárboles de `{changesDir}` (`inProgress/`, `implemented/`, o cualquier otro que exista): un mismo `xxxx` no puede repetirse en ninguno de ellos. La excepción es `{changesDir}/todo/`, que usa la skill `pv-todo` para ideas sueltas ajenas a este flujo: sus carpetas nunca cuentan aquí, ni aunque tuvieran nombre numérico. Para calcularlo sin errores, ejecuta el script [`scripts/next-change-number.py`](scripts/next-change-number.py) (requiere Python 3) desde la raíz del repo:

```
python .claude/skills/pv-internal-workflow/scripts/next-change-number.py
```

El script lee `workFolder` y `numberWidth` de `.claude/pv-context.json`, recorre **todas** las subcarpetas de `{changesDir}` (no solo `inProgress`/`implemented`, pero siempre ignorando `todo/`) buscando nombres puramente numéricos, y devuelve por stdout el siguiente `xxxx` ya formateado con `numberWidth` dígitos y ceros a la izquierda (p.ej. `0002`, o `1` si no hubiera ninguna carpeta numerada todavía). Usa ese valor tal cual como `xxxx` — no lo recalcules a mano ni mires solo `inProgress`/`implemented`.

### create.2 Generar el documento de intención del cambio/fix

Si hay dudas relevantes sobre el alcance de lo que se pide que no se puedan resolver con lo que ya sabes, pregúntalas antes de escribir el documento — no hace falta que sean dudas técnicas de implementación (eso lo resuelve `pv-how` más adelante), solo las de alcance funcional. Guarda esas preguntas junto con las respuestas del usuario: van incluidas en el documento (ver más abajo).

Crea (creando `{changesDir}/inProgress/` si no existe) dos ficheros separados:

```
{changesDir}/inProgress/{xxxx}/description.md
{changesDir}/inProgress/{xxxx}/history.md
```

**`description.md`** sigue exactamente la plantilla [`description.template.md`](description.template.md) de esta misma carpeta, con estas reglas por sección:

- **Nombre** — nombre corto y descriptivo del cambio/fix.
- **Código** — el `xxxx` calculado en el paso anterior.
- **Tipo** — `fix`, `change` o `fast`, según corresponda.
- **Fecha creación** — la fecha actual (formato `YYYY-MM-DD`) en el momento de crear este `description.md`.
- **Descripción completa** — resumen funcional de lo que se ha analizado que pide, entendible por cualquier persona no técnica, sin entrar en solución técnica ni mencionar ficheros, funciones, clases o estructuras de datos:
  - Para un `fix`: qué comportamiento está roto, cómo reproducirlo o identificarlo, y qué se espera que pase en su lugar.
  - Para un `change`: qué se pide añadir o modificar, por qué, y cómo debería comportarse el resultado.
  - Incluye aquí también, si las ha habido, las preguntas de alcance que se le han hecho al usuario junto con sus respuestas.
- **Apuntes técnicos** — cualquier detalle técnico visto durante el análisis (ficheros, funciones, clases, patrones ya existentes en el código relevantes para esta entrada, restricciones técnicas detectadas) que convenga dejar anotado para cuando `pv-how` diseñe la solución. Sección opcional: si el análisis funcional no ha tocado código ni ha encontrado nada técnico relevante, omítela por completo en vez de dejarla vacía.

Esta separación es estricta: cualquier mención a ficheros, funciones, clases CSS u otros detalles de implementación va siempre en **Apuntes técnicos**, nunca en **Descripción completa**, aunque haya surgido de forma natural durante el análisis. El análisis técnico en profundidad y la solución en sí los sigue haciendo `plan.md`, que genera `pv-how`.

**`history.md`** sigue exactamente la plantilla [`history.template.md`](history.template.md): un único encabezado `## {fecha de hoy} — sesión inicial` seguido del `promptOriginal` recibido, tal cual, sin reformular. Es información histórica, de uso exclusivo de `pv-new`/`pv-fix` (ver la propia plantilla) — nunca mezcles su contenido dentro de `description.md`.

### create.3 Confirmar a quien invoca

Indica los ficheros creados (`{changesDir}/inProgress/{xxxx}/description.md` y `.../history.md`) y el `xxxx` resuelto, para que la skill llamante (`pv-new`/`pv-fix`) continúe su propio proceso.

## Acción `move`

Recibida con `xxxx`, `from` y `to` ya resueltos por quien invoca (`pv-do`: `inProgress`→`implemented`).

La mecánica de fichero (comprobar origen, crear destino si falta, mover) la hace de forma determinista y gratis en tokens el script [`scripts/move-change.py`](scripts/move-change.py) (Python estándar, sin dependencias externas) — no la reimplementes a mano. Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-internal-workflow/scripts/move-change.py --xxxx <xxxx> --from <from> --to <to>
```

- Si `{changesDir}/{from}/{xxxx}/` no existe, o ya hay algo en `{changesDir}/{to}/{xxxx}/`, el script termina con error y no mueve nada — es un error de quien invoca (esa skill ya debería haber identificado y verificado la carpeta antes de llamar a `pv-internal-workflow`). Repórtaselo a quien invoca tal cual, sin improvisar una solución.
- Si va bien, el script imprime en stdout la ruta destino relativa a la raíz del repo (p.ej. `changes/implemented/0002`).

Confirma a quien invoca esa ruta destino, para que la skill llamante continúe su propio proceso (mensaje al usuario, pasos siguientes como generar versión o actualizar el grafo, etc. — eso lo gestiona ella, no `pv-internal-workflow`).
