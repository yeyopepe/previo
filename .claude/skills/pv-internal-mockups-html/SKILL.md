---
name: pv-internal-mockups-html
description: Shared, project-agnostic procedure to create or edit static visual mockups in HTML (`design_*.html`) for a change/fix. Receives the destination folder and the list of visual elements to mock up (new or to edit) and returns the paths of the created/edited files, without deciding on its own which elements are needed nor validating anything with the user. Internal use by the pv-new and pv-fix skills (directly or from extend-entry.md), invoked by the name configured in `.claude/pv-context.json`'s `framework.skills.mockups` (by default, this same skill).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5-beta3
  uses: []
---

# pv-internal-mockups-html

A single, shared procedure to generate the visual mockup (`design_*.html`) of a new or modified UI element, as self-contained static HTML/CSS/SVG. Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**Language.** This skill doesn't talk to the user. The mockup's sample text/content follows `framework.changes.language` (default `interaction.language`, English if neither is configured) — the caller tells it, or it resolves it itself by reading `.claude/pv-context.json`.

**This skill doesn't decide which elements need a mockup, nor validate anything with the user.** That's always decided by the caller (typically `pv-new`/`pv-fix`, upon detecting the change has a visual component): this skill is only invoked once it's already known that generating or editing at least one HTML mockup is needed, never "just in case". Presenting the result to the user for confirmation is also the caller's responsibility.

This skill is specifically for **HTML** mockups. If a project configures another skill in `framework.skills.mockups` to use a different technology (e.g. Figma, a component library, images), that alternative skill must fulfill the same input/output contract described here so it can replace this one without `pv-new`/`pv-fix` needing to change anything.

## Expected input from the caller

- **Destination folder**: the path where the files should live, normally `{changesDir}/inProgress/{xxxx}/`.
- **List of visual elements**, one per mockup to create or edit. For each element:
  - **Brief description** of the element (used for the filename: `design_<element-description>.html`, e.g. `design_deck-selection-modal.html`, `design_progress-bar.html`).
  - **What it should show**: look, layout, sample content relevant to illustrate the result (the caller doesn't need to give low-level detail — exact colors, measurements — if it doesn't have it yet).
  - **Action**: `create` (new file) or `edit` (a `design_*.html` with that name already exists in the destination folder and needs modifying) — in this second case, what changes relative to what's already there.

## Rules for each mockup

Every `design_*.html` file is only a visual mockup, not a functional prototype:

- It must show only the look (layout, styles, iconography) that element would have — no need for real data or logic, static sample content illustrating the result is enough.
- It must have no real functionality: no JavaScript reacting to events, no network calls, no state — at most, purely decorative JS if needed for the visual look.
- It must be self-contained: only HTML, CSS and SVG, all embedded in the file itself (no external files, no CDNs, no imports).
- One file per distinct visual element in the proposal — don't group several different elements into the same `design_*.html` unless the caller asked for them as a single unit.

## Steps

1. For each element in the received list, create (if the action is `create`) or edit (if `edit`) the corresponding `design_<element-description>.html` file in the destination folder, following the rules above. When editing, preserve the rest of the file unrelated to the requested change.
2. Return to the caller, in the same turn, the list of created/edited file paths (one per element). Don't present anything to the user or ask for confirmation — that's the caller's job.
