# Prompt history — 00212

Historical information about the analysis process, not current information. Records, verbatim and without rephrasing, the successive prompts with which the user raised and expanded this entry — they can be incomplete or contradictory with each other, since they reflect how the request evolved session by session, not the final result (that lives in `description.md`).

**Exclusive use of `pv-new` and `pv-fix`.** No other skill in the framework (`pv-how`, `pv-do`, `pv-status`, etc.) should read this file or take it into account: the source of truth for what's being asked is always `description.md`.

## 2026-08-15 — initial session

en los mazos aparece siempre en modo juego una etiqueta indicando el número de cartas. Quiero cambiarlo y ampliarlo para todos los componentes. Añade en "Ayuda Jugador":
      -Un check llamado Titulo para des/activar la aparición de un titulo: una etiqueta en la parte superior del componente. Si está activado, muestra el contenido del cuadro de texto según sus propiedades.
      - un botón que abre una modal con las propiedades del titulo:
                  1. cuadro de texto con el contenido del titulo
                  2. dos controles de color para el texto del titulo (negro por defecto) y para el fondo (blanco por defecto). 
                   3. Incluye opción para tranparencia del fondo.

[Aclaraciones posteriores, mismo día, recogidas por turnos de preguntas de confirmación]:

- "Se me olvidó: añade al texto del titulo y del tooltip la variable {cards_current} para sustituirla por el número de cartas actual. Esto de las variables lo quiero reutilizar en el futuro, así que crea un sistema reutilizable."
- Visibilidad del título: solo Modo Juego.
- Formato de texto del título: HTML básico, igual que Tooltip.
- Copiar/Pegar estilo y sincronización de copias: sí, mismo criterio que Tooltip.
- Variable no aplicable al tipo de componente: se deja literal, sin sustituir.
- Posición visual del título: igual que la etiqueta actual del mazo.
- "Mostrar título de componente": override de grupo, igual que "Mostrar tooltip".
- Nombre del campo: "Título de componente" (para evitar confusión con el título de cabecera de la partida).
