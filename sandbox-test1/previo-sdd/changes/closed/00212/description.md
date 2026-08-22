- **Name**: Título de componente + sistema de variables de texto
- **Code**: 00212
- **Type**: change
- **Creation date**: 2026-08-15

## Full description

Hoy, los componentes de tipo "Mazo" muestran siempre (en Modo Edición y en Modo Juego, sin poder desactivarse) una etiqueta fija con el número de cartas que contienen. Este cambio sustituye ese mecanismo fijo por una funcionalidad genérica de "Título de componente", disponible para los 8 tipos de componente, configurable desde la sección "Ayuda jugador" de la ventana de propiedades (el mismo bloque donde ya vive "Mostrar tooltip"/"Tooltip").

**Qué se añade en "Ayuda jugador":**

- Un checkbox **"Mostrar título de componente"**: activa o desactiva que aparezca una etiqueta en la parte superior del componente, visible únicamente en Modo Juego (no en Modo Edición).
- Un botón **"Editar título de componente…"** que abre una ventana propia con:
  1. Un cuadro de texto con el contenido del título. Admite el mismo "formato básico" que ya admite "Tooltip" (negrita, cursiva, saltos de línea, listas — se escribe a mano, sin barra de formato).
  2. Selector de color para el texto del título (negro por defecto).
  3. Selector de color para el fondo del título (blanco por defecto), con control de nivel de transparencia del fondo (el texto en sí no lleva transparencia propia).

Cuando "Mostrar título de componente" está activado, la etiqueta aparece pegada a la esquina superior izquierda del componente (por fuera de su borde), con el contenido, colores y transparencia configurados — mismo lugar donde hoy aparece la etiqueta fija de número de cartas del mazo.

**Sistema de variables de texto (nuevo, reutilizable).** Tanto el campo "Título de componente" como el campo "Tooltip" ya existente admiten variables de la forma `{nombre_variable}`, que se sustituyen automáticamente por un valor en tiempo real cuando el componente se muestra en Modo Juego. La primera variable disponible es `{cards_current}`, que se sustituye por el número actual de cartas — solo tiene sentido en un "Mazo" (con este mecanismo, el usuario puede escribir p. ej. `"{cards_current} cartas"` para recuperar el comportamiento equivalente al contador fijo de hoy, pero ahora opcional y con el formato/color que elija). Si se usa una variable que no aplica al tipo de componente actual (p. ej. `{cards_current}` en algo que no es un mazo), el texto se deja tal cual, literal, sin sustituir — no desaparece ni da error.

Este sistema de variables se diseña pensando en variables futuras más allá de `{cards_current}` (para otros tipos de componente), sin necesidad de rediseñarlo cuando se añadan.

**Casos límite y comportamiento:**

- El mazo deja de mostrar el contador de cartas de forma automática/obligatoria: nace con "Mostrar título de componente" desactivado, igual que cualquier otro tipo. Quien quiera recuperar el contador debe activarlo y escribir el texto con la variable `{cards_current}`.
- "Mostrar título de componente" es una propiedad que se hereda de "Grupo" cuando el componente pertenece a uno (igual que "Mostrar tooltip" hoy): si el componente está agrupado, manda el valor del grupo. El contenido, los colores y la transparencia del título siempre son propios del componente, nunca del grupo.
- "Copiar estilo"/"Pegar estilo" (disponible en "Carta") y la sincronización de copias vinculadas incluyen el bloque completo de "Título de componente" (activado/desactivado, texto, colores, transparencia), con el mismo criterio que ya aplica hoy a "Tooltip".
- No se toca el mecanismo de identificación de Modo Edición (la etiqueta que aparece al pasar el ratón con el tipo e id del componente) ni el comportamiento existente de "Tooltip", salvo para añadirle soporte de las nuevas variables de texto.
- No se incluye ningún editor visual/asistido para el formato básico ni para insertar variables (autocompletar, desplegable de variables disponibles...): se escriben a mano, documentadas en el icono de ayuda del campo — igual que ya ocurre hoy con el formato básico de "Tooltip".

**Preguntas de alcance resueltas con el usuario:**

- ¿Se pierde el contador dinámico de cartas del mazo? Sí, como mecanismo automático — se recupera de forma opcional vía el sistema de variables.
- ¿En qué modo(s) se muestra el título? Solo Modo Juego.
- ¿Texto plano o con formato? Mismo formato básico que "Tooltip".
- ¿Dónde se ancla visualmente? Mismo sitio que la etiqueta actual del mazo (fuera del componente, esquina superior izquierda).
- ¿Es override de grupo el checkbox? Sí, igual que "Mostrar tooltip".
- ¿Se incluye en Copiar/Pegar estilo y sincronización de copias? Sí, igual que "Tooltip".
- ¿Qué pasa si una variable no aplica al tipo de componente? Se deja literal, sin sustituir.
- ¿Cómo se llama el campo nuevo? "Título de componente" (explícitamente, para no confundirlo con el título de cabecera de toda la partida, que es un concepto distinto ya existente).

## Technical notes

- **Mecanismo actual a sustituir**: `.mazo-count-label` (`ui/componentRenderer.js`, rama de render de `'mazo'`) — hoy se añade **incondicionalmente** (sin gate de modo ni de configuración), texto `` `${component.id} — ${cartaIds.length} cartas` ``. CSS en `styles/main.css`: `position: absolute; top: -1.6rem; left: 2px; ...` — este es el anclaje a reutilizar/generalizar para el nuevo título. Documentado en `design/docs/architecture/02-component-types.md` (sección `'mazo'`) y `design/docs/style/03-modales-menus.md`.
- **Patrón a replicar de 00208** (`mostrarTooltip`/`tooltipTexto`, ya implementado): campo checkbox a nivel de `core/component.js` (`createComponent`), propagado en `syncCopyWithOriginal`; `mostrarTooltip` SÍ está en `core/group.js` (`createGroup`/`getEffectiveGeneralProps`) como override de grupo, `tooltipTexto` NO (siempre viene de `component.tooltipTexto`, nunca de `effective`). El nuevo `mostrarTitulo` (nombre propuesto) debería seguir el mismo patrón: override de grupo; `tituloTexto`/`tituloColorTexto`/`tituloColorFondo`/`tituloFondoTransparencia` siempre del componente.
- **Sección "Ayuda jugador"** ya existe en `ui/componentModal.js` (fieldset con legend "Ayuda jugador", checkbox+textarea de "Tooltip", helpers de `ui/helpIcon.js`) — el checkbox+botón nuevos van en el mismo fieldset.
- **Patrón de sub-modal ya existente en el proyecto** (operar sobre copia de trabajo, aplicar solo al Aceptar): `ui/boardPatternModal.js`, `ui/cardShapeModal.js`, `ui/cardTextBoxModal.js` — candidatos a replicar para la nueva sub-modal de edición de título (posible nombre: `ui/componentTitleModal.js`).
- **Patrón de color+transparencia ya existente**: `ui/cardShapeModal.js` (`colorFondo`/`colorFondoTransparencia` de `Forma`) — `<input type="color">` + `<input type="range" min="0" max="100">` sincronizado con campo numérico de texto. Mismo patrón aplicable al selector de color de fondo + transparencia del título. El selector de color del texto del título no necesita transparencia (solo `<input type="color">` simple).
- **Sanitizador de HTML básico ya existente**: `sanitizeBasicTooltipHtml` (`ui/componentRenderer.js`, entrada 00208) — reutilizable tal cual para el contenido del nuevo Título (mismo whitelist de etiquetas).
- **Sistema de variables (nuevo)**: no existe ningún mecanismo de sustitución de variables en el proyecto hoy. Diseñar un módulo nuevo (p. ej. `core/textVariables.js`) con una función pura de sustitución (texto + mapa de variables disponibles → texto resultante, dejando literal cualquier `{...}` no presente en el mapa) y una función que, dado un componente, devuelva el mapa de variables disponibles para su tipo (extensible: empieza con `{ cards_current: String(component.properties.cartaIds.length) }` solo si `component.type === 'mazo'`, mapa vacío para el resto). Debe aplicarse tanto al renderizar `tooltipTexto` (extiende 00208, `attachComponentTooltip` en `ui/componentRenderer.js`) como al renderizar el nuevo título — antes de pasar el texto por `sanitizeBasicTooltipHtml`. Al recalcularse en cada render de la mesa (igual que hoy el contador del mazo se recalculaba en cada render), el valor de `{cards_current}` queda siempre actualizado sin necesidad de invalidación especial.
- **Renderizado del título** (Modo Juego, `ui/componentRenderer.js`): mismo criterio que `attachComponentTooltip` de 00208 — no tocar `element.style.position` del componente (ya es `absolute`, sirve de contexto de posicionamiento), añadir el título como hijo posicionado con el mismo anclaje que usa hoy `.mazo-count-label`. A diferencia del tooltip (oculto por CSS hasta `:hover`), el título debe estar **siempre visible** mientras "Mostrar título de componente" esté activo (no depende de hover) — comportamiento más parecido al propio `.mazo-count-label` actual que al nuevo `.component-tooltip`.
- **Eliminar** tras esta entrada: el bloque `countLabel`/`.mazo-count-label` hardcodeado de la rama `'mazo'` en `ui/componentRenderer.js`, y su regla CSS en `styles/main.css` (o reconvertirla en la clase genérica del nuevo título, a decidir en `pv-how`).
- **Documentación a actualizar** (`pv-how`/`pv-do`): `design/docs/architecture/01-component-model.md` (campos nuevos, override de grupo), `design/docs/architecture/02-component-types.md` (quitar mención al contador fijo de `'mazo'`), `design/docs/style/03-modales-menus.md` (nuevo patrón de título, ya no `.mazo-count-label`), y crear la documentación técnica del nuevo sistema de variables (posiblemente un fichero nuevo en `architectureDocDir` si no encaja en ninguno existente).
