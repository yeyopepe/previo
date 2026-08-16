---
name: pv-internal-mockups-ascii
description: Procedimiento compartido, agnóstico al proyecto, para crear o editar maquetas visuales estáticas en texto plano con caracteres ASCII (`design_*.txt`) de un change/fix. Recibe la carpeta destino y la lista de elementos visuales a maquetar (nuevos o a editar) y devuelve las rutas de los ficheros creados/editados, sin decidir por sí misma qué elementos hacen falta ni validar nada con el usuario. Uso interno de las skills pv-new y pv-fix (directamente o desde extend-entry.md), invocada por el nombre configurado en `framework.skills.mockups` de `.claude/pv-context.json` cuando el proyecto prefiere maquetas ASCII en vez de HTML.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.0
  uses: []
---

# pv-internal-mockups-ascii

Procedimiento único y compartido para generar la maqueta visual (`design_*.txt`) de un elemento de UI nuevo o modificado, como arte ASCII en texto plano. Solo lo invocan otras skills del framework `pv-*` — no está pensado para invocación directa por el usuario.

**Esta skill no decide qué elementos necesitan maqueta ni valida nada con el usuario.** Eso lo decide siempre quien invoca (típicamente `pv-new`/`pv-fix`, al detectar que el cambio tiene componente visual): esta skill solo se invoca cuando ya se sabe que hace falta generar o editar al menos una maqueta ASCII, nunca "por si acaso". Presentar el resultado al usuario para que lo confirme también es responsabilidad de quien invoca.

Esta skill es específicamente para maquetas en **texto ASCII**. Si un proyecto configura otra skill en `framework.skills.mockups` para usar otra tecnología (p.ej. HTML, Figma, una librería de componentes, imágenes), esa skill alternativa debe cumplir el mismo contrato de entrada/salida descrito aquí para poder sustituir a esta sin que `pv-new`/`pv-fix` necesiten cambiar nada.

## Entrada esperada de quien invoca

- **Carpeta destino**: la ruta donde deben vivir los ficheros, normalmente `{changesDir}/inProgress/{xxxx}/`.
- **Lista de elementos visuales**, uno por cada maqueta a crear o editar. Por cada elemento:
  - **Descripción breve** del elemento (se usa para el nombre del fichero: `design_<descripción-del-elemento>.txt`, p.ej. `design_modal-seleccion-mazo.txt`, `design_barra-progreso.txt`).
  - **Qué debe mostrar**: aspecto, maquetación, contenido de ejemplo relevante para ilustrar el resultado (no hace falta que quien invoca dé detalle de bajo nivel — colores exactos, medidas — si no lo tiene todavía).
  - **Acción**: `crear` (fichero nuevo) o `editar` (ya existe un `design_*.txt` en la carpeta destino con ese nombre y hay que modificarlo) — en este segundo caso, qué cambia respecto a lo que ya hay.

## Reglas de cada maqueta

Cada fichero `design_*.txt` es solo una maqueta visual, no un prototipo funcional:

- Es texto plano puro: solo caracteres ASCII (líneas, esquinas y rellenos con `-`, `|`, `+`, `_`, `/`, `\`, `*`, `#`, `.`, espacios, etc.). Nada de HTML, Markdown, emojis ni caracteres Unicode de dibujo de cajas (`─│┌┐└┘`) — el objetivo es que se vea igual de bien en cualquier editor de texto monoespaciado.
- Usa fuente monoespaciada como asunción implícita: alinea columnas y bordes con espacios, cuidando que cada línea de un mismo bloque tenga el ancho consistente para que las cajas cuadren visualmente.
- Debe mostrar únicamente el aspecto (disposición de elementos, jerarquía, agrupación, tamaños relativos) que tendría ese elemento — no necesita datos reales, basta contenido de ejemplo estático que ilustre el resultado (textos de botones, etiquetas, valores de ejemplo).
- Representa controles y estados con convenciones simples y explícitas cuando aporten claridad, por ejemplo:
  - Botón: `[ Guardar ]`
  - Campo de texto: `[ nombre del grupo____ ]`
  - Checkbox marcado/vacío: `[x]` / `[ ]`
  - Elemento seleccionado o resaltado: `> Opción activa <` o rodeado de `*`
  - Icono o imagen: un marcador entre corchetes describiendo qué es, p.ej. `[icono-papelera]`
- Si el elemento tiene varios estados relevantes (p.ej. normal / hover / error) o el flujo tiene varios pasos, represéntalos como bloques separados dentro del mismo fichero, cada uno con un título breve en una línea de comentario (p.ej. `-- Estado: error --`) antes del bloque.
- Un fichero por cada elemento visual diferenciado de la propuesta — no agrupes varios elementos distintos en un mismo `design_*.txt` salvo que quien invoca los haya pedido como una única unidad.

## Pasos

1. Para cada elemento de la lista recibida, crea (si la acción es `crear`) o edita (si es `editar`) el fichero `design_<descripción-del-elemento>.txt` correspondiente en la carpeta destino, siguiendo las reglas de arriba. Al editar, respeta el resto del fichero que no esté relacionado con el cambio pedido.
2. Devuelve a quien invoca, en el mismo turno, la lista de rutas de los ficheros creados/editados (una por elemento). No presentes nada al usuario ni pidas confirmación — eso lo hace quien invoca.
