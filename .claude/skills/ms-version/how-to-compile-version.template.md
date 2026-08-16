# Cómo compilar el entregable de este proyecto

Fichero propio de `ms-version` (no forma parte de `.claude/ms-context.json`): describe el procedimiento de shell/build concreto de este repo para generar el entregable jugable. Lo rellena `ms-version` la primera vez que se invoca y no existe todavía, preguntando al usuario; en invocaciones siguientes se lee y se sigue tal cual, sin volver a preguntar. También se actualiza cada vez que el usuario informa de un cambio en este procedimiento.

Si el entregable se genera con un único comando, describe directamente "Comando(s) a ejecutar" y "Fichero(s) generado(s)" como en el ejemplo de abajo. Si el proceso consta de **varios pasos independientes que generan artefactos distintos** (todos ellos parte del mismo entregable completo, p.ej. build del juego + build de un PDF de reglas), documenta cada uno como un "Paso N: {nombre}" separado, cada uno con su propio "Comando(s) a ejecutar" y "Fichero(s) generado(s)" — en ese caso, todos los artefactos resultantes se copian a `files/`, uno por paso.

## Comando(s) a ejecutar

[Comando o secuencia de comandos exactos, en el orden en que hay que ejecutarlos, desde la raíz del repo. Incluye el intérprete/herramienta (p.ej. `python`, `npm run`) y cualquier flag necesario.]

## Fichero(s) generado(s)

[Ruta (o patrón de ruta, si el nombre incluye una versión autoincremental) donde queda el entregable tras ejecutar el/los comando(s) de arriba, y cómo identificar cuál es el más reciente si hay varios candidatos.]

## Notas

[Cualquier detalle adicional relevante: requisitos previos, efectos secundarios del build (ficheros que también se actualizan), advertencias sobre qué NO tocar manualmente, etc. Sección opcional — omítela si no hay nada que anotar.]
