---
name: pv-new
description: Analyzes and documents an intentional change (new functionality or a deliberate modification to existing behavior, not a bug) requested by the user, leaving it ready in {changesDir}/inProgress to plan and implement later with pv-how. If a code already in inProgress is given, it extends that entry instead of creating a new one. With `/pv-new todo <code>` it starts from an idea already noted in {changesDir}/todo/ instead of a new request, and deletes that idea automatically when done (without asking for confirmation). Trigger: /pv-new [xxxx], or when the user explicitly asks for "a change"/"document this change" as part of the project's workflow.
argument-hint: "[xxxx | todo <code>] <description of the change>"
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5-beta1
  uses: [pv-internal-workflow, pv-internal-tech-analysis, pv-internal-mockups-html, pv-internal-tech-mermaid, pv-how]
---

# pv-new

Analyzes and documents an intentional change to the project (new functionality or a deliberate modification to existing behavior — for bugs use the `pv-fix` skill, not this one). Part of the `pv-*` framework.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. `description.md`, `design_navigation_*.md`, and the sample text inside `design_*.html`/`design_data_*.md` follow `framework.changes.language` (default `interaction.language`, English if neither is configured). If `language` is not configured anywhere, everything is English.

**It implements nothing.** This skill only understands and documents the functional scope of what's being asked; the technical solution is done afterward by the `pv-how` skill, and the implementation by the `pv-do` skill, once it's decided to plan/implement this entry.

**Mockups and diagrams are the central axis of a change's definition, not an optional add-on.** Whenever the change allows it, its intent must be pinned down with a visual representation — not just prose — before considering it documented, and that representation must be **validated by the user**, not just generated. There are four valid cases, not mutually exclusive within the same change:
- **New/modified flows or behavior, with no UI dimension** (logic, the order of an operation, decisions, chained edge cases): a functional Mermaid diagram inside `description.md` (step 2) — one per distinct use case or user story, never several mixed into the same diagram.
- **Visual or style changes** (something the user sees/touches on screen appears or is modified): HTML mockup(s) (`design_*.html`, step 3).
- **UI navigation or interaction** (a screen change, a modal or dropdown opening, or any visual state transition triggered by a user action, even if it doesn't leave a single screen): a navigation diagram (`design_navigation_*.md`, step 3).
- **Data with its own structure** (the change defines or uses something that needs a list of properties or associated data — an object's properties, a table's content, a configuration's fields, etc.): data table(s) (`design_data_*.md`, step 3.1).

Only skip all four when the change truly has no representable visual, flow, or structured-data dimension — never by default or to save the step.

**`description.md` vs `history.md`.** `description.md` only records the current outcome of the analysis (what's being asked, how it should behave) — never the user's original prompt nor any other trace of how it got there. That trace lives separately, in `history.md` (see step 2), a file for the exclusive use of `pv-new`/`pv-fix`: the rest of the framework's skills (`pv-how`, `pv-do`, etc.) don't read it or need it, and the prompts it contains can be incomplete or contradictory with each other without that being a problem — they're the history of an analysis process, not the source of truth.

**Source of truth.** When anticipating doubts and proposing answers (step 1), the only source of truth about how the project currently works is the technical documentation and the real code — never assumptions, what's remembered from previous conversations, or what the user believes the code does. To gather that context, invoke the `pv-internal-tech-analysis` skill (Skill tool) passing it a summary of what's being analyzed, instead of reading `framework.docs.tech` yourself or exploring the code blindly: it's in charge of reading the configured technical documentation first and exploring code only if needed, and returns the gathered context and any inconsistency it detects between documentation and code (remember: in that case the code rules, not the documentation). If it detects any inconsistency, note it in **Technical notes** when documenting (step 2) so `pv-how` can take it into account later. The content of other changes/fixes under `{changesDir}/**` (their `description.md` or `plan.md`, whether in `inProgress`, `implemented` or `closed`) also doesn't count as a source of truth: they're another entry's intent or analysis, not the project's real state. Check them before settling on a proposal about coexisting with what already exists.

## 0. Check that the framework is initialized

If `.claude/pv-context.json` doesn't exist at the repo root, or is missing the
`framework` section (or fields of it that are needed), don't continue: tell
the user they must first run the `pv-init` skill to
initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

## 0.1 Check whether the given code is already in progress

If, when invoking this skill, the user gives a change/fix code (`xxxx`) — e.g. `/pv-new 0001 ...` or "add this to change 0001" — check whether that folder exists **exactly** at `{changesDir}/inProgress/{xxxx}/`.

- **If it exists and the user is giving you new information**: it's not a new change, but an extension of that already-in-progress entry. Read and follow [`extend-entry.md`](extend-entry.md) in this same folder in full — don't continue with the steps below.
- **If it exists, but the user isn't adding new information**: it means you should review and re-analyze the change. Possible causes:
   - `description.md` was written a long time ago and new functionality may already have been implemented.
   - The user may have edited `description.md` by hand and introduced changes.
- **If it doesn't exist** (whether or not that `xxxx` is in `implemented`/`closed`, or doesn't exist anywhere): it's a new change with a new code. Continue with the usual process from step 1, ignoring the given code — the real `xxxx` will be computed by `pv-internal-workflow`, don't assume it yourself.
- If no code was given, continue with the usual process from step 1 anyway.

## 0.2 Check whether it's invoked from a `todo/` idea

If the user invokes this skill as `/pv-new todo <code>` (or explicitly asks to "turn idea `<code>` from todo into a change"), this entry doesn't originate from a new request from the user in chat, but from content already noted by `pv-todo`: read and follow [`todo-mode.md`](todo-mode.md) in this same folder in full before continuing.

If it wasn't invoked this way, continue with the usual process from step 1 of "Steps".

## Steps

1. **Understand the scope and anticipate the usual functional doubts.** Don't wait for an obvious ambiguity to come up: before documenting, review the request and the relevant project code to build your own list of points that usually stay undefined in this kind of change. Go over at least:
   - **Edge cases and states**: what happens when empty, on error, while loading, if canceled halfway.
   - **Coexistence with what exists**: whether this replaces, complements, or conflicts with functionality already present in the project.
   - **Data scope**: whether something gets saved, where, and for whom (if the project distinguishes users/games/sessions); what happens on reload or in another session.
   - **Who can use it**: whether the project has roles or modes that restrict the action.
   - **High-level visual definition**: what new elements appear, roughly where on screen they're placed, how they're activated/deactivated, what visual feedback the user perceives when interacting. Low-level detail (exact colors, measurements, specific components to reuse or create) is out of scope for this analysis — `pv-how` resolves that when planning the technical solution.

   For each point relevant to this specific change, don't hand it back to the user raw: propose a reasonable answer yourself based on the project's context and present the full list (point + your proposal) at once so they can confirm or correct where they disagree, instead of asking one at a time. If there's any point you can't even propose a reasonable assumption for, flag it explicitly as an open question within that same list.
2. **Document the intent.** Invoke the `pv-internal-workflow` skill (Skill tool) with `action=create`, `type=change`, the functional summary of what's being asked — including step 1's list of doubts already resolved (confirmed proposals, the user's corrections and, if applicable, the agreed high-level visual definition) — and `promptOriginal` (the request exactly as the user wrote it, without rephrasing), so it can number the change and create `description.md` and `history.md` at `{changesDir}/inProgress/{xxxx}/`. Note the `xxxx` it returns: you need it in the next step.

   If the functionality being described involves a flow, a sequence of steps/decisions, or an interaction between states or components from the user's point of view (e.g. how a screen transitions, the order of an operation, chained edge cases), invoke (Skill tool) the diagrams skill configured in `.claude/pv-context.json`'s `framework.skills.diagrams` (if not configured, `pv-internal-tech-mermaid`), asking it for a `functional`-type diagram per distinct use case or user story that has that flow — never mix several into the same diagram. Include the diagram(s) it returns, along with the essential notes, when passing this to `pv-internal-workflow`, instead of only describing it in prose — that's how it ends up in `description.md`. Use prose when there's no clear flow/relationship to represent.
3. **Generate the visual proposal and the navigation diagram.** If the change has a visual component (there's something to say in step 1's "High-level visual definition" point):
   - **HTML mockups.** Invoke (Skill tool) the mockups skill configured in `.claude/pv-context.json`'s `framework.skills.mockups` (if not configured, `pv-internal-mockups-html`), passing it the destination folder (`{changesDir}/inProgress/{xxxx}/`) and, for each distinct visual element in the proposal, its description and what it should show (e.g. one element for the deck-selection modal, another for the progress bar), marking the action as `create`. Only invoke it when there's actually at least one element to mock up — never "just in case". Note the `design_*.html` paths it returns.
   - **Navigation diagram.** If the change also introduces or modifies UI navigation or interaction (a screen change, a modal or dropdown opening, or any visual state transition triggered by a user action, even if it doesn't leave a single screen):
     1. **List the use cases first, before drawing anything — and write that list as output text to the user, not just as an internal mental step.** Before creating any `design_navigation_*.md` file, publish in your own reply the numbered list of the distinct flows you're going to represent (e.g. "how the selection changes on click/drag" and "what the context menu offers depending on the active selection" are two distinct use cases, even if they share a screen and are related). Two user actions belong to the same use case only if they answer the same question ("how do I navigate between screens/states?"); if one answers "what options does this interaction offer depending on context?" it's a separate use case, even if its final result is a state already represented in the other. Turning this step into visible text (instead of resolving it only "in your head") is intentional: if while drawing a diagram you find yourself mixing actions that answer different questions, that's the sign this list was skipped or left incomplete — go back to it before continuing.
     2. **Create one `design_navigation_<description>.md` file per entry in that list**, directly at `{changesDir}/inProgress/{xxxx}/` — never mix two use cases in the same diagram, even if that means a file has to reference a state/node from another (e.g. "action X leaves navigation in state Y — see file Z") instead of repeating its internal logic. The number of files must exactly match the number of entries in the list published in the previous step.

   If the change has no visual component, skip this step entirely — don't invoke the mockups skill nor create filler `design_navigation_*.md` files.

   Every `design_navigation_*.md` file combines a Mermaid diagram (`stateDiagram-v2` or `flowchart`, whichever best represents that specific use case) with the relevant UI screens/states as nodes and user actions as transitions, plus brief prose notes only for transitions that aren't clear from the diagram itself — don't repeat in text what the diagram already makes clear.
3.1 **Define the necessary data.** If the change defines or uses something that needs a list of properties or associated data (an object's properties, a database table's content, a configuration's fields, etc.), write one or more `design_data_<description>.md` files directly at `{changesDir}/inProgress/{xxxx}/` — one per clearly distinct entity or data set, never mix unrelated entities in the same file. Each file contains one or more Markdown tables listing that data (suggested columns: data name, functional description, required/possible values as applicable — adjust the columns to whatever brings real information in each case). It's **a functional definition of what data is needed**, not of how it's stored or manipulated: nothing about database column types, persistence engines, table/API names, or any other technical decision — `pv-how` decides that afterward from this table. If the change needs no list of properties or structured data, skip this step entirely.
4. **Validate the visual representation with the user.** If step 2 included a Mermaid diagram, or steps 3/3.1 generated any `design_*.html`, `design_navigation_*.md` or `design_data_*.md`, don't consider them final just because they were written: present them to the user (point them to each `design_*.html`/`design_navigation_*.md`/`design_data_*.md`'s path so they can open or review it, and show the Mermaid diagrams) and ask them to confirm whether they reflect what they had in mind or what they'd change.

   ```
   The visual proposal is at {design_*.html paths}, the navigation at {design_navigation_*.md paths}, the necessary data at {design_data_*.md paths} and the flow as a diagram in description.md. Do they reflect what you had in mind, or is there something to change before continuing?
   ```

   If they ask for changes, adjust the file(s) or the diagram and present it again until they confirm. If the change didn't generate any diagram, `design_*.html`, `design_navigation_*.md` or `design_data_*.md`, skip this step.
5. **State the next step.** Tell the user the change is documented (`description.md`) and, if applicable, with its visual and data proposal already validated (`design_*.html`, `design_navigation_*.md`, `design_data_*.md`); to plan and implement it they should invoke the `pv-how` skill on that `xxxx`. If the user wants to implement it right away, you can invoke `pv-how` directly yourself.

Don't write the change document yourself nor compute the `xxxx` number — `pv-internal-workflow` does that, to keep a single place with that logic. `design_*.html` files are generated by the configured mockups skill (`pv-internal-mockups-html` by default) — don't write them yourself. Step 2's Mermaid diagram code is generated by the configured diagrams skill (`pv-internal-tech-mermaid` by default) — don't draft it yourself either. `design_navigation_*.md` and `design_data_*.md` files, however, you do write directly yourself: they're not the responsibility of any internal skill, which are project-agnostic and don't analyze or design anything.

## Extending an entry already in `inProgress`

When step 0.1 detects that the given `xxxx` already exists at `{changesDir}/inProgress/{xxxx}/`, no new entry is created: the existing one is extended. Full procedure in [`extend-entry.md`](extend-entry.md) in this same folder.
