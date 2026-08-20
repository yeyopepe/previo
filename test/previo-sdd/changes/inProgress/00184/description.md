- **Name**: Reducir recursos por defecto a un ejemplo por tipo
- **Code**: 00184
- **Type**: change
- **Creation date**: 2026-08-07

## Full description

Al arrancar una partida totalmente nueva (sin ninguna partida guardada previamente), la galería de recursos se rellena hoy automáticamente con 38 recursos de imagen predefinidos: fondos de localización, imágenes de mochila, iconos de objetos y reversos de cartas de evento. Todo ese contenido es específico del juego "Errantes" y viene incluido de fábrica en cualquier partida nueva.

Se quiere sustituir esos 38 recursos por solo 2 recursos de ejemplo genéricos, uno por cada tipo de recurso que admite la galería (imagen y tipografía), de forma que una partida nueva arranque con la galería casi vacía, mostrando únicamente un ejemplo mínimo de cada tipo posible en vez de contenido real del juego:

- **1 recurso de tipo imagen**: una imagen básica nueva, un rectángulo de color sólido con una etiqueta de texto encima (p.ej. "Ejemplo imagen"), que no reutiliza ninguna de las 38 imágenes actuales.
- **1 recurso de tipo tipografía**: una fuente libre, de licencia abierta y de tamaño ligero, incluida solo para mostrar que la galería también admite recursos de tipografía.

### Preguntas de alcance resueltas con el usuario

- **¿"1 de cada tipo" significa 1 por cada categoría de imagen actual (localizaciones, mochila, objetos, eventos) o 1 por cada tipo de recurso del sistema (imagen/tipografía)?** Por tipo de recurso del sistema: el resultado final son solo 2 recursos en total, no uno por cada categoría de imagen actual.
- **¿Se reutiliza alguna de las 38 imágenes actuales como ejemplo?** No. Los 2 recursos de ejemplo son contenido nuevo básico, sin relación con las imágenes actuales del juego.
- **¿Qué aspecto tiene el ejemplo de imagen?** Un rectángulo de color sólido con una etiqueta de texto encima, para que se identifique a simple vista como un placeholder de ejemplo.
- **¿Qué aspecto tiene el ejemplo de tipografía?** Una fuente libre y ligera (de licencia abierta), sin más requisito funcional.
- **¿Afecta a partidas ya guardadas?** No. Esto solo cambia el contenido con el que arranca una sesión totalmente nueva (sin ninguna partida guardada todavía); las partidas ya existentes no se ven afectadas.
- **¿Quién puede usarlo?** No hay restricción de rol: es el contenido con el que arranca cualquier partida nueva, igual que hoy.

### Casos límite

Ninguno relevante más allá del comportamiento ya existente: la galería sigue arrancando siempre con contenido predefinido (antes 38 recursos, ahora 2), sin quedar nunca vacía de partida.

### Sin componente visual nuevo

Este cambio no añade ni modifica ninguna pantalla, modal ni interacción de la galería de recursos — la interfaz de la galería se queda igual que hoy. Lo único que cambia es qué recursos trae de fábrica una partida nueva, así que no aplica maqueta HTML ni diagrama de navegación. Tampoco hay un flujo o secuencia de pasos nuevo que representar como diagrama: es un cambio de contenido de datos, no de lógica ni de orden de una operación.

## Technical notes

- Los 38 recursos actuales viven en `src/data/defaultResources.js` (array `DEFAULT_RESOURCES`), cada uno con `{ id, name, type, fileName, mimeType, dataUrl }`. Se siembran desde `seedDefaultResources()` en `src/main.js` (líneas ~72-78), que recorre el array llamando a `createResource(resourceData)` + `addResource(...)` por cada entrada.
- Tipos soportados por el sistema de recursos: `RESOURCE_TYPES = { IMAGE: 'imagen', FONT: 'tipografia' }`, definido en `src/core/resource.js`, con las extensiones válidas ya mapeadas para cada tipo (imagen: png/jpg/jpeg/gif/svg/webp; tipografía: ttf/otf/woff/woff2).
- Las imágenes actuales están en formato `webp` embebido como `dataUrl` (`data:image/webp;base64,...`). El nuevo recurso de imagen de ejemplo debería seguir el mismo patrón de `dataUrl` embebido — pendiente de decidir en `pv-how` cómo se genera ese base64 (script, asset estático convertido, etc.).
- Punto abierto para `pv-how`: elegir la fuente libre concreta a embeber como ejemplo de tipografía (verificar licencia compatible y tamaño reducido) y el color/tamaño/texto exacto del rectángulo de ejemplo de imagen — solo está decidido el criterio general (color sólido + etiqueta / fuente libre ligera), no el detalle.
- Este cambio solo afecta a la semilla de una sesión nueva: no toca `localStorage` de partidas guardadas, ni los backups en `src/_output/backup/`, ni las builds ya generadas en `src/_output/versions/`. La semilla embebida en `#initial-state` de `src/index.html` está vacía en desarrollo, por lo que en local el efecto se ve simplemente arrancando sin partida guardada.
- Incongruencia detectada para quien retome `changes/inProgress/00080/`: su `description.md` menciona "los 38 [recursos] con los que arranca una partida nueva" en la sección "Ampliación: eliminar recursos no usados en el entregable de solo mesa". Tras implementar esta entrada (00184), ese número deja de ser exacto (pasarán a ser 2) — no afecta a la lógica descrita allí (el criterio "sin trato especial para los recursos por defecto" sigue aplicando igual, sean 38 o 2), pero conviene actualizar la cifra si 00080 se retoma después de 00184.
