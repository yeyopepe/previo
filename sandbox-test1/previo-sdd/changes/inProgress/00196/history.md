# Prompt history — 00196

Historical information about the analysis process, not current information. Records, verbatim and without rephrasing, the successive prompts with which the user raised and expanded this entry — they can be incomplete or contradictory with each other, since they reflect how the request evolved session by session, not the final result (that lives in `description.md`).

**Exclusive use of `pv-new` and `pv-fix`.** No other skill in the framework (`pv-how`, `pv-do`, `pv-status`, etc.) should read this file or take it into account: the source of truth for what's being asked is always `description.md`.

## 2026-08-09 — initial session

añade un nuevo componente llamado "bloc de notas" que permita escribir texto con las siguientes características.

Características comunes en modo edición y juego:
- Redimensionable
- Permite escribir un título y un cuerpo
- Incorpora una pequeña barra con herramientas:
      - estilo del texto en el cuerpo: negrita, cursiva, subrayado (usa markdown para guardarlo)

## 2026-08-09 — session 2

El resto estaba bien. Añade otra característica:
- el fondo de la barra superior (dónde está el título), debería tener un color de fondo cofigurable en cualquier modo y momento
- El color del título siempre será negro pero añade a la barra de herramientas dos cosas más:
    - Color del texto seleccionado
    - Color de fondo del texto seleccionado

## 2026-08-09 — session 3

añade también en la parte derecha de la barra de título un icono para copiar todo el contenido de la nota al portapapeles (sin formato: titulo + cuerpo)

## 2026-08-09 — session 4

el componente se llamará "Bloc de notas" e inicialmente son 2 botones uno al lado del otro:
- uno cuadrado y amarillo con una etiqueta "Nueva hoja (0)".
- otro redondo con el dibujo de un ojo que muestra/oculta las hojas (todas).
Al pulsar el botón se añade una nueva hoja con toda la funcionalidad descrita y se actualiza el contador de la etiqueta.
Se pueden añadir múltiples hojas, cada una independiente (redimensionable, movible, etc), pero todas forman parte del mismo componente. Cada hoja lleva un id interno formado con el nombre del componente y un sufijo numerado.
El editor es WYSIWYG pero el formato que usa es markdown.
El botón de copiar contenido copia ese contenido en formato markdown.

Respuestas a las dudas planteadas:
2. También redimensiona
4. Simplifica y que no se reutilice. El usuario tampoco lo va a ver nunca.
6. Si el ojo está en ocultar, el botón de añadir hoja está deshabilitado.
7. Añade un botón para borrar cada hoja
8. Aunque el bloc de notas esté bloqueado, se pueden añadir hojas nuevas. El bloqueo afecta solo al elemento del bloc de notas.
Añade al menú contextual del bloc de notas una opción Bloquear notas (des/bloquea todas las notas a la vez).
Añade también un botón para des/bloquear cada nota por separado.
11. WYSIWYG
12. Al pulsar el botón permite elegir: con formato, sin formato

Confirmación final: sí a las 3 propuestas de cierre (bloqueo rápido individual/global solo entre Ninguno/Todos, borrado de hoja con confirmación, copia "con formato" en markdown con título como encabezado `# Título`).
