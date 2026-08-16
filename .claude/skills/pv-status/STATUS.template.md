# Project status

*Generated: {generatedDate}*

🆕 Change · 👾 Fix · ⚡ Fast · 💡 Todo   🟢 Ready to close · 🟡 Unplanned · 🟠 Planned

## Summary

{summaryBars}

---

| State | 🆕 Change | 👾 Fix | ⚡ Fast | 💡 Todo | Total |
| --- | --- | --- | --- | --- | --- |
| 💡 Todo | — | — | — | {todoTotal} | **{todoTotal}** |
| 🔧 In progress | {inProgressChange} | {inProgressFix} | — | — | **{inProgressTotal}** |
| ✅ Implemented | {implementedChange} | {implementedFix} | {implementedFast} | — | **{implementedTotal}** |
| 📦 Closed | {closedChange} | {closedFix} | {closedFast} | — | **{closedTotal}** |
| **Total** | **{changeTotal}** | **{fixTotal}** | **{fastTotal}** | **{todoTotal}** | **{totalTotal}** |

*(The Fast column can only have values in "Implemented" and "Closed": `fast` changes are pv-fix's trivial shortcut — they're applied and documented in the same invocation, without generating `plan.md`, landing directly in `implemented`.)*

## 🔧 In progress

### 🟢 Ready to review and close (in the changes/implemented folder, includes both change/fix and fast) — {toCloseTotal}

| Code | Description |
| --- | --- |
{readyRows}

### 🟡 Pending technical analysis (only `description.md`, pending planning with `pv-how`) — {pendingTotal}

| Code | Description |
| --- | --- |
{pendingRows}

### 🟠 Planned, pending implementation (`description.md` + `plan.md`, pending implementation) — {toImplementTotal}

| Code | Description |
| --- | --- |
{toImplementRows}

<!-- SECTION:noDescription -->
-   **Entries without `description.md` (anomalous):** {noDescriptionRows}
<!-- /SECTION:noDescription -->

<!-- SECTION:fast -->
## Implemented fast changes

{fastRows}
<!-- /SECTION:fast -->

## 💡 Ideas in todo/ (outside the change/fix flow)

{ideaRows}

<!-- SECTION:warnings -->
## Warnings

{warningRows}
<!-- /SECTION:warnings -->

<!-- ROW_ENTRY: | {icon} {xxxx} | {name} | -->
<!-- EMPTY_ENTRY: | — | *(none)* | -->
<!-- ROW_FAST: -   ⚡ {code} — {name} ({date}) -->
<!-- ROW_IDEA: -   {code}: {idea} -->
<!-- ROW_WARNING: -   {warning} -->
<!-- EMPTY_IDEAS: *(No ideas noted in `todo/`.)* -->
