---
name: pv-internal-tech-analysis
description: Procedimiento compartido, agnóstico al proyecto, para reunir contexto técnico antes de analizar un change/fix o valorar si un cambio es trivial. Primero lee la documentación técnica configurada en framework.docs.tech (arquitectura, biblia de estilo), y solo si hace falta más información explora el código real. Si el tema toca alguna interfaz o estructura de datos, exige tener su definición completa (firma, entrada, retorno, campos) antes de dar el contexto por reunido, y confirma con el usuario cualquier duda de definición que no se resuelva con documentación o código. Si detecta que el código y la documentación no coinciden, señala el código como fuente de la verdad y devuelve la incongruencia como parte del análisis. Al terminar, contrasta el cambio contra la checklist de seguridad de pv-internal-tech-security y añade sus pendientes al resultado. No edita nada. Uso interno de las skills pv-new, pv-fix e pv-how.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.2
  uses: [pv-internal-tech-security]
---

# pv-internal-tech-analysis

Procedimiento único y compartido para obtener contexto técnico fiable antes de tomar cualquier decisión sobre un change/fix (diseñar una solución, valorar causa raíz, o juzgar si un cambio es lo bastante trivial para el atajo `fast` de `pv-fix`). Solo lo invocan otras skills del framework `pv-*` — no está pensado para invocación directa por el usuario.

**Esta skill no escribe ni edita nada.** Es puramente de análisis/lectura: reúne contexto y, si lo hay, reporta incongruencias entre documentación y código a quien la invoca. Qué hacer con esas incongruencias (actualizar el documento ya mismo, dejarlo anotado para más adelante, o usarlo como motivo para descartar una vía rápida) lo decide siempre la skill llamante, según sus propias reglas. La única excepción a no interactuar por su cuenta es puntual (ver paso 3): si queda una duda de definición que bloquea tener el contexto completo, la confirma directamente con el usuario antes de devolver el resultado.

## Entrada esperada de quien invoca

Quien invoca debe pasar un resumen breve de **qué se está analizando** (el change/fix/duda concreta, no la conversación entera) — se usa para acotar la exploración de código del paso 2, en vez de explorar el repo entero sin rumbo.

## 0. Cargar el contexto del proyecto

Lee `.claude/pv-context.json` en la raíz del repo (si no lo has hecho ya en esta sesión). No valides aquí que el framework está inicializado — eso ya lo ha comprobado la skill llamante antes de invocar esta; si `framework` faltara por completo, limítate a tratar todo `docs.tech` como no configurado y sigue directamente al paso 2 con `sourcecodeDir` (o el repo en general) como única fuente.

## 1. Leer primero la documentación técnica existente

Antes de tocar código, mira `framework.docs.tech` en `.claude/pv-context.json`:

- **Si ya leíste un fichero concreto antes en esta sesión** y no ha cambiado desde entonces, no vuelvas a leerlo — reutiliza lo que ya tienes en contexto. Esta regla se aplica por fichero individual, no al directorio completo: los documentos de `architectureDocDir`/`styleBibleDocDir` son varios ficheros pequeños, así que en un ciclo típico (invocación desde `pv-new`/`pv-fix`, luego otra vez desde `pv-how`) solo hace falta releer `INDEX.md` la segunda vez y comprobar si los ficheros hermanos ya leídos siguen siendo los relevantes — releer solo los que falten, nunca el directorio entero de nuevo. Esto es estrictamente más eficiente que releer un fichero monolítico completo dos veces por ciclo.
- Para cada uno de `architectureDocDir` y `styleBibleDocDir` que esté configurado **y** exista de verdad como carpeta en el repo:
  1. Lee siempre `{dir}/INDEX.md` primero (si no lo tienes ya de esta sesión).
  2. Con el resumen de qué se está analizando (recibido como entrada) y la tabla-índice de `INDEX.md` (qué cubre cada fichero hermano), decide qué ficheros hermanos son relevantes y lee solo esos.
  3. En caso de duda razonable sobre si un fichero es relevante, léelo — mejor pasarse que quedarse corto.
- Los que no estén configurados, o estén configurados pero la carpeta no exista todavía, sáltalos sin más — no es un error, simplemente esa fuente no está disponible.
- Si `framework.docs.tech` no existe en absoluto, o ninguno de los dos campos está configurado, no hay nada que leer en este paso: pasa directamente al paso 2.

Devuelve al usuario la lista de documentos que tienes en `.claude/pv-context.json` y cuáles has encontrado y cuáles no.

Con esto construye un contexto preliminar (arquitectura/capas, convenciones de estilo, mapa de ficheros y símbolos) antes de leer una sola línea de código fuente.

## 2. Completar con código real solo si hace falta

Si el contexto del paso 1 ya resuelve lo que quien invoca necesita saber, no exploraciones código de más. Si falta información (no hay documentación configurada, la que hay no cubre el tema, o quien invoca necesita confirmar un detalle concreto de implementación), explora **solo la parte del código relevante al tema indicado** — usando `framework.sourcecodeDir` como punto de partida si está configurado, o el repo en general si no.

## 3. Completitud de interfaces y estructuras de datos

Si el tema analizado implica alguna **interfaz** (endpoint HTTP, función/método público, evento, mensaje entre componentes, contrato entre capas) o **estructura de datos** (modelo, esquema, tabla, DTO, tipo), el contexto no está completo con un resumen genérico — hace falta la definición exacta:

- **Interfaz**: ruta/nombre exacto, verbo o forma de invocación, cada parámetro de entrada (nombre, tipo, si es obligatorio/opcional), forma completa de la salida/retorno (campos y tipos), y códigos de error o casos de fallo relevantes si los hay.
- **Estructura de datos**: todos sus campos, el tipo de cada uno, restricciones (nulidad, claves, valores por defecto) y relación con otras estructuras, en la medida en que sean relevantes al tema analizado.

Esta es la única excepción a "no explores de más" del paso 2: si lo leído en los pasos 1-2 deja una interfaz o estructura relevante a medias, vuelve a explorar el código puntualmente (o la documentación, si la tiene) hasta tener la definición completa — una descripción aproximada no es contexto suficiente para diseñar sobre ella.

### Dudas que ni la documentación ni el código resuelven

Si tras esto queda una duda genuina de definición (p.ej. qué representa un campo ambiguo, qué formato exacto espera un parámetro, por qué una interfaz tiene una forma que no está documentada ni es evidente por el código) que ni `framework.docs.tech` ni el código aclaran, no la des por buena con una suposición silenciosa: formula la solución que te parezca más razonable y confírmala con el usuario antes de dar el contexto por reunido. Esto aplica solo a dudas puntuales de definición que bloquean tener contexto completo — no a decisiones de diseño de la solución en sí, que siguen siendo responsabilidad de quien invoca esta skill.

## 4. Detectar incongruencias: el código manda

Al leer código durante el paso 2, compara lo que encuentras con lo que decía la documentación leída en el paso 1 (si la había). Si algo no coincide (una capa que ya no funciona como describe algún fichero de `architectureDocDir`, o una convención de `styleBibleDocDir` que el código ya no sigue):

- El código real es siempre la fuente de la verdad, nunca lo que diga el documento.
- No corrijas tú el documento aquí. Añade la incongruencia al resultado que devuelves a quien invoca (ver más abajo) como un cambio de documentación pendiente, para que sea esa skill quien decida cómo y cuándo aplicarlo (p.ej. `pv-how` lo integra en las secciones (c)/(d) de su `plan.md`, que `pv-do` aplicará en su paso de actualización de documentación; `pv-new`/`pv-fix` pueden anotarlo en **Apuntes técnicos**; `pv-fix` puede tomarlo como motivo para no calificar como trivial en su atajo `fast`).

## 5. Contrastar contra la checklist de seguridad

Antes de devolver el resultado, invoca la skill `pv-internal-tech-security` (herramienta Skill) pasándole el resumen de qué se está analizando (la misma entrada recibida) y el contexto ya reunido en los pasos 1-4. Esa skill no explora nada por su cuenta ni decide diseño: solo contrasta el cambio contra su checklist de categorías de seguridad y devuelve cuáles son aplicables y, de esas, cuáles quedan pendientes de revisar.

Este paso se ejecuta siempre, no solo cuando el tema analizado "suene" a seguridad — cambios aparentemente ajenos (UI, textos, configuración) pueden tocar de refilón una categoría de la checklist (p.ej. un formulario nuevo que sí implica validación de entrada). Es la propia `pv-internal-tech-security` quien decide qué categorías aplican, no esta skill.

## 6. Devolver el resultado a quien invoca

No redactes ningún fichero. Devuelve a la skill llamante, en el mismo turno:

- **Contexto reunido** — el resumen relevante para el tema indicado, ya sintetizado (no pegues los documentos enteros ni el código tal cual), incluyendo la definición completa de cualquier interfaz o estructura de datos relevante del paso 3.
- **Incongruencias detectadas** — lista (vacía si no hay ninguna) con, por cada una: qué documento la contiene, qué decía, qué muestra el código realmente, y el cambio de documentación sugerido.
- **Puntos de seguridad pendientes** — la lista de "Categorías pendientes de revisar" devuelta por `pv-internal-tech-security` en el paso 5 (vacía si no hay ninguna). No incluyas aquí las categorías que esa skill haya marcado como ya cubiertas — esas no necesitan acción de quien invoca.

Quien invoca decide qué hacer con cada incongruencia y con cada punto de seguridad pendiente (resolverlo con el usuario, anotarlo en `plan.md`, usarlo como motivo para no calificar de trivial); esta skill no vuelve a intervenir sobre eso.
