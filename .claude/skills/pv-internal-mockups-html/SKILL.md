---
name: ms-internal-mockups-html
description: Procedimiento compartido, agnóstico al proyecto, para crear o editar maquetas visuales estáticas en HTML (`design_*.html`) de un change/fix. Recibe la carpeta destino y la lista de elementos visuales a maquetar (nuevos o a editar) y devuelve las rutas de los ficheros creados/editados, sin decidir por sí misma qué elementos hacen falta ni validar nada con el usuario. Uso interno de las skills ms-new y ms-fix (directamente o desde extend-entry.md), invocada por el nombre configurado en `framework.skills.mockups` de `.claude/ms-context.json` (por defecto, esta misma skill).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 1.0.0
  uses: []
---

# ms-internal-mockups-html

Procedimiento único y compartido para generar la maqueta visual (`design_*.html`) de un elemento de UI nuevo o modificado, en HTML/CSS/SVG estático autocontenido. Solo lo invocan otras skills del framework `ms-*` — no está pensado para invocación directa por el usuario.

**Esta skill no decide qué elementos necesitan maqueta ni valida nada con el usuario.** Eso lo decide siempre quien invoca (típicamente `ms-new`/`ms-fix`, al detectar que el cambio tiene componente visual): esta skill solo se invoca cuando ya se sabe que hace falta generar o editar al menos una maqueta HTML, nunca "por si acaso". Presentar el resultado al usuario para que lo confirme también es responsabilidad de quien invoca.

Esta skill es específicamente para maquetas en **HTML**. Si un proyecto configura otra skill en `framework.skills.mockups` para usar otra tecnología (p.ej. Figma, una librería de componentes, imágenes), esa skill alternativa debe cumplir el mismo contrato de entrada/salida descrito aquí para poder sustituir a esta sin que `ms-new`/`ms-fix` necesiten cambiar nada.

## Entrada esperada de quien invoca

- **Carpeta destino**: la ruta donde deben vivir los ficheros, normalmente `{changesDir}/inProgress/{xxxx}/`.
- **Lista de elementos visuales**, uno por cada maqueta a crear o editar. Por cada elemento:
  - **Descripción breve** del elemento (se usa para el nombre del fichero: `design_<descripción-del-elemento>.html`, p.ej. `design_modal-seleccion-mazo.html`, `design_barra-progreso.html`).
  - **Qué debe mostrar**: aspecto, maquetación, contenido de ejemplo relevante para ilustrar el resultado (no hace falta que quien invoca dé detalle de bajo nivel — colores exactos, medidas — si no lo tiene todavía).
  - **Acción**: `crear` (fichero nuevo) o `editar` (ya existe un `design_*.html` en la carpeta destino con ese nombre y hay que modificarlo) — en este segundo caso, qué cambia respecto a lo que ya hay.

## Reglas de cada maqueta

Cada fichero `design_*.html` es solo una maqueta visual, no un prototipo funcional:

- Debe mostrar únicamente el aspecto (maquetación, estilos, iconografía) que tendría ese elemento — no necesita datos reales ni lógica, basta contenido de ejemplo estático que ilustre el resultado.
- No debe tener funcionalidad real: nada de JavaScript que reaccione a eventos, ni llamadas a red, ni estado — como mucho, JS puramente decorativo si hiciera falta para el aspecto visual.
- Ha de ser autocontenido: solo HTML, CSS y SVG, todo incrustado en el propio fichero (sin ficheros externos, sin CDNs, sin imports).
- Un fichero por cada elemento visual diferenciado de la propuesta — no agrupes varios elementos distintos en un mismo `design_*.html` salvo que quien invoca los haya pedido como una única unidad.

## Pasos

1. Para cada elemento de la lista recibida, crea (si la acción es `crear`) o edita (si es `editar`) el fichero `design_<descripción-del-elemento>.html` correspondiente en la carpeta destino, siguiendo las reglas de arriba. Al editar, respeta el resto del fichero que no esté relacionado con el cambio pedido.
2. Devuelve a quien invoca, en el mismo turno, la lista de rutas de los ficheros creados/editados (una por elemento). No presentes nada al usuario ni pidas confirmación — eso lo hace quien invoca.
