---
name: pv-internal-doc-features
description: Procedimiento compartido, agnóstico al proyecto, para leer y mantener actualizada la documentación funcional de `docs.functional.featuresDocPathDir` cuando esa ruta es una carpeta (un fichero por funcionalidad, cada uno con un número identificador estable delante del título, más un `INDEX.md` generado). Ofrece dos acciones: `find` (localizar si una funcionalidad ya tiene entrada propia, antes de decidir si se crea una nueva o se edita la existente) y `upsert` (escribir el fichero final de una funcionalidad, ya redactado por quien invoca, asignando número nuevo solo si es una funcionalidad nueva, y regenerar el índice). Uso interno de la skill pv-do.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.2
  uses: []
---

# pv-internal-doc-features

Procedimiento único y compartido para organizar `docs.functional.featuresDocPathDir` como una carpeta con un fichero por funcionalidad, en vez de un único documento monolítico — pensado para que analizar o actualizar una única funcionalidad no requiera leer el listado completo. Solo lo invoca `pv-do` (quien escribe esta documentación tras implementar un cambio/fix) — no está pensado para invocación directa por el usuario.

**Esta skill no decide qué dice la documentación.** No redacta descripciones funcionales ni decide si una funcionalidad existente cambia de comportamiento — eso lo hace siempre `pv-do`, que ya conoce el cambio implementado. Esta skill solo sabe **dónde** y **cómo** debe vivir esa documentación una vez redactada: nombrar el fichero, mantener el índice consistente y devolver el fichero relevante cuando hace falta comprobar si ya existe.

## Convención de la carpeta

Dada `docs.functional.featuresDocPathDir` (p.ej. `design/docs/features/`):

- `INDEX.md` — tabla de contenidos agrupada por área funcional, con enlaces a cada fichero. **Nunca se edita a mano**: lo regenera siempre [`scripts/rebuild-index.py`](scripts/rebuild-index.py) a partir del resto de ficheros.
- Un fichero `{NNN}-{slug}.md` por funcionalidad (plano, sin subcarpetas por área; el nombre de fichero lleva el mismo número que el título, para que el listado de ficheros de la carpeta quede ordenado igual que `INDEX.md`), siguiendo [`FEATURE.template.md`](FEATURE.template.md):
  - `# {NNN} — {Nombre de la funcionalidad}` — el número identificador es estable: se asigna una vez al crear la funcionalidad (ver acción `upsert`) y no vuelve a cambiar aunque el título se edite después ni aunque otra funcionalidad se borre (tanto en el título como en el nombre de fichero). Sirve para localizarla rápido, no para ordenar nada por relevancia.
  - `**Área**: {Área funcional}`
  - Cuerpo funcional (una o más frases/párrafos).
  - Diagramas funcionales (opcional) — cero o más bloques ```mermaid```, cada uno representando un flujo/caso de uso de esta funcionalidad desde el punto de vista del usuario. Nunca diagramas técnicos (flujo interno, secuencia entre componentes): esos viven en la documentación técnica, no aquí.
  - `- **Disponible en**: ...`
  - `- **Código**: {xxxx}, {xxxx}, ...` — todos los códigos de change/fix que han creado o modificado esta entrada, no solo el último.
  - `- **Desde**: {AAAA-MM-DD}` — fecha en la que se creó esta entrada (el primer `xxxx` de **Código**). No cambia nunca tras asignarse.
  - `- **Última modificación**: {AAAA-MM-DD}` — fecha de la última vez que se editó esta entrada (hoy, cada vez que se pasa por `upsert`).
- Los enlaces cruzados entre funcionalidades usan la ruta relativa al fichero destino (`[texto](NNN-otro-slug.md)`), nunca anclas `#` — cada funcionalidad vive en su propio fichero.

## Entrada esperada de quien invoca

Quien invoca debe indicar la `action` (`find` o `upsert`) y sus parámetros propios (ver más abajo). Si `docs.functional.featuresDocPathDir` no está configurado en `.claude/pv-context.json`, dilo y detente — quien invoca decide qué hacer (normalmente, omitir el paso sin preguntar nada).

## Acción `find`

La invoca `pv-do` antes de redactar, para saber si la funcionalidad que va a documentar ya tiene una entrada propia (y así editarla in place) o es nueva.

Parámetros: una descripción breve de la funcionalidad a buscar (nombre aproximado, área, o de qué trata).

1. Si la carpeta de `featuresDocPathDir` no existe todavía, no hay ninguna funcionalidad documentada — devuelve que no hay coincidencias y detente aquí.
2. Lee `INDEX.md` (si no existe pero la carpeta sí, regenéralo primero con `scripts/rebuild-index.py` antes de leerlo). Es un listado corto — número, nombre de funcionalidad y área, no el contenido completo.
3. Valora por el nombre/área si alguna entrada del índice coincide semánticamente con lo que describe quien invoca (no hace falta coincidencia literal). Si hay 1-2 candidatas plausibles, lee esos ficheros completos (son pequeños) para confirmar antes de responder.
4. Devuelve a quien invoca: la ruta del fichero que coincide (si lo hay, con su contenido actual ya leído) o que no existe ninguna entrada equivalente todavía.

## Acción `upsert`

La invoca `pv-do` con el contenido ya completamente redactado (esta skill no reformula nada).

Parámetros:
- `area` — nombre del área funcional (tal cual debe aparecer en `**Área**:` y agrupar en el índice).
- `título` — nombre de la funcionalidad (tal cual debe aparecer como `# ...`).
- `cuerpo` — descripción funcional completa ya redactada (una o más frases/párrafos, con enlaces cruzados ya en formato `[texto](otro-slug.md)` si aplica).
- `diagramas` — opcional; lista completa de diagramas funcionales que deben quedar en el fichero final, cada uno ya como bloque ```mermaid``` completo (si es una edición in place, la lista resultante tras añadir/actualizar/quitar lo que corresponda, no solo los nuevos). Omitido o lista vacía si la funcionalidad no tiene ningún diagrama funcional.
- `disponible_en` — contenido de la línea `- **Disponible en**:`.
- `códigos` — lista completa de códigos `xxxx` que deben quedar en `- **Código**:` (si es una edición in place, la lista completa resultante tras añadir el nuevo, no solo el nuevo).
- `fichero_existente` — ruta devuelta por una llamada previa a `find`, si esto es una edición in place; omitido si es una funcionalidad nueva.

Pasos:

1. Si la carpeta de `featuresDocPathDir` no existe todavía, créala.
2. **Si hay `fichero_existente`**: usa ese mismo nombre de fichero (no lo renombres aunque el título haya cambiado ligeramente, para no romper enlaces cruzados de otras funcionalidades que ya apunten a él), **conserva el número identificador** que ya tenía en su `#` original (no lo recalcules) y **conserva su `- **Desde**:`** original tal cual. Calcula `- **Última modificación**:` como la fecha de hoy.
3. **Si no hay `fichero_existente`** (funcionalidad nueva):
   - Calcula el número identificador con `python .claude/skills/pv-internal-doc-features/scripts/next-feature-number.py --folder {featuresDocPathDir}`.
   - Calcula el slug del título con `python .claude/skills/pv-internal-doc-features/scripts/slugify.py "{título}"`.
   - El nombre de fichero es `{número}-{slug}.md`.
   - Tanto `- **Desde**:` como `- **Última modificación**:` son la fecha de hoy.
4. Escribe (crea o sobrescribe por completo) `{featuresDocPathDir}/{NNN}-{slug}.md` siguiendo [`FEATURE.template.md`](FEATURE.template.md) con los parámetros recibidos, con `# {número} — {título}` como primera línea. Si `diagramas` viene vacío u omitido, no dejes la sección de diagramas del template en el fichero final — omítela por completo.
5. Ejecuta `python .claude/skills/pv-internal-doc-features/scripts/rebuild-index.py --folder {featuresDocPathDir}` para regenerar `INDEX.md` de forma determinista a partir de todos los ficheros de la carpeta — no edites `INDEX.md` a mano.
6. Devuelve a quien invoca la ruta del fichero escrito.
