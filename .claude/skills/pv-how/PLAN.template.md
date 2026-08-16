- **Fecha creación**: [YYYY-MM-DD]
- **Riesgo**: [mediana 0-10 devuelta por pv-internal-tech-risks]

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

## (f) Análisis de riesgo

*Solo si el usuario ha pedido el detalle del riesgo — por defecto esta sección se omite y solo queda el campo **Riesgo** de la cabecera.* Lista de los 9 factores evaluados por `pv-internal-tech-risks` con su valor 0-10, y la mediana final.

| Factor | Valor |
|---|---|
| Uso compartido | [0-10] |
| Alcance | [0-10] |
| Profundidad del cambio | [0-10] |
| Cobertura de tests | [0-10] |
| Criticidad del flujo | [0-10] |
| Reversibilidad | [0-10] |
| Datos persistentes | [0-10] |
| Superficie de seguridad | [0-10] |
| Datos sensibles | [0-10] |

**Mediana**: [0-10]

| Valor | Significado |
|---|---|
| 0 | Sin riesgo — cambio totalmente aislado, imposible que afecte a nada más |
| 1–2 | Riesgo mínimo — cambio local, con red de seguridad (tests) o fácilmente reversible |
| 3–4 | Riesgo bajo — toca algo de superficie compartida o varios puntos, pero sin tocar contratos ni datos |
| 5–6 | Riesgo moderado — comparte código con otras partes, cobertura de test parcial, o toca un contrato/firma usado por otros |
| 7–8 | Riesgo alto — cambio profundo en código muy compartido y/o sin tests, en un flujo relevante, datos persistentes o seguridad |
| 9 | Riesgo muy alto — cambio estructural en flujo crítico de negocio, difícil de revertir, sin tests |
| 10 | Riesgo extremo — cambio profundo y amplio en código crítico y muy compartido, sin tests, sin reversibilidad fácil, tocando datos y/o seguridad a la vez |
