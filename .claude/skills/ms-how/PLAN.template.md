- **Fecha creación**: [YYYY-MM-DD]

## (a) Anotaciones funcionales

**Fuera de alcance:** [qué queda explícitamente fuera de esta solución — si es un fix, qué mejoras adicionales se detectaron pero no se incluyen. Si no hay nada que excluir, dilo explícitamente ("ningún otro comportamiento se toca") en vez de omitir el campo.]

**Dudas resueltas con el usuario:** [pregunta y respuesta, en breve. Si no hubo ninguna, dilo explícitamente ("ninguna pregunta abierta...") en vez de omitir el campo.]

## (b) Solución técnica

- [ ] **`[fichero]` — [resumen breve de la tarea].** [Qué hay que tocar exactamente (función, variable, regla CSS...), dónde, y por qué — con el detalle suficiente para que se pueda implementar sin volver a decidir nada de diseño. Si hace falta un snippet o un valor exacto (una regla CSS, un nombre de clase, una condición), inclúyelo literal en vez de describirlo en prosa.]
- [ ] **`[fichero]` — [resumen breve de la siguiente tarea].** [...]
- [ ] [...]

Ordena las tareas en el orden en que se deberían implementar. No incluyas aquí pasos de comprobación/verificación manual — esos van en (e). Formato checklist (`- [ ]`) obligatorio: quien implemente debe marcar cada casilla `[x]` solo cuando esa tarea concreta esté hecha, nunca todas de golpe al final.

## (c) Cambios de arquitectura

*Solo si `docs.tech.architectureDocDir` está configurado y esta solución modifica la arquitectura básica del proyecto.* [Qué fichero(s) concretos de esa carpeta hay que actualizar y qué cambiar en cada uno. Omite la sección entera si no aplica.]

## (d) Cambios en estilo

*Solo si `docs.tech.styleBibleDocDir` está configurado y esta solución modifica o amplía el estilo visual del proyecto.* [Qué fichero(s) concretos de esa carpeta hay que actualizar y qué cambiar en cada uno. Omite la sección entera si no aplica.]

## (e) Verificación

- [ ] [Un resultado observable del sistema ya cambiado — no un paso más de implementación. Redáctalo de forma autocontenida (qué se hace y qué se debería ver), sin remitir a un número de tarea de (b): una misma comprobación puede depender de varias tareas a la vez, o una tarea puede no tener una comprobación propia y aportar solo a una compartida. La lista se recorre entera *después* de terminar toda la sección (b), como un checklist de cierre.]
- [ ] [...]

Incluye siempre esta sección (salvo que la solución no tenga ningún comportamiento observable que comprobar, lo cual es raro) — es lo que permite dar la implementación por terminada con confianza, incluso a quien la ejecute sin conocer más contexto que este documento. Formato checklist (`- [ ]`) obligatorio, igual que en (b).
