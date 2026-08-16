---
name: pv-internal-changelog
description: Redacta changelog.md a partir de las entradas acumuladas en {workFolder}/changes/closed, desde una perspectiva estrictamente funcional, y borra las carpetas incorporadas tras confirmación. Uso interno de la skill pv-version.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.2
  uses: []
---

# pv-internal-changelog

Redacta `changelog.md` para una entrega en preparación, a partir de las entradas acumuladas en `{workFolder}/changes/closed/`, y borra esas carpetas tras confirmación explícita del usuario. Solo lo invoca `pv-version` — no está pensado para invocación directa por el usuario.

## Guardarraíl de invocación — leer antes que nada

Esta skill **no se ejecuta si se ha invocado directamente** (p.ej. el usuario ha escrito `/pv-internal-changelog`, o ha pedido "ejecuta/invoca pv-internal-changelog" en texto plano). Solo debe ejecutarse cuando el propio contenido de `pv-version` te ha instruido a invocarla como parte de su proceso, con la carpeta destino ya resuelta.

Si te han invocado sin ese contexto, **detente aquí** y dile al usuario que `pv-internal-changelog` es de uso interno del framework: para preparar una entrega debe usar `/pv-version`. No hagas nada más en ese caso.

```
`/pv-internal-changelog` es de uso interno del framework `pv-*` y no se invoca directamente. Para preparar una entrega usa `/pv-version`.
```

**Entrada esperada de quien invoca:** carpeta destino `{workFolder}/versions/{XXXX}/` (la versión que se está preparando).

## 1. Listar entradas de `closed`

Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-internal-changelog/scripts/list-closed-entries.py
```

Devuelve un JSON con, por cada subcarpeta de `{workFolder}/changes/closed/`, su `xxxx` y la ruta a su `description.md`. Si `entries` viene vacío, informa a quien invoca que no hay nada que incorporar y termina aquí — no crees `changelog.md` ni toques nada más.

## 2. Localizar el changelog de la versión anterior

Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-internal-changelog/scripts/find-previous-version.py --xxxx <XXXX>
```

Recorre `{workFolder}/versions/`, excluye la carpeta `{XXXX}` que se está generando, y devuelve la de fecha de creación más reciente (o `"found": false` si no hay ninguna otra).

- Si `"found": true`: **confirma con el usuario** que esa `xxxx` es la versión anterior correcta antes de usarla (muéstrasela explícitamente) — si el usuario indica otra, usa esa en su lugar. Si `"changelogExists": true`, lee ese `changelog.md` como referencia de qué funcionalidad ya estaba recogida. Si `"changelogExists": false` (versión previa a medio preparar, sin changelog todavía), trátalo igual que si no hubiera versión anterior.
- Si `"found": false`: no hay versión anterior — todo irá a **Nuevo** en el paso 3.

## 3. Redactar `changelog.md`

Por cada entrada de `closed/`, lee su `description.md` y toma sus campos **Nombre**, **Tipo** y **Descripción completa** (ya redactados en términos puramente funcionales por `pv-internal-workflow` al crearlos — no releas código ni reinterpretes técnicamente). Clasifícala en una de cuatro secciones:

- **Correcciones y ajustes** — si **Tipo** es `fix` o `fast`: siempre va aquí directamente, sin comparar contra la versión anterior (son correcciones o cambios triviales, no funcionalidad nueva ni un cambio de comportamiento a documentar como tal).
- En cualquier otro caso (**Tipo** `change`), compárala contra el `changelog.md` de la versión anterior (si lo hay) y clasifícala en:
  - **Nuevo** — funcionalidad que no existía antes (o no hay versión anterior con la que comparar).
  - **Cambios** — modifica o amplía algo que ya aparecía en el changelog anterior.
  - **Eliminado** — quita o desactiva algo que aparecía en el changelog anterior.

Escribe `{workFolder}/versions/{XXXX}/changelog.md` siguiendo la plantilla [`changelog.template.md`](changelog.template.md): cabecera con el `XXXX` de la versión, la fecha, y el número de elementos de cada sección (Nuevo, Cambios, Eliminado, Correcciones y ajustes — cuenta también las que queden en 0), seguida de las cuatro secciones (omite una sección entera si queda vacía), cada entrada con nombre en negrita + resumen funcional en una o dos frases (tono changelog, en pasado), sin mencionar ficheros, funciones ni detalles técnicos.

## 4. Confirmar borrado con el usuario antes de borrar nada

Muestra la lista de `xxxx` que se han incorporado al changelog y pide confirmación explícita de que se pueden borrar sus carpetas de `{workFolder}/changes/closed/` (acción irreversible). Si el usuario no confirma, deja `changelog.md` ya escrito pero no borres nada, y díselo a quien invoca (`pv-version`) en el paso 6.

## 5. Borrar las entradas incorporadas

Solo tras confirmación, ejecuta desde la raíz del repo:

```
python .claude/skills/pv-internal-changelog/scripts/delete-closed-entries.py --xxxx-list <lista de xxxx incorporados, separados por comas>
```

Borra únicamente esas carpetas concretas de `{workFolder}/changes/closed/`, nunca "todo `closed/`" a ciegas, por si aparecieron entradas nuevas entretanto.

## 6. Confirmar a quien invoca

Indica la ruta de `changelog.md` generado, cuántas entradas cayeron en cada sección (Nuevo/Cambios/Eliminado/Correcciones y ajustes), y si se borraron o no las carpetas de `closed/` (y en su caso, cuáles).
