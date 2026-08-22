# Candidatas a diagrama de flujo (workflow.<flujo>.md)

Evaluación de qué skills `pv-*` son candidatas a tener su flujo documentado como diagrama Mermaid dedicado (`workflow.<nombre-flujo>.md`), siguiendo la convención ya aplicada en `pv-init` (`workflow.init.md`) y `pv-update` (`workflow.audit.md`), documentada en `.claude/pv-doc/pv-design/pv-design.en.md`'s "Workflow diagrams" section.

Criterio: tiene sentido cuando la skill combina varios pasos con ramas condicionales reales, puntos donde solo informa al usuario (no bloquea) y puntos donde pide confirmación/datos de forma bloqueante. No tiene sentido para flujos triviales, lineales o sin interacción con el usuario.

## Candidatas fuertes

- **pv-fix** — dos sub-flujos completos (fast-track vs. no-trivial) con múltiples bifurcaciones (trivial/bug/change) y puntos de confirmación bloqueante antes de encadenar `pv-how`.
- **pv-how** — flujo largo con reentradas (regenerar `plan.md` vs. reutilizar el existente), inconsistencias a resolver con el usuario, y una decisión bloqueante final (implementar ahora o no).
- **pv-new** — múltiples puntos de entrada (nuevo/extensión/desde `todo`) y una condición central de representación visual (4 casos no excluyentes), con validación bloqueante del usuario.
- **pv-version** — bucle de confirmación por cada entrada pendiente en `implemented/`, rama informativa-only (solo actualizar el procedimiento de build) vs. proceso completo. Ya insinúa la necesidad de un diagrama: referencia hoy un `version-flow-diagram.template.md` propio — lo natural sería formalizarlo bajo la convención `workflow.*.md` en vez de dejarlo como template aparte.

## Candidatas débiles

Tienen alguna rama o interacción puntual, pero el flujo global es mayormente una tubería determinista — el valor de un diagrama es menor que en las fuertes:

- **pv-internal-tech-analysis** — una rama relevante (documentación suficiente vs. explorar código) y una única excepción bloqueante aislada (confirmar una duda de definición).
- **pv-internal-changelog** — algunas ramas de clasificación (Fixes directo vs. comparar New/Changed/Removed) y un punto de confirmación (versión anterior detectada), pero predominantemente scripts deterministas.
- **pv-do** — casi lineal, con guardas de configuración ("si está configurado, actualizar; si no, saltar") más que bifurcaciones funcionales, sin interacción bloqueante en el camino normal.

## No candidatas

Lineales, sin ramas de negocio reales, o sin interacción con el usuario:

- **pv-status** — router de 3 modos exclusivos, cada rama lineal.
- **pv-todo** — crear/anexar/listar, sin decisiones significativas.
- **pv-internal-workflow** — mecánica de archivos determinista con un guardarraíl de invocación directa.
- **pv-internal-tech-security** — checklist evaluada por categoría, no un flujo temporal.
- **pv-internal-tech-mermaid** — utilidad de generación pura, sin flujo propio ni interacción.
- **pv-internal-tech-risks** — scoring determinista de 9 factores, sin ramas de decisión.
- **pv-internal-mockups-html** / **pv-internal-mockups-ascii** — utilidades de un solo paso funcional (crear/editar), sin interacción.
- **pv-internal-doc-features** — mecánica de archivo con una bifurcación menor (`existing_file` sí/no), sin interacción de usuario.
- **pv-internal-doc-technical** — guía de estilo estática, no es un flujo.

## Siguiente paso sugerido

Crear `workflow.*.md` para las 4 candidatas fuertes, empezando por `pv-version` (ya tiene medio camino andado con `version-flow-diagram.template.md`), y revisar los `SKILL.md` correspondientes para evitar redundancia/contradicción con el diagrama, igual que se hizo con `pv-init`/`pv-update`.
