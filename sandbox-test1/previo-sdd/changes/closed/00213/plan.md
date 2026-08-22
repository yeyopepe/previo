- **Creation date**: 2026-08-15
- **Risk**: [pending recalculation]

## (a) Functional notes

**Out of scope:** aspecto visual del icono "?" (tamaño, color, cursor `help`) — sin cambios, según lo acordado. `.component-tooltip` (identificación de componente en Modo Juego) y `.component-title-label` (rótulo de título de componente) — ninguno de los dos usa `ui/helpIcon.js`, quedan fuera de este cambio aunque uno de ellos reutilice visualmente el mismo aspecto de tooltip flotante.

**Doubts resolved with the user:** ninguna pregunta abierta en esta planificación — el alcance y la dirección del cambio (unificar hacia "siempre ventana emergente al pulsar", no hacia "siempre tooltip al pasar el cursor") ya quedaron resueltos y documentados en `description.md`/`history.md` durante el análisis funcional (`pv-fix`/`pv-new`).

## (b) Technical solution

- [x] **`src/ui/helpIcon.js` — eliminar la bifurcación tooltip/modal.** Quitar la constante `MODAL_THRESHOLD` (línea 4) y la condición `html != null || (text != null && text.length >= MODAL_THRESHOLD)` de `createHelpIcon`. El icono debe añadir siempre el listener de `click` que llama a `openHelpModal({ text, html })` (con `e.stopPropagation()`, igual que hoy), sin la rama `else if (text != null)` que crea el nodo `.help-icon__tooltip` — esa rama y el nodo `tooltip` dejan de existir. Actualizar también el comentario de cabecera del fichero (línea 1-2, "tooltip para texto plano corto, modal para texto largo o con formato") para reflejar el comportamiento único.
- [x] **`src/styles/main.css` — limpiar reglas sin uso.** Eliminar `.help-icon__tooltip` (~línea 2034-2051) y `.help-icon:hover .help-icon__tooltip` (~línea 2053-2055), que quedan sin ningún selector que las dispare tras la tarea anterior. Mantener `.help-icon`/`.help-icon:hover` (aspecto del icono, sin cambios) y el comentario `/* Reusable help icon... */` de cabecera (línea 2010), actualizándolo para que no siga describiendo la variante tooltip. En el comentario de `.component-tooltip` (línea 2057-2063, "Mismo aspecto que .help-icon__tooltip..."), sustituir la referencia a esa clase (que deja de existir) por la descripción directa del aspecto que comparten (fondo `var(--bg-toolbar)`, texto `var(--text-light)`, `box-shadow: var(--shadow-2)`), sin cambiar el resto del comentario ni la regla en sí — `.component-tooltip` no se toca funcionalmente, queda fuera de alcance.

No hace falta tocar ninguno de los 19 puntos donde se llama a `createHelpIcon({ text, html })` (`componentModal.js`, `copyComponentModal.js`, `groupModal.js`, `componentTitleModal.js`, `visualEditorModal.js`): la firma de la función no cambia, solo su comportamiento interno.

## (d) Style changes

- `design/docs/style/03-modales-menus.md`:
  - §12 "Icono de ayuda (tooltip / modal)": reescribir para reflejar el comportamiento único. Título pasa a "Icono de ayuda (modal al pulsar)". Eliminar el punto "Tooltip" (`.help-icon__tooltip`, umbral de 200 caracteres) por completo. El punto "Modal" deja de condicionarse a longitud/formato — se aplica siempre, sin excepción, al pulsar el icono. Mantener la frase "Cualquier ayuda contextual nueva: reutilizar `ui/helpIcon.js`...".
  - §12.3 "Etiqueta identificativa de componente (modo edición)": la frase "Aspecto reutilizado de `.help-icon__tooltip` (§12)" referencia una clase que deja de existir — sustituir por la descripción directa del aspecto compartido (fondo `var(--bg-toolbar)`, texto `var(--text-light)`, `box-shadow: var(--shadow-2)`), sin cambiar nada más de esa sección (`.component-tooltip` en sí no se modifica, queda fuera de alcance de este cambio).
  - §12.2 (tabla de cursores): sin cambios — `cursor: help` en `.help-icon` se mantiene tal cual, fuera de alcance (aspecto visual sin cambios, acordado con el usuario).

## (e) Verification

- [x] Pasar el cursor (sin pulsar) sobre varios iconos de ayuda "?" de distintos ficheros (p. ej. "Bloqueado" en `componentModal.js`, uno de `groupModal.js`, el del editor visual de cartas en `visualEditorModal.js`): no aparece ningún tooltip flotante en ningún caso, solo el cursor de ayuda.
- [x] Pulsar sobre varios de esos mismos iconos: se abre la ventana emergente con el texto/HTML correspondiente en todos los casos, incluido el caso con formato del editor visual de cartas, y se cierra con "Cerrar" o clic fuera del modal.
- [x] `grep -rn "MODAL_THRESHOLD\|help-icon__tooltip" src/` no devuelve ninguna coincidencia en código fuente (fuera de `src/_output/`, que son builds generados y no se tocan).
