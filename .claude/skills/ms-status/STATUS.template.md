# Estado del proyecto

*Generado: {fechaGeneracion}*

🆕 Change · 👾 Fix · ⚡ Fast · 💡 Todo   🟢 Listo para cerrar · 🟡 Sin planificar · 🟠 Planificado

## Resumen

{resumenBarras}

---

| Estado | 🆕 Change | 👾 Fix | ⚡ Fast | 💡 Todo | Total |
| --- | --- | --- | --- | --- | --- |
| 💡 Todo | — | — | — | {todoTotal} | **{todoTotal}** |
| 🔧 En progreso | {inProgressChange} | {inProgressFix} | — | — | **{inProgressTotal}** |
| ✅ Implementado | {implementedChange} | {implementedFix} | {implementedFast} | — | **{implementedTotal}** |
| 📦 Cerrado | {closedChange} | {closedFix} | {closedFast} | — | **{closedTotal}** |
| **Total** | **{changeTotal}** | **{fixTotal}** | **{fastTotal}** | **{todoTotal}** | **{totalTotal}** |

*(La columna Fast solo puede tener valores en "Implementado" y "Cerrado": los cambios `fast` son el atajo trivial de `ms-fix` — se aplican y documentan en la misma invocación, sin generar `plan.md`, quedando ya en `implemented`.)*

## 🔧 En progreso

### 🟢 Listos para revisar y cerrar (en la carpeta changes/implemented, incluye tanto change/fix como fast) — {toCloseTotal}

| Código | Descripción |
| --- | --- |
{filasListas}

### 🟡 Pendientes de análisis técnico (solo `description.md`, pendientes de planificar con `ms-how`) — {pendingTotal}

| Código | Descripción |
| --- | --- |
{filasPendientes}

### 🟠 Planificados, pendientes de implementar (`description.md` + `plan.md`, pendientes de implementar) — {toImplementTotal}

| Código | Descripción |
| --- | --- |
{filasImplementar}

<!-- SECTION:sinDescripcion -->
-   **Entradas sin `description.md` (anómalas):** {filasSinDescripcion}
<!-- /SECTION:sinDescripcion -->

<!-- SECTION:fast -->
## Cambios fast implementados

{filasFast}
<!-- /SECTION:fast -->

## 💡 Ideas en todo/ (fuera del flujo change/fix)

{filasIdeas}

<!-- SECTION:avisos -->
## Avisos

{filasAvisos}
<!-- /SECTION:avisos -->

<!-- ROW_ENTRY: | {icono} {xxxx} | {nombre} | -->
<!-- EMPTY_ENTRY: | — | *(ninguno)* | -->
<!-- ROW_FAST: -   ⚡ {código} — {nombre} ({fecha}) -->
<!-- ROW_IDEA: -   {codigo}: {idea} -->
<!-- ROW_AVISO: -   {aviso} -->
<!-- EMPTY_IDEAS: *(No hay ninguna idea apuntada en `todo/`.)* -->
