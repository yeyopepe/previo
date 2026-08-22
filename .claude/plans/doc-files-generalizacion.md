# Extraer la gestión de fichero a un skill genérico compartido por las 3 skills `pv-internal-doc-*`

## Contexto

`.claude/plans/doc-skills.md` deja constancia de una brecha: `pv-internal-doc-features` gestiona su fichero (numeración estable, `INDEX.md` regenerado por script, acciones `find`/`upsert`), pero `docs.tech.architectureDocDir` y `docs.tech.styleBibleDocDir` no — hoy `pv-do` numera y edita su `INDEX.md` a mano, en prosa, sin script de soporte (2 dígitos, sin campo `Area`). Esto es inconsistente y frágil (numeración manual, riesgo de colisión/drift en `INDEX.md`).

El usuario quiere que **las tres** áreas de documentación (`featuresDocPathDir`, `architectureDocDir`, `styleBibleDocDir`) compartan una única skill de gestión de fichero, y que el formato se unifique al de `doc-features`: 3 dígitos (`NNN`) + campo `**Area**:` + `INDEX.md` regenerado por script + `find`/`upsert`. Para `architectureDocDir`/`styleBibleDocDir`, "Area" pasa a representar el tema técnico/de estilo que agrupa el fichero en el índice (hoy ausente).

Además, el usuario pide documentar las responsabilidades resultantes en `pv-design.en.md`/`pv-design.es.md` con una tabla, siguiendo el mismo formato que la tabla de `.claude/plans/doc-skills.md`.

## Diseño del nuevo skill genérico: `pv-internal-doc-files`

Nuevo skill interno (`user-invocable: false`) en `.claude/skills/pv-internal-doc-files/`, que absorbe **toda** la lógica de gestión de fichero que hoy vive en `pv-internal-doc-features`, generalizada por carpeta. No decide contenido ni redacta — solo nombra el fichero, mantiene la numeración y regenera el índice.

**Contrato:**

- Parámetro común a ambas acciones: `folder` (la carpeta a gestionar — `featuresDocPathDir`, `architectureDocDir` o `styleBibleDocDir`).

- **Acción `find`** — idéntica semántica a la actual de `doc-features`:
  - Entrada: `folder`, una descripción breve de lo que se busca (nombre aproximado / área / tema).
  - Pasos: si la carpeta no existe, no hay coincidencias. Si `INDEX.md` no existe pero la carpeta sí, regenerarlo primero. Leer `INDEX.md`, juzgar semánticamente coincidencia, confirmar candidatos plausibles (1-2) leyendo el fichero completo.
  - Salida: ruta del fichero coincidente (con contenido ya leído) o "no existe entrada equivalente".

- **Acción `upsert`**:
  - Entrada: `folder`, `area` (texto libre — área funcional en features, tema técnico/de estilo en architecture/style), `title`, `body` (contenido ya completamente redactado por el caller — en features es descripción funcional + diagramas + `Available in`/`Code`/`Since`/`Last modified` ya formateados; en architecture/style es el contenido técnico libre que `pv-do` ya redacta hoy siguiendo `pv-internal-doc-technical`/`pv-internal-doc-style`), `existing_file` (opcional, de un `find` previo).
  - El skill **no conoce campos de dominio** (Available in, Code, Since, Last modified son responsabilidad exclusiva del caller, que los incluye ya formateados dentro de `body`) — así el mismo contrato sirve para los tres casos sin necesitar campos condicionales.
  - Pasos: crear la carpeta si no existe. Si hay `existing_file`: mantener nombre de fichero y número (no recalcular). Si no hay `existing_file`: calcular número con `next-feature-number.py --folder {folder}` (ya genérico, sin cambios), calcular slug con `slugify.py "{title}"`. Escribir `{folder}/{NNN}-{slug}.md` con primera línea `# {NNN} — {title}`, segunda línea `**Area**: {area}`, y el resto `{body}` tal cual. Regenerar `INDEX.md` con `rebuild-index.py --folder {folder}` (ya genérico, sin cambios de lógica).
  - Salida: ruta del fichero escrito.

**Scripts**: `next-feature-number.py`, `rebuild-index.py`, `slugify.py`, `_slug.py` se mueven de `pv-internal-doc-features/scripts/` a `pv-internal-doc-files/scripts/` sin cambios de lógica (ya son genéricos por `--folder`). `migrate-legacy-features-doc.py` se queda en `pv-internal-doc-features/` — es específico del caso "legacy `FEATURES.md` único" que solo aplica a features.

## Qué queda en `pv-internal-doc-features`

Se convierte en un wrapper delgado: mantiene su identidad de dominio (plantilla `FEATURE.template.md`, los campos `Available in`/`Code`/`Since`/`Last modified`, la regla de "nunca duplicar entrada, editar en su sitio") pero delega toda la gestión de fichero invocando internamente a `pv-internal-doc-files`. Se mantiene como skill propio (no se fusiona en `pv-do`) porque conserva responsabilidad real: sabe construir el `body` con los campos específicos de features y aplicar sus reglas de dominio (diagramas funcionales, cross-links `[text](NNN-slug.md)`). `pv-do` lo sigue invocando igual que hoy (misma interfaz `find`/`upsert` de cara a `pv-do`, sin romper su sección 2.1 actual para features).

## Cambios en `pv-do` (sección "2.1 Update documentation after implementing")

Para `architectureDocDir` y `styleBibleDocDir`: sustituir la numeración/edición manual de `INDEX.md` en prosa por invocaciones a `pv-internal-doc-files`:
- Antes de redactar, `action=find` con una descripción del tema tocado, para saber si ya existe fichero a editar en su sitio.
- Redactar el `body` (ya con las reglas de `pv-internal-doc-technical` / `pv-internal-doc-style` aplicadas) y guardar con `action=upsert`, pasando `area` (el tema técnico/de estilo), `title`, `body`, y `existing_file` si `find` encontró coincidencia.
- Eliminar de la prosa toda referencia a "next free number (`NN-slug.md`)" y "add it to INDEX.md's index table" manual — ahora es automático vía el skill.

Actualizar `metadata.uses` de `pv-do` para incluir `pv-internal-doc-files` junto a `pv-internal-doc-features`.

## Cambios en `pv-init/schema.json`

Actualizar la `description`/ejemplos de `docs.tech.architectureDocDir` y `docs.tech.styleBibleDocDir` (líneas ~172-181) para reflejar el nuevo formato: carpeta con `INDEX.md` + ficheros `NNN-slug.md` (3 dígitos) con campo `**Area**:`, igual convención que `featuresDocPathDir`, en vez de la actual "2-digit numeric prefix, e.g. `01-`, `02-`" sin área.

## Migración

No se crea script de migración genérico: el propio framework pv-* es su único "proyecto real" con `docs/architecture` configurado (ver `pv-context.json`), y sus ficheros existentes se ajustan a mano como parte de este mismo trabajo (renumerar a 3 dígitos, añadir `**Area**:`, regenerar `INDEX.md` con el script ya movido). No se justifica un script de un solo uso para un caso que se resuelve manualmente en minutos.

## Documentación de diseño (`pv-design.en.md` / `pv-design.es.md`)

Añadir una nueva tabla de responsabilidades para las skills `pv-internal-doc-*`, con el mismo formato que la tabla de `.claude/plans/doc-skills.md`, actualizada para reflejar el nuevo skill `pv-internal-doc-files` y el reparto final (features/architecture/style ya no gestionan fichero por su cuenta, todas delegan en `doc-files`). Ubicarla en la sección "Internal and support" de `pv-design.en.md` (y su traducción en `pv-design.es.md`), cerca de las entradas existentes de `pv-internal-doc-features`/`pv-internal-doc-technical`/`pv-internal-doc-style` (alrededor de la línea 172 en el `.md` inglés). Además:
- Añadir la entrada de responsabilidad de `pv-internal-doc-files` (nueva skill) en el listado de "Internal and support", con su bloque de "Assets and scripts" (los 4 scripts movidos).
- Actualizar la entrada existente de `pv-internal-doc-features` para reflejar que ahora delega la gestión de fichero en `pv-internal-doc-files` y que sus scripts se movieron (dejar solo `migrate-legacy-features-doc.py` y su plantilla).
- Actualizar la línea 21 (diagrama) y la línea 138 (lista de skills internas) para incluir `pv-internal-doc-files`.
- Actualizar la línea 300 (`tech.architectureDocDir` description) para reflejar 3 dígitos + Area en vez de "2-digit numeric prefix... `01-`, `02-`".
- Actualizar el árbol de estructura de ficheros (línea ~423) si referencia `INDEX.md` generado por `pv-internal-doc-features` — ahora es `pv-internal-doc-files`.

## Ficheros a crear/modificar

**Crear:**
- `.claude/skills/pv-internal-doc-files/SKILL.md`
- `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py` (movido)
- `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` (movido)
- `.claude/skills/pv-internal-doc-files/scripts/slugify.py` (movido)
- `.claude/skills/pv-internal-doc-files/scripts/_slug.py` (movido)

**Modificar:**
- `.claude/skills/pv-internal-doc-features/SKILL.md` (delgar en doc-files, quitar la lógica de numeración/índice que se traslada)
- `.claude/skills/pv-do/SKILL.md` (sección 2.1, `metadata.uses`)
- `.claude/skills/pv-init/schema.json` (descripciones de `architectureDocDir`/`styleBibleDocDir`)
- `.claude/pv-doc/pv-design/pv-design.en.md` (tabla nueva + actualizaciones puntuales arriba listadas)
- `.claude/pv-doc/pv-design/pv-design.es.md` (misma traducción)

**Eliminar** (tras mover):
- `.claude/skills/pv-internal-doc-features/scripts/next-feature-number.py`
- `.claude/skills/pv-internal-doc-features/scripts/rebuild-index.py`
- `.claude/skills/pv-internal-doc-features/scripts/slugify.py`
- `.claude/skills/pv-internal-doc-features/scripts/_slug.py`

**Versión**: `metadata.version` (hoy `0.9.5b11`) aparece en el frontmatter de `pv-internal-doc-features`, `pv-do`, y del nuevo `pv-internal-doc-files`. No se decide aquí el número final — se actualizará como parte del proceso normal de `pv-version`/`dev-generate-version`, fuera del alcance de este plan.

## Verificación

- Ejecutar manualmente `pv-internal-doc-files`'s `rebuild-index.py`/`next-feature-number.py` contra `docs/features` (caso ya existente) para confirmar que el comportamiento no cambió tras el movimiento de ficheros.
- Ajustar a mano los ficheros existentes en `docs/architecture` del propio repo (renumerar a `NNN`, añadir `**Area**:`) y regenerar su `INDEX.md` con el script movido, para validar el nuevo formato end-to-end.
- Revisar que `pv-do/SKILL.md` ya no menciona numeración manual de 2 dígitos en ningún punto de la sección 2.1.
- Relectura cruzada de `pv-design.en.md`/`pv-design.es.md` para que la nueva tabla y los puntos actualizados no contradigan el resto del documento (diagrama, listado de skills internas, árbol de estructura).
