- **Name**: Profundidad/extrusión configurable para todos los componentes
- **Code**: 00210
- **Type**: change
- **Creation date**: 2026-08-15

## Full description

Se añade una propiedad nueva, disponible para cualquier tipo de componente (tablero, carta, dado, mazo, token, texto, etc.), que permite darle una apariencia de "extrusión" o profundidad: como si el componente tuviera un grosor real y no fuera un elemento totalmente plano. El tamaño de esa profundidad es configurable por quien edita el componente, en píxeles, con `0` como valor por defecto (sin ningún cambio respecto al aspecto actual).

El efecto debe leerse como un cuerpo sólido con grosor real (un bloque con un lateral visible), no como una sombra difusa proyectada — es una distinción explícita pedida por el usuario tras ver que la técnica de profundidad que ya usa hoy el componente "Dado" (una copia de su silueta desplazada y sombreada) se percibe como "solo una sombra".

### Dónde se configura — nueva pestaña "Visuales"

La edición de un componente gana una pestaña nueva, **"Visuales"**, insertada entre "Generales" y "Específicas" (el resto de pestañas ya existentes, incluida "Copias" para componentes con copias vinculadas, no cambian). La nueva pestaña agrupa todo lo que afecta al aspecto del componente, reorganizando controles que hoy están repartidos entre "Generales" y "Específicas":

- **Tamaño** (campos "Alto"/"Ancho" y checkbox "Mantener proporción"): se traslada tal cual desde "Generales" — deja de estar ahí. Se aplica a los 8 tipos por igual, como hoy.
- **Profundidad y Color de extrusión** (lo nuevo de este cambio): una fila con dos campos — "Profundidad" (número, en píxeles, mínimo `0`) y "Color de extrusión" (selector de color, con el cálculo automático por defecto si no se toca). Se aplica a los 8 tipos por igual (sin efecto visible en "Texto", ver más abajo).
- **Controles visuales específicos por tipo** que hoy viven dentro de "Específicas" (p. ej. "Biselado en el borde"/"Sombra" de "Tablero simple"/"Tablero personalizado", color y grosor del borde del tablero, "Esquinas redondeadas" de "Carta", forma circular de "Mazo", y cualquier otro control agrupado hoy bajo una sección "Visual" dentro de las propiedades específicas de un tipo): se trasladan también a "Visuales", dejando en "Específicas" solo lo que no es puramente visual (contenido de texto, resultados de dado, contenido de mazo, imágenes de fondo, etc.).

**"Específicas" sin nada que mostrar**: si tras este traslado un tipo de componente se queda sin ninguna propiedad no-visual que configurar en su pestaña "Específicas", esa pestaña muestra el mensaje "Este objeto no tiene propiedades" en vez de quedar en blanco sin explicación. "Visuales", en cambio, siempre tiene contenido (Tamaño y Profundidad/Color de extrusión están presentes en los 8 tipos), así que nunca muestra ese mensaje.

### Alcance y casos particulares

- **Aplica a los 8 tipos de componente por igual**, sin necesidad de configuración específica por tipo.
- **Excepción — tipo "Texto"**: al no tener caja ni fondo (solo el propio texto), esta propiedad no tiene ningún efecto visible en este tipo.
- **Componente "Dado"**: hoy ya simula profundidad con un mecanismo propio y fijo (no configurable). Este cambio lo sustituye por la nueva propiedad general y su técnica sólida — deja de tener un mecanismo aparte. El valor por defecto de "Dado" se ajusta para mantener una sensación de profundidad similar a la actual, pero con el aspecto sólido nuevo en vez del aspecto de sombra actual.
- **Convive sin conflicto** con el bisel de "Tablero simple"/"Tablero personalizado" y con la sombra de contacto que ya tienen las piezas de juego — un componente puede combinar extrusión, bisel y sombra a la vez, sin que unas sustituyan a las otras.
- **Puramente visual**: no cambia la posición, el tamaño lógico ni el área de arrastre/click del componente. El efecto puede sobresalir visualmente del contorno nominal del componente (igual que ya ocurre hoy con "Dado").
- **Límite máximo**: pendiente de confirmar un tope razonable (propuesta inicial: 40px) tras validar el aspecto con los mockups, para evitar que un valor desproporcionado rompa la lectura visual del componente.
- **Color de la parte extruida**: configurable de forma independiente al tamaño. Por defecto se calcula automáticamente como un tono más oscuro del color propio del componente (igual que hoy hace `'dado'`/el bisel), pero el usuario puede elegir un color propio distinto para la extrusión desde la misma pestaña "Visuales", junto al campo de profundidad.
- **Reorganización de pestañas**: la modal de edición de componente gana la pestaña "Visuales" entre "Generales" y "Específicas" (las demás pestañas existentes no cambian). Ver detalle en "Dónde se configura" más arriba.
- **"Texto" y su color de fondo**: aunque este tipo tiene una propiedad de color de fondo configurable (con opción de transparencia), la extrusión sigue sin tener efecto visible en "Texto" en ningún caso — decisión explícita para mantener el comportamiento simple y predecible, sin una regla condicionada al estado de otra propiedad.

### Preguntas de alcance resueltas con el usuario

| Punto | Resuelto |
|---|---|
| ¿Campo general o específico por tipo? | General, a nivel de componente (como Bloqueado/Oculto) |
| ¿Cómo se ve el efecto? | Debe leerse como cuerpo sólido con grosor, no como sombra — corrección explícita del usuario tras ver que el mecanismo actual de "Dado" parece solo una sombra |
| ¿Qué pasa con "Dado", que ya simula profundidad? | Se unifica: pasa a usar esta misma propiedad y la técnica sólida nueva, sustituyendo su mecanismo actual |
| ¿Convive con bisel/sombra existentes? | Sí, capas independientes y compatibles |
| ¿Afecta a "Texto"? | No tiene efecto visible en ese tipo |
| ¿Afecta a posición/tamaño lógico/área de interacción? | No, puramente cosmético |
| ¿Límite máximo de profundidad? | Propuesta 40px, a confirmar tras revisar mockups |
| ¿Se puede elegir el color de la parte extruida? | Sí, campo de color independiente, junto al de profundidad — por defecto se calcula automáticamente (tono más oscuro del color propio) |
| ¿Dónde vive la extrusión y el resto de controles visuales? | Nueva pestaña "Visuales" (antes eran solo "Generales"/"Específicas") — agrupa Tamaño (trasladado desde Generales), Profundidad/Color de extrusión, y los controles visuales específicos por tipo que hoy están dentro de "Específicas" (bisel, sombra, borde, esquinas redondeadas, forma...) |
| ¿Qué pasa si "Específicas" se queda sin nada tras mover lo visual? | Muestra "Este objeto no tiene propiedades" en vez de quedar vacía sin explicación. "Visuales" nunca muestra ese mensaje (Tamaño/Extrusión siempre presentes) |

## Technical notes

- Modelo de componente: dos campos generales nuevos a nivel raíz (junto a `bloqueado`, `oculto`, `mostrarTooltip`...), no dentro de `properties`: profundidad (número, px) y color de extrusión (string color, o `null`/ausente = cálculo automático por `shadeColor`). Ver `design/docs/architecture/01-component-model.md`.
- Patrón de UI a reutilizar para el campo doble profundidad+color: `ui/componentModal.js` ya tiene el patrón "color + campo asociado, misma fila" documentado en `design/docs/style/INDEX.md` §8 ("Campo de color + grosor asociado, misma fila") — ejemplo de referencia: sección "Borde" del tablero (`borderRow`/`borderColorField`/`borderWidthField`, `componentModal.js` ~L1052-1090), `div.modal__field` exterior con `display:flex; gap:0.5rem` y dos sub-`div` `flex:1`. El nuevo campo replica exactamente esta estructura.
- Checklist a revisar al tocar un campo transversal nuevo (`design/docs/architecture/INDEX.md` §8): persistencia (`core/persistence.js`, `core/fileExport.js`, suscripción de autoguardado), renderizado (`ui/componentRenderer.js`), `getComponentsBounds`, ficheros de prueba (`src/test/*.json`).
- Migración: ausencia del campo en un guardado antiguo debe comportarse como `0` (sin efecto), mismo criterio que `mostrarTooltip`/`oculto`/`subirAlMoverInteractuar` (sin migración explícita necesaria).
- Técnica actual de profundidad a sustituir/unificar: `'dado'` (`ui/componentRenderer.js`, `renderDiceSilhouette`) — copia de la silueta en tono oscuro (`shadeColor`, `core/colorUtils.js`) desplazada detrás. Pasa a usarse la nueva técnica sólida (capas apiladas de sombra dura sin blur, o mecanismo equivalente que dé aspecto de bloque opaco) tanto para `'dado'` como para el resto de tipos.
- Documentación de estilo a actualizar en su momento (`design/docs/style/INDEX.md`, sección "Bisel/profundidad" y `01-tokens-visual.md` §6 "Elevación, sombra y transición"): no hay hoy ningún token ni sistema documentado para esta nueva propiedad — `pv-how` deberá definir cómo se integra con el sistema de elevación existente (3 niveles de sombra) sin confundirlo conceptualmente con él.
- Sin incongruencias detectadas entre documentación técnica y código durante el análisis (`pv-internal-tech-analysis`). Documentos revisados: `design/docs/architecture/INDEX.md`, `01-component-model.md`; `design/docs/style/INDEX.md`, `01-tokens-visual.md`.
- Reorganización de pestañas (`ui/componentModal.js`): hoy son dos (`createTab('general', 'Generales')`, `createTab('specific', 'Específicas')` — nombres orientativos, ver código real). La sección "Tamaño" (`sizeSection`, `heightField`/`widthField`/`keepRatioField`, ~L327-385) vive hoy dentro del contenido de "Generales" (`generalContent`) y debe moverse al contenido de la nueva pestaña "Visuales". Los controles visuales específicos por tipo a trasladar incluyen, entre otros ya documentados en `design/docs/style/INDEX.md` (sección "Bisel/profundidad" y "Esquinas redondeadas de Carta"): checkbox "Biselado en el borde" (`biseladoField`, aparece dos veces en el fichero, ~L1004 y ~L1453, una por tipo tablero), checkbox "Sombra" (`sombraField`, ~L1022 y ~L1470), fila "Color del borde"/"Grosor" (`borderRow`, ~L1052-1090), checkbox "Esquinas redondeadas" de `'carta'`, selector de forma circular de `'mazo'`. `pv-how` debe enumerar la lista exacta y exhaustiva de qué se mueve por tipo al diseñar la solución — esta lista es orientativa, basada en lo ya visto en el análisis funcional, no exhaustiva.
- Mensaje "Este objeto no tiene propiedades": no existe hoy ningún fallback para pestaña de propiedades específicas vacía (no se ha detectado ningún tipo actual que quede sin nada tras el traslado, pero `pv-how` debe confirmarlo recorriendo los 8 tipos en `02-component-types.md` antes de dar por hecho que el mensaje llega a activarse con el catálogo actual).
