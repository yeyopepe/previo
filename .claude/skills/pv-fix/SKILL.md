---
name: pv-fix
description: Analiza un bug/comportamiento roto o un cambio muy pequeño y de análisis casi nulo (typo, ajuste de un valor/constante, texto, un estilo puntual...) pedido por el usuario. Si el análisis revela que es trivial (bug o no), lo aplica y documenta directamente en el mismo turno, sin pasar por `plan.md`. Si no es trivial y es un bug, lo documenta en {changesDir}/inProgress y lo implementa encadenando pv-how (que a su vez encadena pv-do), con el análisis acotado estrictamente al fix. Si no es trivial y no es un bug (funcionalidad nueva o cambio intencionado mayor), avisa e invoca pv-new en su lugar. Trigger: /pv-fix, o cuando el usuario pide explícitamente "un fix"/corregir un bug, o "algo rápido"/"un fast" para un cambio o fix trivial.
argument-hint: <descripción del bug o cambio a aplicar>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.0
  uses: [pv-internal-workflow, pv-internal-tech-analysis, pv-internal-mockups-html, pv-internal-tech-mermaid, pv-new, pv-how]
---

# pv-fix

Analiza, documenta e implementa un fix (comportamiento roto) sobre el proyecto, y además es la vía rápida del framework `pv-*` para cambios **muy pequeños y de análisis casi nulo** (un typo, un texto, un valor/constante puntual, un ajuste de estilo aislado — sean o no un bug). Para funcionalidad nueva o cambios intencionados que no sean triviales usa la skill `pv-new`, no esta. Parte del framework `pv-*`.

Un fix no trivial es, por naturaleza, un cambio acotado: el análisis y la solución deben centrarse **única y exclusivamente en corregir el bug reportado**, con el menor cambio posible. Nada de aprovechar para refactorizar, renombrar o tocar código no relacionado con la causa raíz — eso, si hace falta, es un `pv-new` aparte.

**Nunca uses git de forma destructiva ni hagas commit sin permiso.** La rama fast-track de esta skill edita código directamente, pero eso no autoriza a ir más allá:

- No ejecutes `git commit` (ni `git add` seguido de commit) salvo que el usuario lo haya pedido explícitamente en este turno. Terminar el cambio no es una autorización implícita para commitear.
- No ejecutes `git restore`, `git checkout -- <fichero>`, `git reset`, `git clean`, ni ningún otro comando que descarte cambios en el árbol de trabajo, aunque el fichero afectado parezca no tener relación con este fix. Si ves cambios de otro trabajo en curso (tuyo o del usuario) que no quieres incluir, dilo y pregunta cómo proceder — no los deseches tú mismo.

**Primero valora si el cambio es trivial.** Antes de decidir cómo tratarlo, esta skill siempre comprueba si lo pedido califica como "fast" (ver paso 2). Si califica, se aplica y documenta ya implementado en el mismo turno, sin pasar por `{changesDir}/inProgress/` con `plan.md` ni encadenar `pv-how`/`pv-do`. **Esto no es un atajo para saltarse el análisis de algo que sí lo necesita** — es solo para lo que verdaderamente no requiere ninguno. Si tienes dudas razonables sobre si califica, no lo fuerces: trátalo como que no califica.

Si lo pedido no es trivial:
- Si es un bug, sigue el flujo normal de esta skill (documentar + encadenar `pv-how`/`pv-do`).
- Si no es un bug (funcionalidad nueva o modificación de comportamiento intencionada que no es trivial), esta skill no la asume: avisa al usuario e invoca `pv-new` con la petición tal cual, para que arranque su propio proceso de definición.

Para el fix no trivial, esta skill no implementa nada por sí misma: documenta la intención y encadena directamente la skill `pv-how`, que es quien analiza la causa raíz técnica y escribe el `plan.md`, y que a su vez (si se confirma) encadena `pv-do` para implementar.

**Los mockups y diagramas son el eje central de la definición de un fix no trivial, no un añadido opcional.** Siempre que el fix lo permita, el comportamiento esperado debe quedar fijado mediante una representación visual — no solo prosa — y esa representación debe quedar **validada por el usuario**, no solo generada. Casos válidos (no excluyentes): **cambios visuales o de estilo** → maqueta(s) HTML (`design_*.html`, paso 4); **flujos o interacciones rotos** (una secuencia de pasos, una transición de estados) → diagrama Mermaid dentro de `description.md` (paso 3). Solo prescinde de ambos si el fix no tiene de verdad ninguna dimensión visual ni de flujo representable. Un cambio fast-tracked (trivial) nunca genera mockups ni diagramas — por definición no tiene ninguna decisión de diseño que fijar.

**Fuente de la verdad.** Para distinguir qué hace hoy el proyecto de lo que el usuario cree que hace, la única fuente de verdad es la documentación técnica y el código real — no asunciones ni memoria de la conversación. Para reunir ese contexto, invoca la skill `pv-internal-tech-analysis` (herramienta Skill) pasándole un resumen de lo que se está analizando, en vez de leer tú mismo `framework.docs.tech` o explorar el código a ciegas: ella lee primero la documentación técnica configurada y explora código solo si hace falta, devolviendo el contexto reunido y cualquier incongruencia entre documentación y código (en ese caso el código manda). Si detecta alguna incongruencia, anótala en **Apuntes técnicos** al documentar (fix no trivial, paso 3) o tómala como motivo para no calificar como trivial (paso 2). Tampoco cuenta como fuente de verdad el contenido de otros cambios/fixes que existan bajo `{changesDir}/**` (su `description.md` o `plan.md`, estén en `inProgress`, `implemented` o `closed`): son intención o análisis de otra entrada, no el estado real del proyecto.

## 0. Comprobar que el framework está inicializado

Si `.claude/pv-context.json` no existe en la raíz del repo, o le falta la sección `framework` (o campos suyos necesarios), no continúes: dile al usuario que primero debe ejecutar la skill `pv-init` para inicializar/completar el framework en este proyecto, y detente ahí.

```
Este proyecto todavía no tiene el framework `pv-*` inicializado (o le falta configuración). Ejecuta primero `/pv-init` antes de volver a invocarme.
```

## 1. Entender la petición a nivel funcional

Si hay ambigüedad sobre qué comportamiento es el correcto (para un bug) o qué hay que cambiar exactamente (para un cambio pequeño), pregunta. No hace falta localizar la causa raíz en código todavía — eso, si el cambio resulta no ser trivial, lo hace `pv-how` al analizar el fix en detalle.

## 2. Valorar si el cambio es "fast"

Invoca la skill `pv-internal-tech-analysis` (herramienta Skill) pasándole un resumen de la petición, para reunir el contexto técnico necesario (lee primero la documentación de `framework.docs.tech` configurada, y solo explora código si hace falta). Con ese contexto ya reunido, valora la petición contra estos criterios — para calificar como `fast` debe cumplirlos **todos**, sea o no un bug:

- Se entiende sin ambigüedad qué hay que cambiar con una sola lectura de la petición — no falta información relevante ni hace falta tomar ninguna decisión de diseño o de alcance. Si para poder aplicarlo necesitarías preguntar bastante al usuario, no es `fast`.
- Toca pocos ficheros, de forma muy localizada (una constante, un texto, un valor, una regla de estilo, una condición puntual, un typo). Si afecta a más de 3 ficheros, no es `fast`, por poco que sea el cambio en cada uno.
- Si el cambio implica 0% de riesgo para el resto de la aplicación (no modifica ninguna interfaz de ninguna función o la modifica asegurando totalmente la retrocompatibilidad; no cambia ninguna respuesta; no cambia ningún flujo; no cambia ningún valor utilizado por otras partes de la aplicación además de la que estamos modificando), es `fast`.
- No introduce comportamiento nuevo ni cambia un flujo o interacción existente — como mucho ajusta un valor, texto o aspecto de algo que ya existe.
- No tiene casos límite relevantes que analizar, ni afecta a cómo conviven distintas partes del proyecto entre sí.
- Si es un bug: no es, ni de lejos, uno cuya causa raíz haya que investigar — si hace falta indagar para encontrar por qué falla algo, no es `fast` (pero sigue siendo un fix: ve al paso 3).
- Si el cambio afecta a **`docs.tech.architectureDocDir`** o **`docs.tech.styleBibleDocDir`** (si están configurados en `.claude/pv-context.json`) solo en valores de constantes o parámetros, es `fast`.
- Si el cambio afecta a **`docs.tech.architectureDocDir`** o **`docs.tech.styleBibleDocDir`** (si están configurados en `.claude/pv-context.json`) de forma relevante (una decisión de arquitectura, una convención de estilo visual/interacción/redacción), no es `fast`, aunque el cambio en el código en sí sea pequeño. Si `pv-internal-tech-analysis` reporta alguna incongruencia entre esos documentos y el código, tampoco califica como `fast`: una incongruencia con la documentación técnica es, por definición, algo que afecta a esos documentos.
- Si el cambio afecta a **`docs.functional.*`** no es `fast`.

Ejemplos orientativos que sí calificarían: corregir un texto o typo, cambiar un color/tamaño/margen puntual, ajustar el valor de una constante o configuración, corregir un enlace o ruta mal escrita, renombrar una etiqueta visible, o un bug evidente de un vistazo (p.ej. una condición invertida en un único sitio).

Ejemplos que **no** calificarían (aunque el usuario los pida como "rápidos"): cualquier funcionalidad nueva, cualquier cambio que module cómo se comporta algo (no solo su aspecto/valor), cualquier fix cuya causa no sea obvia a simple vista, cualquier cambio que toque más de 2 ficheros o varios flujos/componentes relacionados entre sí, cualquier cambio que afecte a arquitectura o a la biblia de estilo.

Si tienes dudas razonables sobre si califica, no lo fuerces: trátalo como que no califica.

**Si califica como `fast`**, ve a la sección "Rama fast-track" más abajo — no sigas con el resto de pasos numerados de esta skill.

**Si no califica:**
- Y es un bug (aunque no calificara como `fast` por su causa raíz, sigue siendo un fix): continúa con el paso 3.
- Y no es un bug (funcionalidad nueva o modificación de comportamiento intencionada): avisa al usuario indicando explícitamente qué punto de los criterios no cumple, y a continuación, sin esperar confirmación adicional, invoca directamente la skill `pv-new` (herramienta Skill) pasándole tal cual la petición del usuario, para que arranque su propio proceso de definición en `{changesDir}/inProgress/`. No sigas con el resto de pasos de esta skill: a partir de aquí el proceso lo continúa `pv-new`.

  ```
  Esto no califica como cambio "fast" ni es un bug: {motivo concreto incumplido}. Voy a documentarlo con `pv-new` para analizarlo y planificarlo como corresponde.
  ```

## 3. Documentar la intención (fix no trivial)

Invoca la skill `pv-internal-workflow` (herramienta Skill) con `action=create`, `type=fix`, el resumen funcional de qué está mal y qué se espera en su lugar, y `promptOriginal` (la petición tal cual la ha escrito el usuario, sin reformular), para que se encargue de numerar el fix y crear `description.md` y `history.md` en `{changesDir}/inProgress/{xxxx}/`.

Si la funcionalidad que se describe incorpora un flujo, una secuencia de pasos/decisiones o una interacción entre estados o componentes desde el punto de vista del usuario (p.ej. cómo transiciona una pantalla, el orden de una operación, casos límite encadenados), invoca (herramienta Skill) la skill de diagramas configurada en `framework.skills.diagrams` de `.claude/pv-context.json` (si no está configurado, `pv-internal-tech-mermaid`), pidiéndole un diagrama de tipo `funcional` por cada caso de uso o historia de usuario distinto que tenga ese flujo — nunca mezcles varios en un mismo diagrama. Incluye el/los diagrama(s) que te devuelva, junto con las notas imprescindibles, al pasárselo a `pv-internal-workflow`, en vez de describirlo solo en prosa — así queda ya así en `description.md`. Usa prosa cuando no haya un flujo/relación clara que representar.

## 4. Generar la propuesta visual (fix no trivial)

Si el cambio tiene componente visual (hay algo que decir en el punto "Definición visual de alto nivel" del paso 1), invoca (herramienta Skill) la skill de maquetas configurada en `framework.skills.mockups` de `.claude/pv-context.json` (si no está configurado, `pv-internal-mockups-html`), pasándole la carpeta destino (`{changesDir}/inProgress/{xxxx}/`) y, por cada elemento visual diferenciado de la propuesta, su descripción y qué debe mostrar (p.ej. un elemento para el modal de selección de mazo, otro para la barra de progreso), marcando la acción como `crear`. Anota las rutas `design_*.html` que te devuelva. Si el cambio no tiene componente visual (lógica interna, datos, backend), omite este paso por completo — no invoques la skill de maquetas "por si acaso".

## 5. Validar la representación visual con el usuario (fix no trivial)

Si el paso 3 incluyó algún diagrama Mermaid o el paso 4 generó algún `design_*.html`, preséntaselos al usuario (ruta de cada `design_*.html` y el diagrama) y pídele que confirme si reflejan el comportamiento esperado o qué cambiaría, antes de encadenar la planificación. Si pide cambios, ajusta y vuelve a presentarlo hasta que lo confirme. Si el fix no generó ningún diagrama ni `design_*.html`, omite este paso.

## 6. Encadenar la planificación (fix no trivial)

Invoca directamente la skill `pv-how` (herramienta Skill) sobre ese mismo `xxxx`, indicando explícitamente que es un fix y que su análisis y solución deben limitarse estrictamente a corregir el bug documentado — cambio mínimo, sin ampliar alcance ni tocar nada no relacionado con la causa raíz. No le pidas al usuario que invoque `pv-how` por separado: continúa tú mismo con ese flujo (análisis → `plan.md` → confirmación → `pv-do` implementa → mueve a `implemented`), tal como lo define `pv-how`.

No escribas tú mismo el documento de fix ni calcules el número `xxxx` — eso lo hace `pv-internal-workflow` para mantener un único sitio con esa lógica. Los ficheros `design_*.html` los genera la skill de maquetas configurada (`pv-internal-mockups-html` por defecto) — no los escribas tú mismo. El código de los diagramas Mermaid del paso 3 lo genera la skill de diagramas configurada (`pv-internal-tech-mermaid` por defecto) — tampoco lo redactes tú mismo. No escribas tú mismo el `plan.md` ni toques código directamente — eso lo hacen `pv-how` y `pv-do` para mantener un único sitio con esa lógica.

## Rama fast-track (cambio trivial, bug o no)

Si el paso 2 concluyó que el cambio es `fast`, sigue estos pasos en vez de los anteriores:

1. **Documentar la intención.** Invoca la skill `pv-internal-workflow` (herramienta Skill) con `action=create`, `type=fast`, el resumen funcional de qué se pide (qué estaba mal o qué texto/valor/estilo se ajusta) y `promptOriginal` (la petición tal cual la ha escrito el usuario, sin reformular), para que numere la entrada y cree `{changesDir}/inProgress/{xxxx}/description.md` y `.../history.md`. Anota el `xxxx` que devuelva.
2. **Aplicar el cambio.** Implementa el cambio directamente en el código con tu proceso normal de ingeniería (editar, verificar que compila/pasan los tests si los hay). Sigue siendo un cambio real sobre el proyecto: aplícalo con el mismo cuidado que cualquier otra edición, aunque no pase por `plan.md`.

   Un cambio `fast` **nunca** debe tocar `docs.tech.architectureDocDir` ni `docs.tech.styleBibleDocDir` (ver paso 2 de arriba) — no los actualices, ni actualices tampoco `docs.functional.featuresDocPathDir`, como parte de esta rama. Si durante la implementación descubres que sí hace falta tocar arquitectura, biblia de estilo, o que el cambio se extiende a más ficheros de los previstos, es señal de que el cambio no era tan trivial: para inmediatamente, no lo apliques a medias (deshaz lo ya tocado si llegaste a tocar algo), y sigue en su lugar el paso 3 (si es un bug) o el aviso + invocación de `pv-new` (si no lo es) descritos en el paso 2 de arriba.
3. **Documentar el cambio ya aplicado.** Añade al `description.md` creado en el punto 1 una nueva sección al final, `## Cambios aplicados`, con el detalle técnico breve de lo tocado (ficheros y qué se cambió en cada uno).
4. **Mover la entrada a `implemented`.** Invoca la skill `pv-internal-workflow` (herramienta Skill) con `action=move`, el `xxxx` del punto 1, `from=inProgress` y `to=implemented` — no muevas la carpeta tú mismo.
5. **Confirmar al usuario.** Indica qué se ha implementado y la ruta del fichero de documentación (`{changesDir}/implemented/{xxxx}/description.md`).
