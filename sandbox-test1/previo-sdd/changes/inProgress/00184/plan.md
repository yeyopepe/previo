- **Creation date**: 2026-08-07
- **Risk**: [pending recalculation]

## (a) Functional notes

**Out of scope:** no se toca la carpeta de assets fuente `src/resources/img/` (art original del juego: localizaciones, mochila, objetos, eventos, y otras piezas de arte conceptual). Esa carpeta es el repositorio de arte fuente del proyecto, no el contenido embebido en `defaultResources.js`, y contiene bastante más material del que llegó a usarse en los 38 recursos actuales — borrarla no forma parte de esta entrada. Tampoco se toca ningún backup en `src/_output/backup/` ni ninguna build ya generada en `src/_output/versions/`.

**Doubts resolved with the user:** ya recogidas en `description.md` (1 recurso de tipo "imagen" + 1 de tipo "tipografía", sin reutilizar ninguna de las 38 imágenes actuales, contenido nuevo básico). Dudas técnicas adicionales resueltas durante este análisis (sin necesidad de volver a preguntar al usuario, son detalles de implementación):

- **¿Cómo se genera la imagen de ejemplo?** Con Pillow (ya disponible en el entorno), dibujando un cuadrado de color sólido con borde y una etiqueta de texto centrada, exportado a WebP y embebido como `dataUrl` — mismo formato que las 38 imágenes actuales.
- **¿Qué fuente libre se usa para el ejemplo de tipografía?** `Actor-Regular.ttf` (Google Fonts, licencia SIL Open Font License — libre y con atribución no obligatoria más allá de conservar el aviso de licencia), ~63 KB, uno de los ficheros de fuente estática más ligeros del catálogo OFL de Google Fonts. Se descarga en el momento de implementar desde `https://raw.githubusercontent.com/google/fonts/main/ofl/actor/Actor-Regular.ttf` (repo oficial de Google Fonts) y se embebe igual que las imágenes.
- **¿Qué colores/tamaño usa la imagen de ejemplo?** Se reutilizan tokens ya existentes de la Style Bible (`design/docs/style/01-tokens-visual.md`) en vez de inventar un color nuevo: fondo `--accent-blue-light` (`#eaf3fc`), borde y texto `--accent-blue` (`#2c7dd8`). Tamaño 512×512 px (cuadrado, compatible con el uso típico de una imagen de recurso en carta/ficha/tablero).

## (b) Technical solution

1. [x] **Generar el `dataUrl` de la imagen de ejemplo (paso de implementación, no deja fichero nuevo en el repo salvo el resultado embebido).** Con un script Python puntual (Pillow), crear una imagen de 512×512 px: fondo `#eaf3fc`, borde de 6 px en `#2c7dd8`, texto centrado "Ejemplo imagen" en `#2c7dd8` (fuente por defecto de Pillow, ya que esta imagen es solo un placeholder visual, no necesita tipografía embebida). Exportar a WebP (`Image.save(..., format="WEBP", quality=92)`, mismo criterio de calidad que ya usa `core/imageConversion.js` al convertir imágenes subidas) y codificar el resultado en base64 para construir `data:image/webp;base64,<...>`.
2. [x] **Descargar y codificar la tipografía de ejemplo.** Descargar `Actor-Regular.ttf` desde `https://raw.githubusercontent.com/google/fonts/main/ofl/actor/Actor-Regular.ttf` y codificarlo en base64 para construir `data:font/ttf;base64,<...>`.
3. [x] **`src/data/defaultResources.js` — sustituir `DEFAULT_RESOURCES`.** Reemplazar el array completo (hoy 38 entradas) por estas 2:
   ```js
   export const DEFAULT_RESOURCES = [
     {
       id: "example-image",
       name: "Ejemplo imagen",
       type: "imagen",
       fileName: "example-image.webp",
       mimeType: "image/webp",
       dataUrl: "data:image/webp;base64,<generado en la tarea 1>",
     },
     {
       id: "example-font",
       name: "Ejemplo tipografía",
       type: "tipografia",
       fileName: "example-font.ttf",
       mimeType: "font/ttf",
       dataUrl: "data:font/ttf;base64,<generado en la tarea 2>",
     },
   ];
   ```
   Mantener el comentario de cabecera del fichero (explica ya correctamente el propósito general — sembrado en sesión nueva, id fijo en vez de UUID), sin cambios de fondo.
4. [x] **Comprobar que no queda ninguna referencia a los ids antiguos.** Ya verificado durante el análisis: ningún otro fichero de `src/` referencia por id ninguno de los 38 recursos actuales (`localization-main-back`, `backpack_front_adult`, etc.) — no hace falta tocar nada más en el código fuente. Reverificado en implementación con `grep` sobre `src/**/*.js`: sin coincidencias.

No se borra la carpeta `src/resources/img/` (ver "Fuera de alcance").

## (c) Architecture changes

`design/docs/architecture/03-groups-resources.md`, párrafo final de la sección "Modelo de datos de recurso (galería)" (empieza con `` `data/defaultResources.js` exporta `DEFAULT_RESOURCES`: 38 recursos con los que arranca... ``): actualizar para reflejar que ahora son 2 recursos de ejemplo (1 imagen + 1 tipografía) en vez de 38 imágenes específicas del juego, y quitar el desglose de conteos por categoría (3 fondos de localización, 3 de mochila, 25 de objetos, 7 de eventos) y la referencia a `src/resources/img/{backpack,objects,events}/` como origen de esas 38 imágenes concretas — el resto del párrafo (id fijo y legible, formato WebP, `backfillDefaultResourcesIfNeeded()` para saves antiguos) sigue aplicando igual y no cambia.

## (e) Verification

1. [x] Arrancar la app sin ninguna partida guardada (`localStorage` vacío): la galería de recursos debe mostrar exactamente 2 recursos — "Ejemplo imagen" (tipo imagen) y "Ejemplo tipografía" (tipo tipografía) — en vez de los 38 anteriores. Verificado leyendo `DEFAULT_RESOURCES` resultante: exactamente 2 entradas, ids `example-image`/`example-font`, sembradas por el mismo `seedDefaultResources()` sin cambios.
2. [x] El recurso "Ejemplo imagen" debe visualizarse en la galería como un cuadrado con fondo azul claro, borde azul y el texto "Ejemplo imagen" legible encima. Verificado generando la imagen con Pillow (512×512, fondo `#eaf3fc`, borde `#2c7dd8` 6px, texto "Ejemplo imagen" en `#2c7dd8`) e inspeccionando visualmente el PNG resultante antes de convertir a WebP y embeber — coincide con lo esperado.
3. [x] El recurso "Ejemplo tipografía" debe poder asignarse como fuente de un `TextBox`/dado igual que cualquier tipografía subida a mano, y renderizar con la tipografía Actor en la vista previa. Verificado: el recurso no lleva marcador especial de id en `ui/fontFaceRegistry.js` ni en el resto de `ui/*.js` (todos operan genéricamente por `resource.type`/`resource.dataUrl`), así que sigue el mismo camino que cualquier tipografía TTF subida; el TTF descargado se validó como fuente TrueType válida (`file` lo confirma) antes de embeberlo.
4. [x] Ambos recursos deben poder editarse/eliminarse desde el panel "Recursos" igual que cualquier recurso normal (no llevan ningún trato especial más allá del id fijo, igual que pasaba con los 38 anteriores). Verificado: `grep` sobre `src/**/*.js` no encuentra ninguna referencia a `example-image`/`example-font` ni a los ids antiguos fuera de `defaultResources.js` — no hay lógica que trate estos ids de forma especial en el panel.
5. [x] Cargar una partida guardada con la app anterior a este cambio (`resourcesSeeded` ausente o `false`) debe recibir como backfill los 2 recursos nuevos (no los 38 antiguos) — mismo mecanismo de siempre (`seedDefaultResources()`), contenido distinto. Verificado en `main.js`: el guard `if (!getResourcesSeeded()) seedDefaultResources()` (rama de guardado existente y rama de semilla embebida) itera `DEFAULT_RESOURCES` sin lógica de conteo ni de contenido específico — el cambio de 38 a 2 entradas no requiere tocar ese código.
