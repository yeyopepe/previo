- **Name**: Reordenar y renombrar "tooltip" en Ayuda jugador
- **Code**: 00215
- **Type**: fast
- **Creation date**: 2026-08-15

## Full description

En el modal de propiedades de un componente, pestaña "Generales", sección "Ayuda jugador", hay dos bloques de opciones: uno para el título del componente ("Mostrar título de componente" + botón "Editar título de componente…") y otro para el tooltip ("Mostrar tooltip" + campo de texto "Tooltip"). Actualmente el bloque del tooltip aparece primero y el del título después.

Se pide:
1. Intercambiar el orden de ambos bloques, para que el bloque del título aparezca primero y el del tooltip después.
2. Sustituir la palabra "tooltip" por "ayuda" en los textos visibles de esa sección: el checkbox "Mostrar tooltip" pasa a llamarse "Mostrar ayuda", la etiqueta del campo de texto "Tooltip" pasa a llamarse "Ayuda", y los textos explicativos (iconos de ayuda contextual "?") de esos dos campos se reformulan usando "ayuda" en vez de "tooltip".

Solo cambia el texto visible en esa sección del modal de propiedades del componente. No afecta al comportamiento (el checkbox sigue activando el mismo tooltip al pasar el ratón por encima en Modo Juego), ni a ningún otro modal (el checkbox "Mostrar tooltip" del modal de propiedades de un Grupo no forma parte de la sección "Ayuda jugador" y queda fuera de este cambio).

## Technical notes

- `src/ui/componentModal.js`, sección "Ayuda jugador" dentro de la pestaña "Generales" (~líneas 497-597 antes del cambio): bloque tooltip = `tooltipField` + `tooltipTextoField` (checkbox "Mostrar tooltip", label "Tooltip", dos `createHelpIcon`); bloque título = `titleField` + `titleEditField` (checkbox "Mostrar título de componente", botón "Editar título de componente…").
- Reordenar es solo cambiar el orden de `helpSection.appendChild(...)` de ambos bloques (o mover el bloque de código completo); no cambia ninguna variable, evento ni dato.
- Renombrar solo afecta a `textContent`/`text` de: `tooltipLabel` ("Mostrar tooltip" → "Mostrar ayuda"), `tooltipTextoLabel` ("Tooltip" → "Ayuda"), y los dos `createHelpIcon({ text: ... })` asociados a esos campos. No se tocan nombres de variables JS (`tooltipField`, `tooltipCheckbox`, etc.) ni las propiedades del modelo de datos (`mostrarTooltip`, `tooltipTexto` en `core/component.js`/`core/group.js`), que quedan igual.
- El checkbox "Mostrar tooltip" de `src/ui/groupModal.js` (sección "General" del modal de grupo) usa el mismo texto pero vive en otra sección/modal — no se toca.

## Cambios aplicados

- `src/ui/componentModal.js`, sección "Ayuda jugador" (pestaña "Generales" del modal de propiedades de un componente):
  - Movido el bloque de código de `tooltipField`/`tooltipTextoField` para que se añada a `helpSection` después del bloque `titleField`/`titleEditField` (antes iba primero) — el título aparece ahora primero y el tooltip después.
  - `tooltipLabel.textContent`: `'Mostrar tooltip'` → `'Mostrar ayuda'`.
  - `tooltipTextoLabel.textContent`: `'Tooltip'` → `'Ayuda'`.
  - Texto del icono de ayuda del checkbox: "...muestra un tooltip al pasar el ratón por encima en Modo Juego: el texto de 'Tooltip'..." → "...muestra una ayuda al pasar el ratón por encima en Modo Juego: el texto de 'Ayuda'...".
  - Texto del icono de ayuda del campo de texto: "Texto que verá el jugador como tooltip..." → "Texto que verá el jugador como ayuda...".
  - Sin cambios en nombres de variables JS, en el modelo de datos (`mostrarTooltip`, `tooltipTexto`) ni en ningún otro fichero.
