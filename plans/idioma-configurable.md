# Plan — Traducir el framework `pv-*` al inglés + idioma configurable

> Revisión de un análisis previo (escrito cuando el framework aún se llamaba `ms-*` y se pensaba para el repo `errantes-board-game`). El diseño de fondo se mantiene; lo que cambia en esta revisión es el inventario de ficheros/skills y la forma de `.claude/pv-context.json`, para que coincidan con el estado real de este repo (`previo`, que **es** el framework, no un consumidor de él) a fecha 2026-08-16. El propio `README.md` ya anuncia "soporte multi-idioma" como feature — este plan es lo que le da contenido.

## Contexto

Todo el framework `pv-*` (`.claude/skills/pv-*`, `.claude/pv-guide.md`, `.claude/pv-design.md`, plantillas y scripts) está escrito en español: instrucciones de cada `SKILL.md`, mensajes al usuario, plantillas de documentos y buena parte de los scripts Python (comentarios, docstrings, nombres de placeholder).

El objetivo es doble:

1. **Traducir todo el framework al inglés** como idioma base — el que usan las instrucciones internas de cada skill (el "código" que seguimos los LLMs), independientemente de con quién se esté hablando.
2. **Permitir que el usuario configure otros idiomas**, con un campo `language` embebido en distintos puntos de `framework` dentro de `.claude/pv-context.json`, de forma independiente para cuatro cosas distintas:
   - la interacción general con el usuario (`framework.interaction.language`; valor por defecto para todo lo demás si no se especifica nada más concreto),
   - los documentos de seguimiento de un change/fix en curso (`description.md`, `plan.md`, `history.md`...), vía `framework.changes.language`,
   - los documentos de una entrega ya empaquetada (`changelog.md`), vía `framework.versions.language`,
   - cada área de documentación de referencia declarada en `framework.docs.*` (`docs.functional` para features, `docs.tech` para arquitectura + biblia de estilo juntas), por separado.

Regla general: **ante cualquier duda de a qué idioma pertenece algo, se usa el idioma por defecto** (`framework.interaction.language`). Y `pv-init` debe **confirmar siempre con el usuario** la configuración de idioma durante la inicialización, no solo preguntarla si faltan pistas.

## Qué cambió desde la versión anterior de este plan (y por qué importa)

El análisis original se escribió contra una versión anterior del framework (`ms-*`) y contra la forma de configuración de otro proyecto. Desde entonces:

- **Renombrado completo `ms-*` → `pv-*`** (skills, ficheros de config, `pv-context.json`).
- **`framework.changesDir` ya no existe.** Ahora hay `framework.workFolder` (string, default `"/"`), bajo el cual las skills crean por sí mismas dos subcarpetas de nombre fijo: `{workFolder}/changes/` (con `inProgress/`, `implemented/`, `todo/`, `closed/`) y `{workFolder}/versions/`. No hay ya un objeto `changes` con una ruta configurable — sólo `workFolder`.
- **`framework.mockupsSkill` ya no existe suelto.** Ahora vive en `framework.skills.mockups`, junto a `framework.skills.diagrams` (nuevo: nombre de la skill de diagramas Mermaid intercambiable).
- **Han aparecido skills nuevas** que el inventario anterior no cubría: `pv-version` (empaqueta una entrega), `pv-internal-changelog` (redacta `changelog.md` desde `changes/closed`), `pv-internal-doc-features` (mantiene `docs.functional.featuresDocPathDir` cuando es carpeta con un fichero por feature + `INDEX.md`), `pv-internal-tech-mermaid` (genera diagramas Mermaid, sustituye a la generación de diagramas que antes vivía embebida en otras skills), `pv-internal-tech-risks` y `pv-internal-tech-security` (checklists de riesgo/seguridad devueltas como contexto estructurado, no como texto al usuario).
- **`docs.functional`/`docs.tech` ya existen en el schema actual**, tal cual los describía el plan anterior (con `featuresDocPathDir`, `architectureDocDir`, `styleBibleDocDir`), pero sin ningún campo `language` — es terreno ya preparado para añadirlo sin fricción.
- **La documentación humana del framework (`pv-guide.md`/`pv-design.md`) ya tiene su par `.en.md`** mantenido a mano (`pv-guide.en.md`, `pv-design.en.md`, ambos actualizados). Esto es una estrategia de traducción **distinta** y **complementaria** a la de este plan: son ficheros para que una persona lea en GitHub, no instrucciones de un LLM ni output generado por skills, así que puede seguir como un par estático de ficheros por idioma en vez de un `language` dinámico. Este plan no toca ese mecanismo, pero conviene dejarlo explícito para que no parezca una inconsistencia sin explicar.
- **El versionado de skills ya no parece semver independiente por skill** (el plan anterior asumía algo tipo `ms-new` en `1.11.0`, `ms-fix` en `2.1.0`...). A día de hoy **todas** las skills están sincronizadas en `metadata.version: 0.9.2`, lo que sugiere una versión compartida del framework que se sube junto en cada entrega, no un semver por skill. Este plan **no asume** cuál es la convención correcta — es una pregunta abierta a confirmar con el usuario antes de tocar ningún `metadata.version` (ver sección de riesgos).

## Principio de diseño clave (sin cambios)

**Las instrucciones que sigue el LLM (el contenido de cada `SKILL.md`, plantillas, scripts) se quedan siempre en inglés**, se configure lo que se configure en `language`. Lo único que cambia según `language` es **el idioma del texto que el LLM produce hacia fuera**: lo que le dice al usuario en el chat, y el contenido de los documentos que escribe. Separar "idioma de las instrucciones" de "idioma de la salida" es lo que hace fiable seguir instrucciones complejas en inglés (el idioma en el que estas skills están mejor probadas) mientras se conversa o se documenta en el idioma que el usuario prefiera.

## Campos `language` embebidos en `framework` de `.claude/pv-context.json`

Ningún campo nuevo a nivel raíz: cada `language` se embebe como hermano de los campos que ya existen dentro de `framework`, en el objeto al que pertenece. Todos opcionales — si ninguno existe, todo funciona en inglés (comportamiento por defecto, sin romper proyectos ya inicializados con el schema actual).

```json
"framework": {
  "workFolder": "/",
  "sourcecodeDir": "src",
  "numberWidth": 4,
  "interaction": { "language": "en" },
  "changes": { "language": "es" },
  "versions": { "language": "es" },
  "skills": {
    "mockups": "pv-internal-mockups-html",
    "diagrams": "pv-internal-tech-mermaid"
  },
  "docs": {
    "functional": { "language": "es", "featuresDocPathDir": "design/docs/features" },
    "tech": { "language": "en", "architectureDocDir": "design/docs/architecture", "styleBibleDocDir": "design/docs/style" }
  }
}
```

- **`framework.interaction.language`** (opcional, por defecto `"en"`) — idioma en el que las skills hablan con el usuario en el chat (preguntas, confirmaciones, resúmenes). Es también el **valor de respaldo** de `changes.language`, `versions.language` y de cualquier bloque de `docs.*` sin `language` propio.
- **`framework.changes.language`** (opcional, por defecto = `interaction.language`) — idioma de los documentos de un change/fix **en curso**: `description.md` (de `pv-new`/`pv-fix`, y también el de `pv-todo`), `plan.md`, `history.md`, y el texto de ejemplo dentro de las maquetas `design_*.html`/`design_*.txt`. Todos viven bajo `{workFolder}/changes/**`. **Nuevo respecto al plan anterior**: como `changesDir` ya no es una ruta configurable (es fija bajo `workFolder`), este objeto lleva únicamente `language` — no hay ruta que acompañarlo.
- **`framework.versions.language`** (opcional, por defecto = `interaction.language`) — **objeto nuevo, no existía en el plan anterior porque `pv-version`/`pv-internal-changelog` no existían.** Idioma de `changelog.md`, generado por `pv-internal-changelog` bajo `{workFolder}/versions/{XXXX}/` a partir de las entradas de `changes/closed`. Es una familia de documentos distinta de `changes.language`: describe una entrega ya cerrada desde una perspectiva funcional, no el proceso de un cambio individual en curso, y puede razonablemente querer un idioma distinto (p.ej. changelog en inglés para publicar, mientras el proceso interno de changes se documenta en español).
- **`framework.docs.functional.language`** (opcional, por defecto = `interaction.language`) — idioma de `featuresDocPathDir`.
- **`framework.docs.tech.language`** (opcional, por defecto = `interaction.language`) — idioma compartido por `architectureDocDir` y `styleBibleDocDir`. Simplificación deliberada (igual que en el plan anterior): ambos cuelgan del mismo objeto `tech` y normalmente se redactan juntos; desacoplarlos sería una extensión futura de este mismo diseño.

Sigue sin modelarse como mapa de rutas libres con "longest prefix match": cada `language` vive pegado al campo (o grupo de campos) al que ya se refiere.

### Tabla de resolución de idioma

| Contenido | Quién lo escribe | Campo que aplica | Fallback |
|---|---|---|---|
| Chat con el usuario (preguntas, confirmaciones, resúmenes) — todas las skills | todas | `framework.interaction.language` | `"en"` |
| `description.md` (change/fix, incluido `pv-todo`) | `pv-internal-workflow`, `pv-todo` | `framework.changes.language` | `interaction.language` |
| `plan.md` | `pv-how` | `framework.changes.language` | `interaction.language` |
| `history.md` | `pv-internal-workflow` | `framework.changes.language` | `interaction.language` |
| `design_navigation_*.md` | `pv-new`/`pv-fix` | `framework.changes.language` | `interaction.language` |
| Texto de ejemplo en `design_*.html`/`design_*.txt` | `pv-internal-mockups-html`/`-ascii` | `framework.changes.language` | `interaction.language` |
| Diagramas Mermaid embebidos en `description.md`/`plan.md` | `pv-internal-tech-mermaid` (idioma pasado por quien la invoca) | `framework.changes.language` | `interaction.language` |
| `changelog.md` | `pv-internal-changelog` | `framework.versions.language` | `interaction.language` |
| `docs.tech.architectureDocDir` | `pv-do` | `framework.docs.tech.language` | `interaction.language` |
| `docs.tech.styleBibleDocDir` | `pv-do` | `framework.docs.tech.language` | `interaction.language` |
| Diagramas Mermaid embebidos en docs de arquitectura | `pv-internal-tech-mermaid` (idioma pasado por `pv-do`) | `framework.docs.tech.language` | `interaction.language` |
| `docs.functional.featuresDocPathDir` (vía `pv-internal-doc-features`) | `pv-do` → `pv-internal-doc-features` | `framework.docs.functional.language` | `interaction.language` |
| Instrucciones de cada `SKILL.md`, plantillas, scripts | — | — (siempre inglés) | — |

### Casos que se quedan explícitamente en inglés (límite conocido y asumido)

- **Etiquetas de campo markdown usadas como anclas parseables** (`**Type**`, `**Name**`, `**Code**`, `**Date**`, `## Idea`, `## Notes`, `**Area**`... en `description.md`, `plan.md`, y los ficheros de `docs.functional.featuresDocPathDir`): se tratan como marcado estructural fijo, igual que ya se hace con nombres de campo JSON (regla de la sección "Alcance de la traducción"), **no como prosa traducible**. Quedan siempre en inglés, cualquiera que sea `changes.language`/`docs.functional.language`; solo el *valor* que sigue a cada etiqueta (el texto libre) sigue ese idioma. Motivo: varios scripts Python parsean estos documentos con regex ancladas al literal en español actual — `collect_status.py` (`**Tipo**`, `**Nombre**`), `filter_status.py` (`**Tipo**`, `**Fecha**`), `render_status.py` (`**Fecha**`), `list_todo.py` (`## Idea`), `rebuild-index.py` de `pv-internal-doc-features` (`**Área**`). Si esas etiquetas cambiaran con `language`, el parseo fallaría en silencio (la entrada cae a `"unknown"`/`null`, con avisos espurios en vez de un error visible) en lugar de romperse de forma ruidosa. Fijar las etiquetas evita ese riesgo sin necesitar lógica de idioma en los scripts. Ver más abajo el detalle de scripts afectados.
- **Informe de `pv-status`**: lo generan scripts Python deterministas (`collect_status.py`, `filter_status.py`, `render_status.py`) rellenando plantillas por sustitución de placeholders, sin pasar por el LLM — precisamente para que sea gratis en tokens y consistente. Sus cabeceras de tabla y texto fijo **no se traducen dinámicamente**; sería desproporcionado mantener plantillas por idioma dentro del script para un valor de idioma en texto libre. Decisión (aplicando "ante la duda, usa el de por defecto"): el contenido tabular se queda siempre en inglés, sea cual sea `interaction.language`. Solo el texto que el LLM añade alrededor (la frase de introducción antes de pegar la tabla) sigue `interaction.language`.
- **Salida estructurada de `pv-internal-tech-risks` y `pv-internal-tech-security`**: son procedimientos internos que devuelven listas factor=valor / categorías de checklist a quien las invoca (`pv-how`, `pv-internal-tech-analysis`), no texto de cara al usuario ni contenido que se escriba tal cual en un documento. Se quedan en inglés como vocabulario técnico interno del framework; es responsabilidad de la skill que consume ese resultado (`pv-how`) traducirlo si lo vuelca en `plan.md` en `changes.language`.
- **`pv-internal-tech-analysis` citando fragmentos de `docs.tech.*`**: si cita literalmente texto de la documentación técnica, lo cita en el idioma en que esté escrita realmente — no traduce lo que lee.
- **`pv-guide.md`/`pv-design.md`**: fuera del alcance de `language` dinámico — siguen como par de ficheros estáticos `.md`/`.en.md` mantenidos a mano (mecanismo ya existente, sin cambios en este plan).

## Cambios en `pv-init`

1. **`schema.json`** (`.claude/skills/pv-init/schema.json`) — añadir el campo opcional `language` (string) en:
   - `framework.interaction` (objeto nuevo, con solo `language`).
   - `framework.changes` (objeto nuevo, con solo `language` — no hay ruta que añadir, a diferencia del plan anterior).
   - `framework.versions` (objeto nuevo, con solo `language`).
   - `framework.docs.functional` (añadir `language` junto a `featuresDocPathDir`, ya existente).
   - `framework.docs.tech` (añadir `language` junto a `architectureDocDir`/`styleBibleDocDir`, ya existentes).

   Todos con `additionalProperties: false` en sus objetos contenedores, siguiendo el patrón ya usado en el resto de `framework`. Añadir también el campo opcional `framework._comments` (objeto `clave → string`), mismo patrón que `skillModels._instructions`: metadata informativa para quien edite el JSON a mano, ignorada en tiempo de ejecución. Añadir un ejemplo completo con los cinco campos `language` (`interaction`, `changes`, `versions`, `docs.functional`, `docs.tech`) y con `_comments` al array `examples` del schema.

2. **`scripts/check-context.py`** (`.claude/skills/pv-init/scripts/check-context.py`) — el script imprime hoy `{"exists","hasFramework","missingRequired","complete"}` y `missingRequired` siempre viene vacío porque `framework` no tiene campos `required`. Añadir al JSON de salida un campo nuevo `hasLanguage` (booleano: `true` si `framework.interaction.language` existe en el fichero, sin importar qué contenga). Es el único campo cuya ausencia dispara la pregunta incondicional de `pv-init`; `changes.language`/`versions.language`/`docs.*.language` son afinamientos opcionales sobre ese valor por defecto y se preguntan en la misma ronda pero no condicionan `hasLanguage`.

3. **`SKILL.md`** (`.claude/skills/pv-init/SKILL.md`) — nuevo paso, en el mismo punto donde hoy se pregunta por `workFolder`/`sourcecodeDir`/`docs.*` (paso 3, "preguntar lo que falte"):
   - **Si es una inicialización desde cero** (no existe `.claude/pv-context.json`, o el usuario confirmó reinicializar): preguntar **siempre** por la configuración de idioma, sin condicionarlo a pistas detectadas — igual que ya se hace hoy con `workFolder`. Usar `AskUserQuestion`:
     1. Idioma de interacción (`framework.interaction.language`) — proponer inglés por defecto, dejando claro que puede ser cualquier otro (texto libre, o código ISO 639-1 tipo `es`, `fr`).
     2. Idioma de los documentos de change/fix en curso (`framework.changes.language`) — proponer el mismo que interacción por defecto, preguntando solo si quiere uno distinto.
     3. Idioma del changelog de entregas (`framework.versions.language`) — mismo patrón, proponer el de interacción por defecto.
     4. Idioma de cada área de `framework.docs` ya resuelta en este mismo paso (`docs.functional.language`, `docs.tech.language`, las que apliquen según lo que el usuario haya configurado) — mismo patrón.
   - Al escribir/actualizar `language`, `pv-init` también escribe (o completa) `framework._comments` con la explicación de cada campo `language` configurado.
   - **Si es una actualización parcial** (`hasLanguage` es `false` pero el resto de `framework` ya existe, siguiendo la rama que hoy ya contempla el SKILL.md para "opcionales sin configurar"): incluir esta misma pregunta en la misma ronda de preguntas, no crear una ronda aparte. Si `hasLanguage` es `true`, no volver a preguntar.

4. **Paso de confirmación final** — el resumen debe incluir también lo que ha quedado configurado en `interaction.language`/`changes.language`/`versions.language`/`docs.*.language`.

## Cambios en cada skill: aplicar la configuración de idioma

Cada skill invocable (más las internas que hablan directamente con el usuario o escriben documentos) añade, en su paso de carga de contexto, un párrafo corto y estándar:

> **Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. [Frase específica de la skill: qué campo `language` aplica al documento que escribe, con su fallback — ver tabla de resolución arriba.] If `language` is not configured anywhere, everything is English.

Aplicación concreta por skill (inventario actual, `.claude/skills/`):

- **`pv-init`** — caso especial: al preguntar por primera vez, todavía no hay `interaction.language`. Usa inglés hasta que el usuario fije uno; en invocaciones posteriores sobre un proyecto ya inicializado, usa `interaction.language` si existe.
- **`pv-new`, `pv-fix`** — chat en `interaction.language`; `description.md` (vía `pv-internal-workflow`), `design_navigation_*.md` y el texto de ejemplo de `design_*.*` en `changes.language`.
- **`pv-how`** — chat en `interaction.language`; `plan.md` en `changes.language`. Al pedir diagramas a `pv-internal-tech-mermaid` para `plan.md`, le pasa `changes.language` como idioma objetivo.
- **`pv-do`** — chat en `interaction.language`; al actualizar `docs.functional.featuresDocPathDir` (vía `pv-internal-doc-features`), usa `docs.functional.language`; al actualizar `docs.tech.architectureDocDir`/`styleBibleDocDir`, usa `docs.tech.language` (fallback `interaction.language` en ambos casos) — **no** `changes.language`, aunque la fuente (`plan.md`) esté en otro idioma: es responsabilidad de `pv-do` traducir el contenido al escribirlo en el documento de referencia final.
- **`pv-version`** — chat en `interaction.language`; copia de documentación técnica y generación del entregable son operaciones de copia/build, no generan prosa nueva (no aplica `language`); encadena `pv-internal-changelog` para `changelog.md`.
- **`pv-internal-workflow`** — chat (mensajes de guardarraíl) en `interaction.language`; `description.md` (acción `create`) y `history.md` en `changes.language`.
- **`pv-internal-changelog`** — chat (confirmación antes de borrar carpetas de `changes/closed`) en `interaction.language`; `changelog.md` en `versions.language`.
- **`pv-internal-doc-features`** — no habla con el usuario; el contenido que redacta en cada fichero de feature y en `INDEX.md` sigue `docs.functional.language` (se lo indica quien la invoca, `pv-do`).
- **`pv-internal-tech-analysis`** — no escribe nada ni habla directamente con el usuario; si cita literalmente fragmentos de `docs.tech.*`, los cita en el idioma real en que estén escritos (no traduce lo que lee).
- **`pv-internal-tech-mermaid`** — no habla con el usuario; recibe el idioma objetivo como parte de la entrada de quien la invoca (no lee `pv-context.json` por sí misma, ya que no sabe en qué documento final se va a insertar cada diagrama).
- **`pv-internal-tech-risks`, `pv-internal-tech-security`** — salida estructurada interna, se queda en inglés (ver límite conocido arriba); no hablan con el usuario.
- **`pv-internal-mockups-html`/`-ascii`** — no hablan con el usuario; el texto de ejemplo dentro de `design_*.html`/`.txt` sigue `changes.language` (se lo indica quien invoca, o lo resuelve leyendo `.claude/pv-context.json` ella misma).
- **`pv-status`** — chat (frase que envuelve el informe) en `interaction.language`; el informe en sí se queda en inglés según el límite documentado — dejarlo explícito en el propio `SKILL.md` para que no se intente "arreglar" sin revisar antes esta decisión.
- **`pv-todo`** — chat en `interaction.language`; su `description.md` en `changes.language` (misma familia que `pv-new`/`pv-fix`, aunque viva en `todo/` en vez de `inProgress/`).

## Alcance de la traducción al inglés (inventario actualizado)

### Skills — `SKILL.md` y ficheros de soporte

- `pv-init/SKILL.md`, `schema.json`
- `pv-new/SKILL.md`, `extend-entry.md`, `todo-mode.md`
- `pv-fix/SKILL.md`
- `pv-how/SKILL.md`, `PLAN.template.md`
- `pv-do/SKILL.md`, `FEATURES.template.md`
- `pv-status/SKILL.md`, `STATUS.template.md`, `STATUS.filtered.template.md`, `STATUS.todo.template.md`
- `pv-todo/SKILL.md`, `description.template.md`
- `pv-version/SKILL.md`, `how-to-compile-version.template.md`, `version-flow-diagram.template.md`
- `pv-internal-workflow/SKILL.md`, `description.template.md`, `history.template.md`
- `pv-internal-changelog/SKILL.md`, `changelog.template.md`
- `pv-internal-doc-features/SKILL.md`, `FEATURE.template.md`
- `pv-internal-tech-analysis/SKILL.md`
- `pv-internal-tech-mermaid/SKILL.md`
- `pv-internal-tech-risks/SKILL.md`
- `pv-internal-tech-security/SKILL.md`
- `pv-internal-mockups-html/SKILL.md`
- `pv-internal-mockups-ascii/SKILL.md`

Reglas de traducción (sin cambios respecto al plan anterior, salvo la nueva viñeta sobre etiquetas de campo):
- Se traduce toda la prosa, incluido frontmatter `description`/`argument-hint` — `description` es lo que el harness usa para el trigger de la skill, debe quedar en inglés e igual de específico que hoy.
- **No se traducen**: nombres de skill (`pv-new`, `pv-how`...), nombres de campo JSON, rutas de fichero, código/comandos.
- **Tampoco se traducen dinámicamente las etiquetas de campo markdown de las templates que actúan como anclas parseables** (`**Type**`, `**Name**`, `**Code**`, `**Date**`, `## Idea`, `## Notes`, `**Area**`...): se traducen una vez al inglés como parte de esta migración (igual que el resto de la template) y a partir de ahí quedan fijas, cualquiera que sea `changes.language`/`docs.functional.language` — ver caso explícito más abajo. Solo el valor que acompaña a cada etiqueta sigue el idioma configurado.
- Los bloques de mensaje literal al usuario se traducen al inglés como texto base, pero marcados como el mensaje a adaptar según `interaction.language` en tiempo de ejecución, no como texto fijo.

### Documentación del framework

- `.claude/pv-guide.md`/`.claude/pv-guide.en.md`, `.claude/pv-design.md`/`.claude/pv-design.en.md` — **ya bilingües** (par de ficheros mantenido a mano, mecanismo existente y fuera de alcance de este plan). Sí falta: añadir a `pv-guide.md`/`pv-guide.en.md` la sección nueva explicando `language` (mismo hueco donde hoy se explica `skillModels`), en ambos idiomas.

### Scripts Python (docstrings, comentarios, mensajes de error/consola → inglés)

- `pv-init/scripts/check-context.py`, `sync-skill-models.py`, `assets/pv.py` (**hallazgo durante la implementación**, no estaba en el inventario original: es el lanzador de terminal que `pv-init` copia a la raíz del repo, con texto de UI en español — incluye su propio `NOMBRE_RE` que también había que actualizar a `**Name**` para seguir el rename de etiquetas de campo)
- `pv-how/scripts/get-max-change-codes.py`
- `pv-do/` — sin scripts propios
- `pv-status/scripts/collect_status.py`, `filter_status.py`, `render_status.py`, `list_todo.py`, `terminal_output.py`
- `pv-todo/scripts/new-todo-code.py`
- `pv-version/scripts/copy-build-artifacts.py`, `copy-docs.py`, `init-version-folder.py`
- `pv-internal-workflow/scripts/move-change.py`, `next-change-number.py`
- `pv-internal-changelog/scripts/delete-closed-entries.py`, `find-previous-version.py`, `list-closed-entries.py`
- `pv-internal-doc-features/scripts/_slug.py`, `migrate-legacy-features-doc.py`, `next-feature-number.py`, `rebuild-index.py`, `slugify.py`

Caso especial `pv-status` (igual que en el plan anterior, revisar si sigue aplicando tal cual): los placeholders/claves en español (`código`, `nombre`, `fecha`, `tipo`, `descripción`, `estado`, `filas...`) se renombran 1:1 al inglés en placeholders, `.format(...)` y claves de JSON emitido — sin ambigüedad de diseño porque el output se queda en inglés siempre (ver límite conocido). Revisar también `list_todo.py` y `terminal_output.py`, que no existían en el inventario anterior.

**Scripts con dependencia real de idioma, no solo cosmética (comentarios/docstrings)** — parsean con regex las etiquetas de campo de documentos que las templates generan, así que dependen de que esas etiquetas queden fijas en inglés (ver caso explícito en la sección de resolución de idioma más arriba):
- `pv-status/scripts/collect_status.py` — `TIPO_RE`/`NOMBRE_RE` sobre `**Tipo**`/`**Nombre**` de `description.md`; `IDEA_FULL_RE`/`NOTAS_FULL_RE` sobre `## Idea`/`## Notas` (formato `pv-todo`).
- `pv-status/scripts/filter_status.py` — mismo parseo de `**Tipo**`/`**Fecha**`.
- `pv-status/scripts/render_status.py` — `FECHA_RE` sobre `**Fecha**` (usado por `extract_fecha` para fast entries).
- `pv-status/scripts/list_todo.py` — busca literalmente la sección `'## Idea'`.
- `pv-internal-doc-features/scripts/rebuild-index.py` — `**Área**\*\*` para agrupar `INDEX.md`.

Al traducir estas etiquetas en las templates (`description.template.md`, `description.template.md` de `pv-todo`, `FEATURE.template.md`) hay que actualizar estos regex al literal en inglés (`**Type**`, `**Name**`, `## Idea`, `## Notes`, `**Area**`...) y dejarlos así de forma fija — no parametrizarlos por `language`, ya que las propias etiquetas no varían con `language` (ver arriba).

### Explícitamente fuera de alcance

- `.claude/improvement/**` si existe — notas de auditoría histórica del propio framework.
- Planes históricos ya guardados en `plans/`.
- Todo lo que no esté bajo `.claude/` (código de la app que uses para probar el framework, `README.md`/`README.en.md` — éstos últimos, igual que `pv-guide`/`pv-design`, siguen su propio mecanismo de par de ficheros, no `language` dinámico).

## Ficheros nuevos

Ninguno estructural — traducción + extensión de schema + paso nuevo en `pv-init`, no una skill nueva.

## Migración y retrocompatibilidad

- Todos los campos `language` son opcionales a nivel de schema: cualquier `.claude/pv-context.json` existente sigue siendo válido sin cambios — todo funciona en inglés por defecto.
- No hay migración destructiva: la próxima vez que se invoque `pv-init` sobre un proyecto sin `language`, el nuevo `hasLanguage` de `check-context.py` lo detecta y lo pregunta una vez, sin tocar el resto de configuración (merge).
- Los proyectos que no vuelvan a invocar `pv-init` siguen operando en inglés indefinidamente — comportamiento correcto y explícito, no un bug.

## Aplicar esto al `pv-context.json` de este propio repo

Este repo (`previo`) ya tiene `.claude/pv-context.json` sin campos `language`. Como parte de la implementación:

1. Añadir los campos `language` (`interaction`, `changes`, `versions`, `docs.functional`, `docs.tech` — para las áreas que ya estén configuradas: hoy falta `docs.tech.styleBibleDocDir`, revisar si sigue sin configurarse). **Decidido (confirmado con el usuario el 2026-08-16, no hace falta repreguntar al implementar):** los cinco campos en español (`"es"`), consistente con el histórico de este proyecto.
2. No hace falta retraducir `changes/`/`versions/` ya existentes — el idioma configurado aplica hacia adelante.

## Plan de verificación

- **Schema**: `python -c "import json; json.load(open('.claude/skills/pv-init/schema.json'))"` no falla tras el cambio; validar a mano los ejemplos nuevos (incluido `_comments`) contra la forma añadida.
- **`check-context.py`**: ejecutar contra el `pv-context.json` actual (sin `language`) y comprobar `hasLanguage: false`; añadir `framework.interaction.language` de prueba y comprobar `hasLanguage: true`.
- **`pv-init` (flujo completo)**: invocar sobre un repo de prueba sin `.claude/pv-context.json` y comprobar que la pregunta de idioma aparece siempre, con las cuatro sub-preguntas, que el fichero resultante tiene la forma esperada y que `framework._comments` queda escrito.
- **`pv-init` (flujo parcial)**: sobre un `pv-context.json` ya completo salvo `language`, comprobar que solo pregunta por idioma.
- **Ciclo completo con idioma no-inglés**: en un repo de prueba con `interaction.language="es"` y `changes.language="en"`, invocar `/pv-new` y comprobar que las preguntas/confirmaciones salen en español pero `description.md` en inglés.
- **`pv-version`/`pv-internal-changelog` con `versions.language` distinto de `changes.language`**: comprobar que `changelog.md` sale en el idioma de `versions`, no en el de `changes`, aunque las entradas de origen en `changes/closed` estén en otro idioma.
- **`pv-status` con `interaction.language` no inglés**: comprobar que la tabla sigue en inglés y que la frase introductoria del LLM sí sale en el idioma configurado.
- **Scripts de `pv-status` tras el rename de placeholders**: ejecutar `render_status.py`/`filter_status.py` sobre `changes/` real de este repo y comparar mismos totales, solo con cabeceras/placeholders en inglés.
- **Parseo de scripts con `changes.language`/`docs.functional.language` no inglés**: crear una entrada de prueba con `description.md` redactado con `changes.language="es"` (o cualquier otro no-inglés) pero con las etiquetas de campo fijas en inglés (`**Type**`, `**Name**`...); ejecutar `collect_status.py`/`filter_status.py`/`list_todo.py` y comprobar que `type`/`name`/`idea` se extraen correctamente (no `"unknown"`/`null`, ni avisos espurios de "no se pudo determinar Tipo"). Repetir con un fichero de feature en `docs.functional.featuresDocPathDir` y `rebuild-index.py`, comprobando que agrupa por el área real y no bajo "Sin área"/"No area".
- **Regresión general**: recorrer `pv-new → pv-how → pv-do → pv-version` completo en un repo de prueba sin tocar `language` (caso "legacy"), y comprobar que todo el texto generado sigue en inglés de punta a punta.

## Riesgos y preguntas abiertas

- **Tamaño**: sigue siendo un cambio grande (17 skills, sus scripts y plantillas, más el diseño de idioma). El plan anterior sugería trocearlo en varias entradas `pv-new`/`pv-fix` reales; **decidido (2026-08-16): se implementa por edición directa de fichero, tratando este plan.md como spec ya cerrada**, sin pasar por el ciclo `pv-new`/`pv-how`/`pv-do` — más rápido, a cambio de no dejar rastro en `changes/` ni pasar por la revisión de `pv-how`.
- **Convención de `metadata.version`**: el plan anterior asumía semver independiente por skill (`ms-new` en `1.11.0`, etc.). Hoy **todas** las skills están en `0.9.2` de forma sincronizada, lo que sugiere una versión de framework compartida en vez de por skill. **Decidido (2026-08-16): no tocar `metadata.version` en ningún `SKILL.md` como parte de esta traducción.** Si en el futuro aparece un mecanismo de bump global, se aplicará aparte.
- **`design_*.html`/`.txt` en `changes.language`**: si el idioma de interacción/changes difiere del idioma real de la UI del proyecto (que no tiene por qué coincidir con ninguno), el texto de ejemplo de las maquetas podría no reflejar el idioma real de la app. No hay campo hoy para "idioma de la UI del proyecto"; sería una extensión futura fuera de alcance.
- **Traducción de `plan.md` → `docs.tech.*` cuando `changes.language` ≠ `docs.tech.language`**: `pv-do` tiene que traducir contenido, no solo copiarlo — señalarlo explícitamente en `pv-do/SKILL.md`.
- **Granularidad de `docs.tech.language`**: comparte idioma entre `architectureDocDir` y `styleBibleDocDir`. Alternativa descartada por ahora (un `language` por campo de ruta individual) — revisar si algún caso real lo necesita antes de implementarlo.
- **`pv-internal-tech-mermaid` sin acceso directo a `pv-context.json`**: al recibir el idioma como parámetro de entrada en vez de resolverlo ella misma, cada skill que la invoca (`pv-internal-workflow`, `pv-new`, `pv-fix`, `pv-how`, `pv-do`) tiene que calcular primero el `language` correcto según en qué documento va a insertar el diagrama, y pasárselo explícitamente — confirmar que esto queda claro en su contrato de entrada/salida documentado en `pv-internal-tech-mermaid/SKILL.md`.
