- **Name**: Unificar comportamiento del icono de ayuda "?"
- **Code**: 00213
- **Type**: change
- **Creation date**: 2026-08-15

## Full description

En toda la app existe un icono de ayuda contextual "?" que aparece junto a distintos campos de las ventanas de propiedades y configuración. Hoy conviven dos comportamientos distintos según cuánto texto tenga la ayuda: algunas ayudas aparecen como un pequeño tooltip flotante con solo pasar el cursor por encima, mientras que otras exigen pulsar sobre el icono para que se abra una ventana emergente con el texto.

Se unifica ese comportamiento a uno solo: **todos** los iconos de ayuda "?" de la app, sin excepción, abren la ventana emergente de ayuda al pulsar sobre el icono. Deja de existir la variante de tooltip que aparecía solo con pasar el cursor por encima — ya no depende de cuánto texto tenga la ayuda, el comportamiento es el mismo en todos los casos.

Esto afecta a los iconos de ayuda de las ventanas de propiedades de componente, propiedades de grupo, edición del título de componente, copia de componente y editor visual de cartas — cualquier punto de la app donde aparezca este icono de ayuda.

### Puntos de alcance resueltos

- **Contenido que hoy ya se muestra en ventana emergente** (textos largos): sin cambios de fondo, sigue en ventana emergente al pulsar.
- **Contenido que hoy se muestra en tooltip al pasar el cursor** (textos cortos): pasa a mostrarse también en ventana emergente al pulsar, dejando de aparecer solo con el cursor encima.
- **Contenido con formato** (un caso concreto en el editor visual de cartas): sin cambios, se sigue mostrando en la ventana emergente tal cual ya se mostraba.
- **Datos, roles y modos de la app**: sin cambios — es un ajuste de comportamiento de interfaz, no afecta a qué se guarda ni a quién puede ver o editar qué.
- **Aspecto visual**: sin cambios — se reutiliza la misma ventana emergente de ayuda que ya existe hoy para los casos de texto largo, y el propio icono "?" mantiene su aspecto actual.

### Aclaración sobre la dirección del cambio

La petición inicial planteaba lo contrario (unificar hacia mostrar siempre el tooltip al pasar el cursor, sin pulsar). Tras revisar con el usuario los casos de texto largo y con formato que hoy dependen de la ventana emergente, se acordó invertir la dirección: la unificación final va hacia "siempre pulsar para ver la ayuda en ventana emergente", no hacia "siempre tooltip al pasar el cursor". Ver `history.md` para la traza completa de esa conversación.

## Technical notes

- Todos los iconos de ayuda de la app se generan desde un único componente compartido, `ui/helpIcon.js` (`createHelpIcon({ text, html })`), usado en 18 puntos: `componentModal.js` (9), `copyComponentModal.js` (2), `groupModal.js` (3), `componentTitleModal.js` (1), `visualEditorModal.js` (1, con `html`).
- Hoy ese componente decide el comportamiento según una constante `MODAL_THRESHOLD = 200` (caracteres): por debajo, tooltip vía CSS `.help-icon:hover .help-icon__tooltip`; por encima, o si hay `html`, listener de click que abre `openHelpModal` (reutiliza `.modal-overlay`/`.modal`, botón "Cerrar").
- Para este cambio: eliminar `MODAL_THRESHOLD` y la rama condicional en `createHelpIcon` — debe añadir siempre el listener de click, sin crear nunca el nodo `.help-icon__tooltip`.
- `src/styles/main.css` (~líneas 1994-2015): la clase `.help-icon__tooltip` y la regla `.help-icon:hover .help-icon__tooltip` quedan sin uso tras el cambio anterior — valorar su eliminación como parte de la limpieza.
- `design/docs/style/03-modales-menus.md §12` ("Icono de ayuda (tooltip / modal)") documenta el comportamiento dual actual — debe actualizarse para reflejar el comportamiento único (ventana emergente al pulsar, sin bifurcación por longitud de texto).
- No confundir con otros tooltips de la app que no son de este patrón y quedan fuera de alcance: `.component-tooltip` (identificación de componente en Modo Juego, `ui/componentRenderer.js`, disparado en hover sobre todo el componente) y `.component-title-label` (rótulo de título de componente, siempre visible, no depende de hover) — ninguno de los dos usa `ui/helpIcon.js` ni el icono "?".
