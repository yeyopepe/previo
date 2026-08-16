---
name: pv-todo
description: Apunta y desarrolla ideas sueltas para el futuro sin meterlas en el flujo de trabajo del proyecto — las guarda en {changesDir}/todo/{código}/description.md, una carpeta aparte que ninguna otra skill pv-* usa ni tiene en cuenta. Sirve tanto para anotar una idea nueva como para seguir desarrollando/ampliando una ya apuntada. Trigger: /pv-todo [código] <idea>, o cuando el usuario pide "apuntar"/"dejar anotada" una idea para más adelante, sin pedir que se documente como change/fix.
argument-hint: "[código] <idea a anotar o desarrollar>"
model: claude-haiku-4-5
effort: medium
metadata:
  version: 0.9.0
  uses: []
---

# pv-todo

Cuaderno de ideas del framework `pv-*`, pero **fuera** de su flujo de trabajo: no documenta un cambio/fix a implementar, solo deja constancia de una idea para desarrollarla más adelante, a un ritmo distinto del de `pv-new`/`pv-fix`. No hay planificación (`pv-how`/`pv-do`), ni estados (`inProgress`/`implemented`/`closed`), ni versión: una idea anotada aquí se queda aquí hasta que, en su caso, alguien decida convertirla en un change/fix de verdad con `pv-new`/`pv-fix` (fuera ya de esta skill).

Vive en `{changesDir}/todo/`, una subcarpeta hermana de `inProgress`/`implemented`/`closed` pero **ajena por completo** al resto del framework: ninguna otra skill `pv-*` la lee, la escribe, ni cuenta sus carpetas al numerar o buscar cambios/fixes. Los códigos que usa esta skill no tienen ninguna relación con el `xxxx` numérico de change/fix — son solo identificadores únicos dentro de `{changesDir}/todo/`.

## 0. Comprobar que el framework está inicializado

Si `.claude/pv-context.json` no existe en la raíz del repo, o le falta la sección `framework`, no continúes: dile al usuario que primero debe ejecutar la skill `pv-init` para inicializar/completar el framework en este proyecto, y detente ahí.

```
Este proyecto todavía no tiene el framework `pv-*` inicializado (o le falta configuración). Ejecuta primero `/pv-init` antes de volver a invocarme.
```

A partir de aquí, `changesDir` es notación abreviada para `{workFolder}/changes` (subcarpeta de nombre fijo dentro de `framework.workFolder`, que por defecto es `"/"`, la raíz del repo).

## 1. Decidir si es una idea nueva o una ampliación

Si el usuario indica un código al invocar esta skill (p.ej. `/pv-todo a3f9k añade también...`), comprueba si existe **exactamente** `{changesDir}/todo/{código}/`.

- **Si existe**: es una ampliación de una idea ya apuntada. Ve a la sección [Ampliar una idea ya apuntada](#ampliar-una-idea-ya-apuntada).
- **Si no existe**, o no se ha indicado ningún código: es una idea nueva. Continúa en el paso 2.

Si el usuario no da contenido alguno (p.ej. solo pide "qué ideas tengo apuntadas" o "lista las todo"), salta directamente al paso de [Listar ideas apuntadas](#listar-ideas-apuntadas) sin crear ni modificar nada.

## 2. Generar un código único

La generación y comprobación de colisión las hace de forma determinista y gratis en tokens el script [`scripts/new-todo-code.py`](scripts/new-todo-code.py) (Python estándar, sin dependencias externas) — no lo hagas a mano. Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-todo/scripts/new-todo-code.py
```

El script lee `workFolder` de `.claude/pv-context.json` (o usa `--work-folder` si se lo pasas), lista las subcarpetas que ya existan bajo `{changesDir}/todo/` (sin necesidad de que exista todavía — en ese caso no hay ninguna carpeta que colisione), genera un código alfanumérico corto (`[a-z0-9]`, 5 caracteres por defecto, `--length` para otro tamaño) que no coincida con ninguna ya existente ahí, e imprime únicamente ese código por stdout. No consulta ni tiene en cuenta ninguna otra carpeta del repo (ni `inProgress`/`implemented`/`closed`, ni nada fuera de `{changesDir}/todo/`): la única condición de unicidad es no repetirse dentro de esta subcarpeta. Usa ese valor tal cual como código — no lo recalcules a mano.

## 3. Anotar la idea

Sin preguntar dudas de alcance ni proponer respuestas a huecos funcionales (eso es lo que distingue esta skill de `pv-new`/`pv-fix`: aquí se anota la idea tal cual está, aunque esté incompleta o sea solo un esbozo), crea:

```
{changesDir}/todo/{código}/description.md
```

**`description.md`** sigue **exactamente** la plantilla [`description.template.md`](description.template.md) de esta misma carpeta: cuatro cabeceras markdown `## Idea`, `## Código`, `## Fecha creación` y `## Notas`, en ese orden, sin negrita ni `:` al final de la cabecera (ni `## Idea:` ni `**Idea:**`) — `list_todo.py`/`collect_status.py` de `pv-status` parsean estas cabeceras con una expresión regular literal (`^##\s*Idea\s*\n+`) y cualquier variación (cabecera en negrita, dos puntos, título distinto como "Ide") hace que la idea no se pueda leer y aparezca como "(sin idea)" en `/pv-status todo`.

- **Idea** — nombre corto que resuma la idea.
- **Código** — el código generado en el paso 2.
- **Fecha creación** — la fecha actual (formato `YYYY-MM-DD`) en el momento de crear este `description.md`.
- **Notas** — el contenido de la idea, tal como la ha planteado el usuario. Puede ser una frase suelta, una lista de posibilidades, dudas abiertas sin resolver, o cualquier otra forma en la que el usuario quiera dejarla anotada — no fuerces la estructura de `description.md` de `pv-new`/`pv-fix` (no hay "Prompt original" ni "Descripción completa" separados).

Si la idea tiene componente visual claro y el usuario quiere dejar constancia de ello, puedes crear también algún `design_*.html` igual que hace `pv-new` (maqueta autocontenida, sin funcionalidad real) — pero no es obligatorio ni el foco de esta skill; solo hazlo si el usuario lo pide o aporta ese material.

## 4. Confirmar al usuario

Indica el código asignado y la ruta del fichero creado, y recuerda que esta idea se queda anotada en `{changesDir}/todo/` sin entrar en el flujo de trabajo — si en algún momento se quiere convertir en un cambio/fix real, hay que documentarla de nuevo con `pv-new`/`pv-fix` (esta skill no hace esa conversión automáticamente).

## Ampliar una idea ya apuntada

Cuando el paso 1 detecta que el código indicado ya existe en `{changesDir}/todo/{código}/`:

1. Abre `{changesDir}/todo/{código}/description.md` para ver lo ya anotado.
2. Añade lo nuevo a la sección **Notas**, dejando lo anterior tal cual (no lo borres ni lo reescribas) y añadiendo lo nuevo a continuación — igual que un cuaderno donde se sigue escribiendo, no un documento que se reformula cada vez.
3. Confirma al usuario que la idea `{código}` queda actualizada.

## Listar ideas apuntadas

Si el usuario pide ver qué ideas hay anotadas: lista las subcarpetas de `{changesDir}/todo/` y, para cada una, su código y el campo **Idea** de su `description.md`. Si la carpeta no existe o está vacía, dilo así — no hay ninguna idea apuntada todavía.

## Qué NO hace esta skill

- No planifica ni implementa nada (no hay equivalente a `pv-how`/`pv-do` aquí).
- No mueve ideas entre estados ni las "cierra" — para eso no hay flujo; si una idea deja de interesar, es el usuario quien decide borrarla o dejarla tal cual.
- No numera con el `xxxx` del framework ni invoca `pv-internal-workflow` — su numeración es independiente y local a `{changesDir}/todo/`.
- No cuenta como fuente de intención para `pv-how`, `pv-do` ni ninguna otra skill del framework: `{changesDir}/todo/` es territorio exclusivo de `pv-todo`.
