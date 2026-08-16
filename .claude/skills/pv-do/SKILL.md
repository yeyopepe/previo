---
name: pv-do
description: Implementa un change/fix cuyo plan.md ya está escrito en {changesDir}/inProgress/{xxxx}/ — edita el código según la solución técnica, actualiza la documentación sincronizada, y mueve la entrada a {changesDir}/implemented. Parte del framework pv-*. Trigger: /pv-do <xxxx>, o cuando el usuario pide implementar un cambio/fix ya planificado por pv-how (normalmente encadenado automáticamente desde ella).
argument-hint: <xxxx del cambio/fix ya planificado>
model: claude-haiku-4-5
effort: medium
metadata:
  version: 0.9.1
  uses: [pv-internal-workflow, pv-internal-doc-features]
---

# pv-do

Toma una entrada de `{changesDir}/inProgress/{xxxx}/` cuya solución técnica ya está escrita en `plan.md` (por la skill `pv-how`) y la lleva hasta implementada: edita el código, actualiza la documentación sincronizada, y mueve la carpeta a `{changesDir}/implemented/{xxxx}/`.

**Fuente de la verdad.** El `plan.md` de esta entrada es la guía de lo que hay que implementar. Si durante la implementación algo no cuadra con el código real, el código manda — para y coméntaselo al usuario en vez de improvisar una solución distinta sin decírselo (ver paso 2). Si la entrada tiene un `history.md`, no lo abras: es historial de prompts de uso exclusivo de `pv-new`/`pv-fix`, nunca información a tener en cuenta al implementar ni al documentar (paso 2.1), y leerlo solo gastaría contexto sin aportar nada.

**Nunca uses git de forma destructiva ni hagas commit sin permiso.** Esta skill edita ficheros de código/documentación y mueve la carpeta del cambio (paso 3), pero nunca va más allá por su cuenta:

- No ejecutes `git commit` (ni `git add` seguido de commit) salvo que el usuario lo haya pedido explícitamente en este turno. Terminar la implementación no es una autorización implícita para commitear.
- No ejecutes `git restore`, `git checkout -- <fichero>`, `git reset`, `git clean`, ni ningún otro comando que descarte cambios en el árbol de trabajo, aunque el fichero afectado parezca no tener relación con esta entrada. Si al hacer `git status`/`git add` ves cambios de otro trabajo en curso (tuyo o del usuario) que no quieres incluir, dilo y pregunta cómo proceder — no los deseches tú mismo.
- Si necesitas comprobar el estado del repo (`git status`, `git diff`) hazlo solo para verificar tu propio trabajo, nunca como paso previo a limpiar o descartar ficheros que no has tocado en esta implementación.

## 0. Cargar el contexto del proyecto

Lee `.claude/pv-context.json` en la raíz del repo. Si no existe, o le falta la sección `framework`, no continúes: dile al usuario que primero debe ejecutar la skill `pv-init` para inicializar/completar el framework en este proyecto, y detente ahí.

```
Este proyecto todavía no tiene el framework `pv-*` inicializado (o le falta configuración). Ejecuta primero `/pv-init` antes de volver a invocarme.
```

`docs.tech.architectureDocDir`, `docs.functional.featuresDocPathDir` y `docs.tech.styleBibleDocDir` son opcionales y se usan en el paso 2.1; si no están configurados, omite las actualizaciones correspondientes sin preguntar nada.

## 1. Identificar la entrada a implementar

Si el usuario, al invocar esta skill, indica un `xxxx`, un nombre de carpeta o una descripción del cambio/fix, resuélvelo buscando **únicamente** dentro de `{changesDir}/inProgress/`, y comprueba que tiene `plan.md`:

- Si la carpeta existe pero **no** tiene `plan.md` todavía: no continúes. Dile al usuario que esa entrada aún no tiene solución técnica planificada y que primero debe invocar `pv-how` sobre ese `xxxx`.
- Si no encuentras ninguna carpeta que corresponda dentro de `{changesDir}/inProgress/`: si existe con ese `xxxx` en `{changesDir}/implemented/`, dile al usuario que ese cambio/fix ya está implementado; si no existe en ningún sitio, dile que no lo encuentras y pregunta el `xxxx` o la carpeta correctos.

**Si no indica nada** (p.ej. invoca `/pv-do` sin argumentos): no asumas que se refiere al último cambio/fix mencionado en la conversación ni a ningún otro dato del contexto de chat. Lista únicamente las carpetas de `{changesDir}/inProgress/` que ya tengan `plan.md` (listas para implementar) — su `xxxx` y, si lo tiene, el nombre/resumen de su `description.md` — y pregunta explícitamente al usuario cuál quiere implementar. Si no hay ninguna con `plan.md` todavía (aunque haya entradas en `inProgress` sin planificar), dile que no hay ningún cambio/fix listo para implementar y que primero hace falta planificarlo con `pv-how`.

```
Estos cambios/fixes ya tienen `plan.md` y están listos para implementar:
- {xxxx} — {nombre/resumen}
- ...

¿Cuál quieres que implemente?
```

```
No hay ningún cambio/fix con `plan.md` listo para implementar. Usa `pv-how` primero para planificar alguno de los pendientes en `{changesDir}/inProgress/`.
```

Una vez identificada, esa es `{xxxx}` y su carpeta `{changesDir}/inProgress/{xxxx}/` para el resto del proceso.

## 2. Implementar

Implementa todo lo que dice `plan.md`. Sus checklists (`(b)` y, si existe, `(e)`) son la única lista de tareas fiable — no confíes en lo que recuerdes de haberlas leído antes, ve casilla por casilla:

- Recorre la sección **(b) Solución técnica** **una tarea a la vez, en orden**: implementa esa tarea concreta (editar código, verificar que compila / pasan los tests si los hay) y, inmediatamente después de darla por hecha, edita `plan.md` marcando esa casilla como `- [x]` antes de pasar a la siguiente. No implementes varias tareas seguidas y las marques todas al final — el marcado inmediato es lo que evita saltarse una sin darte cuenta.
- Si `plan.md` tiene sección **(c) Cambios de arquitectura**, aplica esos cambios al fichero (o ficheros) de `docs.tech.architectureDocDir` que indique esa sección, como parte de esta implementación.
- Si `plan.md` tiene sección **(e) Verificación**, una vez marcadas todas las casillas de (b), recorre cada ítem de (e) **uno a uno** y comprueba que el resultado observable descrito se cumple de verdad (leyendo el código/DOM/estilos resultantes, no dando por hecho que la tarea de (b) que lo produce quedó bien). Marca su casilla `- [x]` solo cuando lo hayas comprobado así. Si algún ítem no se cumple, corrígelo antes de marcarlo — no lo des por terminado ni lo menciones como pendiente al usuario.
- **Antes de pasar al paso 3**, relee `plan.md` completo buscando casillas `- [ ]` sin marcar en (b) o (e). Si encuentras alguna, esa tarea o verificación quedó pendiente sin que te dieras cuenta: complétala ahora, no la ignores ni la des por implícita.

Si durante la implementación descubres que el plan no es viable tal cual está escrito, para y coméntaselo al usuario en vez de improvisar una solución distinta sin decírselo.

## 2.1 Actualizar documentación tras implementar

Una vez implementado en código lo anterior, actualiza siempre lo siguiente antes de mover la carpeta:

- **`docs.tech.architectureDocDir`** — si está configurado, revisa el fichero (o ficheros) de esa carpeta que correspondan al área tocada y déjalos reflejando fielmente el estado técnico resultante. Aplica lo que diga la sección (c) del plan si la tenía; si no la tenía pero al implementar resulta que sí se ha tocado algo que esa carpeta describe, actualízala igualmente — no depende únicamente de que el plan lo anticipara. Si la solución introduce un tema nuevo que no encaja en ningún fichero existente de esa carpeta, crea uno nuevo con el siguiente número libre (`NN-slug.md`, sin reutilizar ni renumerar los existentes) y añádelo a la tabla-índice de `INDEX.md`. Si no está configurado, omite este punto sin preguntar nada.
- **`docs.functional.featuresDocPathDir`** — si está configurado, es documentación **funcional**, no un changelog: describe qué puede hacer la app hoy, organizado por área/módulo funcional, no una lista cronológica de changes/fixes. En cualquiera de los dos casos de abajo, si lo implementado amplía o modifica una funcionalidad que ya tiene entrada propia, **edítala in place** para que siga describiendo fielmente el comportamiento actual (nunca añadas una entrada nueva para lo mismo), añadiendo el `xxxx` de esta entrada a su campo **Código**; si es una funcionalidad nueva, crea una entrada en el área funcional que le corresponda (crea el área si no existe todavía) con el `xxxx` de esta entrada en **Código**.
  - **Diagramas funcionales.** Si `description.md` de esta entrada contiene algún diagrama Mermaid **funcional** (los generados en el paso 2 de `pv-new`/`extend-entry.md`), o la carpeta de la entrada tiene uno o varios `design_navigation_*.md` (diagramas de navegación de UI — `pv-new` puede haber generado varios, uno por cada caso de uso distinto), y alguno de esos diagramas representa un flujo de la funcionalidad que estás documentando aquí, llévalo también a la entrada de features — tal cual, sin reescribirlo. Si dos o más de esos diagramas se referencian entre sí (p.ej. uno dice "ver diagrama 1" o nombra un estado/nodo definido en otro fichero), llévalos siempre juntos, todos o ninguno — nunca incluyas un diagrama que referencia a otro sin ese otro también, para no dejar una referencia rota en la documentación de features. **Nunca** lleves diagramas técnicos (los de `plan.md`: flujo técnico, secuencia técnica, ni los de `docs.tech.architectureDocDir`) — esos son de implementación interna, no de cara al usuario. Si la entrada de features ya tenía diagramas propios de una versión anterior de la funcionalidad, consérvalos salvo que este cambio los deje desactualizados (en ese caso, sustitúyelos por los nuevos en vez de acumular ambos).
  - **Si `featuresDocPathDir` es una carpeta** (la convención recomendada — compruébalo mirando si existe como directorio, o si aún no existe pero el valor no termina en `.md`): invoca la skill `pv-internal-doc-features` (herramienta Skill) con `action=find` y una descripción breve de la funcionalidad implementada, para saber si ya tiene fichero propio. Redacta el contenido final (cuerpo, diagramas funcionales según el punto anterior, `Disponible en`, lista completa de `Código`) tú mismo con el criterio de arriba, y guárdalo invocando `pv-internal-doc-features` con `action=upsert` (pasando `diagramas` solo si hay alguno que incluir) — pasando `fichero_existente` si `find` devolvió una coincidencia, u omitiéndolo si es una entrada nueva.
  - **Si `featuresDocPathDir` es un único fichero** (proyectos que todavía no han migrado a carpeta): edítalo tú mismo con el mismo criterio (incluidos los diagramas funcionales), usando como plantilla de una entrada nueva la de [`FEATURES.template.md`](FEATURES.template.md) de esta skill; créalo a partir de esa plantilla si todavía no existe.
  - Si `docs.functional.featuresDocPathDir` no está configurado, omite este punto sin preguntar nada.
- **`docs.tech.styleBibleDocDir`** — si está configurado, revisa el fichero (o ficheros) de esa carpeta que correspondan y actualízalos si lo implementado introduce o modifica convenciones de estilo (visual, de interacción, de redacción, etc.) relevantes para el proyecto. Igual que con `architectureDocDir`, si el tema no encaja en ningún fichero existente crea uno nuevo con el siguiente número libre y añádelo a la tabla-índice de `INDEX.md`. Si no está configurado, o lo implementado no afecta a ninguna convención de estilo, omite este punto sin preguntar nada.

## 3. Mover la carpeta a `implemented`

Invoca la skill `pv-internal-workflow` (herramienta Skill) con `action=move`, `xxxx`, `from=inProgress` y `to=implemented` — no muevas la carpeta tú mismo.

## 4. Confirmar al usuario

Indica qué se ha implementado, qué documentación se ha actualizado (`docs.tech.architectureDocDir`/`docs.functional.featuresDocPathDir`/`docs.tech.styleBibleDocDir`, según aplicara), y que la carpeta se movió a `{changesDir}/implemented/{xxxx}/`.
