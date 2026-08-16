# Modo `/pv-new todo <código>`

Procedimiento completo cuando la skill `pv-new` se invoca como `/pv-new todo <código>` (o el usuario pide explícitamente "convierte la idea `<código>` de todo en un change"). Esta entrada no nace de una petición nueva del usuario en el chat, sino del contenido ya apuntado por `pv-todo`.

1. Comprueba que existe **exactamente** `{changesDir}/todo/{código}/description.md`. Si no existe, dile al usuario que no hay ninguna idea con ese código en `todo/` y detente ahí (no inventes ni asumas un código parecido).
2. Lee ese `description.md` completo (secciones `## Idea`, `## Código` y `## Notas`) y, si los hay, sus ficheros `design_*.html` de esa misma carpeta. Este es el contenido a analizar y documentar — úsalo como si fuera la petición del usuario para el resto del proceso, en vez de esperar una descripción nueva en el chat. Si el usuario añadió también contexto adicional al invocar la skill, súmalo al análisis.
3. Pregunta al usuario si quiere desarrollar la idea contigo antes de continuar.

```
¿Quieres que refinemos esta idea ("<nombre de la idea>") antes de escribirla o documento el cambio con la información actual?
```

Si confirma, propón ideas y charla con él hasta refinar un poco más la idea antes de continuar con el punto 4. Si no quiere, pasa al punto 4.
4. Continúa con el proceso habitual desde el paso 1 de "Pasos" de `SKILL.md` (anticipar dudas, documentar con `pv-internal-workflow`, propuesta visual), usando ese contenido como base. Al invocar `pv-internal-workflow` en el paso 2 de "Pasos", usa como `promptOriginal` el contenido de `## Notas` de la idea (más cualquier contexto adicional que el usuario haya añadido al invocar la skill o durante el refinado del paso 3 de aquí), para que quede como historial en `history.md`. Si había `design_*.html` en la idea de `todo/`, tenlos en cuenta al construir la propuesta visual del paso 3 (no los copies tal cual sin más: son solo un boceto de partida, no una maqueta ya validada).
5. **Solo si el paso 2 de "Pasos" termina con éxito** (la entrada ya existe en `{changesDir}/inProgress/{xxxx}/`), borra automáticamente `{changesDir}/todo/{código}/` entera (`description.md` y cualquier `design_*.html` que tuviera), sin pedir confirmación al usuario — el borrado es una limpieza automática del origen ya migrado, no una acción destructiva que requiera aprobación. Si el paso 2 no llega a completarse, deja la idea tal cual en `todo/`.
6. En el paso 4 de "Pasos" (indicar el siguiente paso), menciona también que la idea `{código}` de `todo/` ha quedado convertida en el cambio `{xxxx}` y borrada de `todo/`.
