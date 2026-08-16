---
name: pv-new
description: Analiza y documenta un cambio intencionado (nueva funcionalidad o modificación de comportamiento existente, no un bug) pedido por el usuario, dejándolo listo en {changesDir}/inProgress para planificar e implementar después con pv-how. Si se indica un código ya en inProgress, amplía esa entrada en vez de crear una nueva. Con `/pv-new todo <código>` parte de una idea ya apuntada en {changesDir}/todo/ en vez de una petición nueva, y borra esa idea automáticamente al terminar (sin pedir confirmación). Trigger: /pv-new [xxxx], o cuando el usuario pide explícitamente "un change"/"documentar este cambio" como parte del flujo de trabajo del proyecto.
argument-hint: "[xxxx | todo <código>] <descripción del cambio>"
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.0
  uses: [pv-internal-workflow, pv-internal-tech-analysis, pv-internal-mockups-html, pv-internal-tech-mermaid, pv-how]
---

# pv-new

Analiza y documenta un cambio intencionado sobre el proyecto (funcionalidad nueva o modificación de comportamiento existente a propósito — para bugs usa la skill `pv-fix`, no esta). Parte del framework `pv-*`.

**No implementa nada.** Esta skill solo entiende y documenta el alcance funcional de lo que se pide; la solución técnica la hace después la skill `pv-how`, y la implementación la skill `pv-do`, cuando se decida planificar/implementar esta entrada.

**Los mockups y diagramas son el eje central de la definición de un cambio, no un añadido opcional.** Siempre que el cambio lo permita, su intención debe quedar fijada mediante una representación visual — no solo prosa — antes de darla por documentada, y esa representación debe quedar **validada por el usuario**, no solo generada. Hay cuatro casos válidos, y no son excluyentes entre sí dentro de un mismo cambio:
- **Flujos o funcionamiento nuevos/modificados, sin dimensión de UI** (lógica, orden de una operación, decisiones, casos límite encadenados): diagrama Mermaid funcional dentro de `description.md` (paso 2) — uno por cada caso de uso o historia de usuario distinto, nunca varios mezclados en el mismo diagrama.
- **Cambios visuales o de estilo** (aparece o se modifica algo que el usuario ve/toca en pantalla): maqueta(s) HTML (`design_*.html`, paso 3).
- **Navegación o interacción de UI** (cambia de pantalla, se abre un modal o un desplegable, o cualquier transición de estado visual disparada por una acción del usuario, aunque no salga de una sola pantalla): diagrama de navegación (`design_navigation_*.md`, paso 3).
- **Datos con estructura propia** (el cambio define o usa algo que necesita una lista de propiedades o datos asociados — propiedades de un objeto, contenido de una tabla, campos de una configuración, etc.): tabla(s) de datos (`design_data_*.md`, paso 3.1).

Solo prescinde de los cuatro cuando el cambio no tenga de verdad ninguna dimensión visual, de flujo ni de datos estructurados representable — no por defecto ni por ahorrar el paso.

**`description.md` vs `history.md`.** `description.md` recoge únicamente el resultado vigente del análisis (qué se pide, cómo debe comportarse) — nunca el prompt original del usuario ni ninguna otra traza de cómo se llegó ahí. Esa traza vive aparte, en `history.md` (ver paso 2), un fichero de uso exclusivo de `pv-new`/`pv-fix`: el resto de skills del framework (`pv-how`, `pv-do`, etc.) no lo leen ni lo necesitan, y los prompts que contiene pueden ser incompletos o contradictorios entre sí sin que eso sea un problema — son historial de un proceso de análisis, no la fuente de la verdad.

**Fuente de la verdad.** Al anticipar dudas y proponer respuestas (paso 1), la única fuente de verdad sobre cómo funciona hoy el proyecto es la documentación técnica y el código real — nunca asunciones, ni lo que se recuerde de conversaciones anteriores, ni lo que el usuario crea que hace el código. Para reunir ese contexto, invoca la skill `pv-internal-tech-analysis` (herramienta Skill) pasándole un resumen de lo que se está analizando, en vez de leer tú mismo `framework.docs.tech` o explorar el código a ciegas: ella se encarga de leer primero la documentación técnica configurada y de explorar código solo si hace falta, y te devuelve el contexto reunido y cualquier incongruencia entre documentación y código que detecte (recuerda: en ese caso el código manda, no la documentación). Si detecta alguna incongruencia, anótala en **Apuntes técnicos** al documentar (paso 2) para que `pv-how` la tenga en cuenta más adelante. Tampoco cuenta como fuente de verdad el contenido de otros cambios/fixes que existan bajo `{changesDir}/**` (su `description.md` o `plan.md`, estén en `inProgress`, `implemented` o `closed`): son intención o análisis de otra entrada, no el estado real del proyecto. Consúltalos antes de dar por buena una propuesta sobre convivencia con lo existente.

## 0. Comprobar que el framework está inicializado

Si `.claude/pv-context.json` no existe en la raíz del repo, o le falta la
sección `framework` (o campos suyos necesarios), no continúes: dile al
usuario que primero debe ejecutar la skill `pv-init` para
inicializar/completar el framework en este proyecto, y detente ahí.

```
Este proyecto todavía no tiene el framework `pv-*` inicializado (o le falta configuración). Ejecuta primero `/pv-init` antes de volver a invocarme.
```

## 0.1 Comprobar si el código indicado ya está en curso

Si el usuario, al invocar esta skill, indica un código de cambio/fix (`xxxx`) — p.ej. `/pv-new 0001 ...` o "añade esto al cambio 0001" — comprueba si existe esa carpeta **exactamente** en `{changesDir}/inProgress/{xxxx}/`.

- **Si existe y el usuario te da información nueva**: no es un cambio nuevo, sino una ampliación de esa entrada ya en curso. Lee y sigue completo [`extend-entry.md`](extend-entry.md) de esta misma carpeta — no sigas con los pasos de más abajo.
- **Si existe, pero el usuario no te está añadiendo información nueva**: significa que debes revisar y reanalizar el cambio. Posibles causas:
   - Hace mucho tiempo que se escribió el fichero `description.md` y pueden haber funcionalidades nuevas ya implementadas.
   - El usuario puede haber editado `description.md` a mano e introducido cambios.
- **Si no existe** (esté o no ese `xxxx` en `implemented`/`closed`, o no exista en ningún sitio): es un cambio nuevo con un código nuevo. Continúa con el proceso habitual desde el paso 1, ignorando el código indicado — el `xxxx` real lo calculará `pv-internal-workflow`, no lo asumas tú.
- Si no se ha indicado ningún código, continúa igualmente con el proceso habitual desde el paso 1.

## 0.2 Comprobar si se invoca a partir de una idea de `todo/`

Si el usuario invoca esta skill como `/pv-new todo <código>` (o pide explícitamente "convierte la idea `<código>` de todo en un change"), esta entrada no nace de una petición nueva del usuario en el chat, sino del contenido ya apuntado por `pv-todo`: lee y sigue completo [`todo-mode.md`](todo-mode.md) de esta misma carpeta antes de continuar.

Si no se invocó así, sigue con el proceso habitual desde el paso 1 de "Pasos".

## Pasos

1. **Entender el alcance y anticipar las dudas funcionales habituales.** No esperes a que surja una ambigüedad evidente: antes de documentar, revisa la petición y el código relevante del proyecto para construir tú mismo una lista de los puntos que habitualmente quedan indefinidos en este tipo de cambios. Repasa al menos:
   - **Casos límite y estados**: qué pasa en vacío, en error, durante la carga, si se cancela a medias.
   - **Convivencia con lo existente**: si esto sustituye, complementa o entra en conflicto con funcionalidad ya presente en el proyecto.
   - **Alcance de los datos**: si algo se guarda, dónde y para quién (si el proyecto distingue usuarios/partidas/sesiones); qué pasa al recargar o en otra sesión.
   - **Quién puede usarlo**: si el proyecto tiene roles o modos que restringen la acción.
   - **Definición visual de alto nivel**: qué elementos nuevos aparecen, en qué zona aproximada de la pantalla se ubican, cómo se activan/desactivan, qué feedback visual percibe el usuario al interactuar. Queda fuera de este análisis el detalle de bajo nivel (colores exactos, medidas, componentes concretos a reutilizar o crear) — eso lo resuelve `pv-how` al planificar la solución técnica.

   Para cada punto relevante para este cambio concreto, no se lo devuelvas en bruto al usuario: propón tú una respuesta razonable a partir del contexto del proyecto y preséntale la lista completa (punto + tu propuesta) de una sola vez para que la confirme o corrija donde no esté de acuerdo, en vez de preguntar uno a uno. Si hay algún punto sobre el que no puedas ni siquiera proponer una asunción razonable, márcalo explícitamente como pregunta abierta dentro de esa misma lista.
2. **Documentar la intención.** Invoca la skill `pv-internal-workflow` (herramienta Skill) con `action=create`, `type=change`, el resumen funcional de lo que se pide — incluyendo la lista de dudas del paso 1 ya resuelta (propuestas confirmadas, correcciones del usuario y, en su caso, definición visual de alto nivel acordada) — y `promptOriginal` (la petición tal cual la ha escrito el usuario, sin reformular), para que se encargue de numerar el cambio y crear `description.md` y `history.md` en `{changesDir}/inProgress/{xxxx}/`. Anota el `xxxx` que te devuelva: lo necesitas en el paso siguiente.

   Si la funcionalidad que se describe incorpora un flujo, una secuencia de pasos/decisiones o una interacción entre estados o componentes desde el punto de vista del usuario (p.ej. cómo transiciona una pantalla, el orden de una operación, casos límite encadenados), invoca (herramienta Skill) la skill de diagramas configurada en `framework.skills.diagrams` de `.claude/pv-context.json` (si no está configurado, `pv-internal-tech-mermaid`), pidiéndole un diagrama de tipo `funcional` por cada caso de uso o historia de usuario distinto que tenga ese flujo — nunca mezcles varios en un mismo diagrama. Incluye el/los diagrama(s) que te devuelva, junto con las notas imprescindibles, al pasárselo a `pv-internal-workflow`, en vez de describirlo solo en prosa — así queda ya así en `description.md`. Usa prosa cuando no haya un flujo/relación clara que representar.
3. **Generar la propuesta visual y el diagrama de navegación.** Si el cambio tiene componente visual (hay algo que decir en el punto "Definición visual de alto nivel" del paso 1):
   - **Maquetas HTML.** Invoca (herramienta Skill) la skill de maquetas configurada en `framework.skills.mockups` de `.claude/pv-context.json` (si no está configurado, `pv-internal-mockups-html`), pasándole la carpeta destino (`{changesDir}/inProgress/{xxxx}/`) y, por cada elemento visual diferenciado de la propuesta, su descripción y qué debe mostrar (p.ej. un elemento para el modal de selección de mazo, otro para la barra de progreso), marcando la acción como `crear`. Solo la invoques cuando haya de verdad al menos un elemento que maquetar — nunca "por si acaso". Anota las rutas `design_*.html` que te devuelva.
   - **Diagrama de navegación.** Si además el cambio introduce o modifica navegación o interacción de UI (cambio de pantalla, apertura de un modal o desplegable, o cualquier transición de estado visual disparada por una acción del usuario, aunque no salga de una sola pantalla):
     1. **Enumera primero los casos de uso, antes de dibujar nada — y escribe esa lista como texto de salida al usuario, no solo como paso mental interno.** Antes de crear ningún fichero `design_navigation_*.md`, publica en tu propia respuesta la lista numerada de los flujos distintos que vas a representar (p.ej. "cómo cambia la selección al hacer click/arrastrar" y "qué ofrece el menú contextual según la selección activa" son dos casos de uso distintos, aunque compartan pantalla y estén relacionados). Dos acciones del usuario pertenecen al mismo caso de uso solo si responden a la misma pregunta ("¿cómo navego entre pantallas/estados?"); si una responde a "¿qué opciones ofrece esta interacción según el contexto?" es un caso de uso aparte, aunque su resultado final sea un estado ya representado en el otro. Convertir este paso en un texto visible (en vez de resolverlo solo "en la cabeza") es intencional: si al escribir un diagrama te encuentras mezclando acciones que responden a preguntas distintas, es la señal de que esta lista se saltó o quedó incompleta — vuelve a ella antes de seguir.
     2. **Crea un fichero `design_navigation_<descripción>.md` por cada entrada de esa lista**, directamente en `{changesDir}/inProgress/{xxxx}/` — nunca mezcles dos casos de uso en el mismo diagrama, aunque para eso un fichero tenga que referenciar un estado/nodo de otro (p.ej. "la acción X deja la navegación en el estado Y — ver fichero Z") en vez de repetir su lógica interna. El número de ficheros debe coincidir exactamente con el número de entradas de la lista publicada en el paso anterior.

   Si el cambio no tiene componente visual, omite este paso por completo — ni invoques la skill de maquetas ni crees ficheros `design_navigation_*.md` de relleno.

   Cada fichero `design_navigation_*.md` combina un diagrama Mermaid (`stateDiagram-v2` o `flowchart`, el que mejor represente ese caso de uso concreto) con las pantallas/estados de UI relevantes como nodos y las acciones del usuario como transiciones, más notas breves en prosa solo para las transiciones que no queden claras con el propio diagrama — no repitas en texto lo que el diagrama ya deja claro.
3.1 **Definir los datos necesarios.** Si el cambio define o usa algo que necesita una lista de propiedades o datos asociados (propiedades de un objeto, contenido de una tabla de base de datos, campos de una configuración, etc.), escribe uno o varios ficheros `design_data_<descripción>.md` directamente en `{changesDir}/inProgress/{xxxx}/` — uno por cada entidad o conjunto de datos claramente diferenciado, nunca mezcles entidades sin relación en el mismo fichero. Cada fichero contiene una o varias tablas Markdown que enumeran esos datos (columnas orientativas: nombre del dato, descripción funcional, obligatoriedad/valores posibles según aplique — ajusta las columnas a lo que aporte información real en cada caso). Es **una definición funcional de qué datos hacen falta**, no de cómo se guardan o manipulan: nada de tipos de columna de base de datos, motores de persistencia, nombres de tabla/API o cualquier otra decisión técnica — eso lo decide `pv-how` después a partir de esta tabla. Si el cambio no necesita ninguna lista de propiedades o datos estructurados, omite este paso por completo.
4. **Validar la representación visual con el usuario.** Si el paso 2 incluyó algún diagrama Mermaid, o los pasos 3/3.1 generaron algún `design_*.html`, `design_navigation_*.md` o `design_data_*.md`, no los des por buenos solo porque se hayan escrito: preséntaselos al usuario (indícale la ruta de cada `design_*.html`/`design_navigation_*.md`/`design_data_*.md` para que lo abra o revise, y muestra los diagramas Mermaid) y pídele que confirme si reflejan lo que tenía en mente o qué cambiaría.

   ```
   La propuesta visual queda en {rutas de los design_*.html}, la navegación en {rutas de los design_navigation_*.md}, los datos necesarios en {rutas de los design_data_*.md} y el flujo como diagrama en description.md. ¿Reflejan lo que tenías en mente, o hay algo que cambiar antes de seguir?
   ```

   Si pide cambios, ajusta el/los fichero(s) o el diagrama y vuelve a presentarlo hasta que lo confirme. Si el cambio no generó ningún diagrama, `design_*.html`, `design_navigation_*.md` ni `design_data_*.md` (pasos 1/3.1 no encontraron dimensión visual, de flujo ni de datos), omite este paso.
5. **Indicar el siguiente paso.** Informa al usuario de que el cambio queda documentado (`description.md`) y, si procede, con su propuesta visual y de datos ya validada (`design_*.html`, `design_navigation_*.md`, `design_data_*.md`); para planificarlo e implementarlo debe invocar la skill `pv-how` sobre ese `xxxx`. Si el usuario quiere implementarlo ya mismo, puedes invocar `pv-how` directamente tú.

No escribas tú mismo el documento de cambio ni calcules el número `xxxx` — eso lo hace `pv-internal-workflow` para mantener un único sitio con esa lógica. Los ficheros `design_*.html` los genera la skill de maquetas configurada (`pv-internal-mockups-html` por defecto) — no los escribas tú mismo. El código de los diagramas Mermaid del paso 2 lo genera la skill de diagramas configurada (`pv-internal-tech-mermaid` por defecto) — tampoco lo redactes tú mismo. Los ficheros `design_navigation_*.md` y `design_data_*.md`, en cambio, sí los escribes tú directamente: no son responsabilidad de ninguna skill interna, que son agnósticas al proyecto y no analizan ni diseñan nada.

## Ampliar una entrada ya en `inProgress`

Cuando el paso 0.1 detecta que el `xxxx` indicado ya existe en `{changesDir}/inProgress/{xxxx}/`, no se crea una entrada nueva: se amplía la que ya hay. Procedimiento completo en [`extend-entry.md`](extend-entry.md) de esta misma carpeta.
