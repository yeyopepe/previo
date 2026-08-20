---
name: pv-how
description: Analyzes and plans the technical solution for a change/fix already documented in {changesDir}/inProgress — generates a plan.md with the technical solution (or re-analyzes it if one already exists), and if the user confirms, chains the pv-do skill to implement it. Part of the pv-* framework. Trigger: /pv-how <xxxx>, or when the user asks to plan/analyze the technical solution for a change or fix already documented by pv-new/pv-fix.
argument-hint: <xxxx or description of the change/fix to plan>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b10
  uses: [pv-internal-tech-analysis, pv-internal-tech-mermaid, pv-internal-mockups-html, pv-internal-tech-risks, pv-do]
---

# pv-how

Takes an entry already documented by `pv-new`/`pv-fix` at `{changesDir}/inProgress/{xxxx}/` and analyzes its technical solution, writing it down in `plan.md`. If the user confirms they want to implement it now, chains directly to the `pv-do` skill, which is the one that edits the code and moves the folder to `{changesDir}/implemented/{xxxx}/`.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. `plan.md` follows `framework.changes.language` (default `interaction.language`, English if neither is configured) for its prose — headings, section titles, and everything in sections (a)-(f) — except the labels wrapped in `[[[...]]]` in `PLAN.template.md` (**Creation date**, **Risk**), which stay fixed in English always (see the "Marker convention in templates" section of `pv-design.en.md`): write them without the brackets. `pv-status`'s `filter_status.py` parses both literally (`extract_date`/`extract_risk`, reused from `description.md`'s parsing) to build the status report; translating them makes the entry's planned date and risk show up as missing there, silently. The one exception within the risk-factor prose is `pv-internal-tech-risks`' 9 risk factor names: it returns them in English as internal framework vocabulary (see the note in step 3.1) — translate them to `changes.language` yourself when writing section (f), don't leave them in English. When asking `pv-internal-tech-mermaid` for a diagram for `plan.md`, pass it `changes.language` as the target language. If `language` is not configured anywhere, everything is English.

**Source of truth.** The technical documentation (`docs.tech.*`) and the real code are the only source of truth for how the project works today — not what `description.md` implicitly assumes about the implementation, nor memory of previous conversations. Gather that context always by invoking the `pv-internal-tech-analysis` skill (never by reading `framework.docs.tech` yourself raw or exploring code blindly) when analyzing the root cause and designing the solution (step 3), even if you already have an idea of how something works from prior context. The `description.md` or `plan.md` of **other** changes/fixes under `{changesDir}/**` (in `inProgress`, `implemented` or `closed`) also don't count as a source of truth: they're another entry's intent or analysis, not the project's real state — the only other entry's document that's actually relevant here is the one step 0.1 explicitly consults (the max `xxxx` codes, for order verification). If entry `{xxxx}` has a `history.md`, ignore it entirely: it's prompt history for the exclusive use of `pv-new`/`pv-fix` (it can be incomplete or contradictory on purpose), never a source to take into account here — what's current is always `description.md`.

## Documentation format: diagrams before prose

When writing or updating `plan.md`, if what needs describing is a flow, a process with steps/decisions, a sequence of interactions, or a relationship between states or components, invoke (Skill tool) the diagrams skill configured in `.claude/pv-context.json`'s `framework.skills.diagrams` (if not configured, `pv-internal-tech-mermaid`), asking it for a `technical-flow`-type diagram (internal process with steps/decisions) or `technical-sequence`-type (communication between components/actors) depending on what needs representing — ask for both separately if the case has both dimensions. Include the diagram(s) it returns, accompanied by the essential notes, instead of a long paragraph explaining the same thing in prose. Reserve prose for what the diagram can't express (nuances, reasons, one-off exceptions) or for content with no clear flow/relationship structure to represent. Don't draft the Mermaid code yourself.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there. The full schema is at [`../pv-init/schema.json`](../pv-init/schema.json) (read it first if you haven't already this session).

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

`docs.tech.architectureDocDir`, `docs.functional.featuresDocPathDir`, `docs.tech.styleBibleDocDir` and `sourcecodeDir` are optional and used as context in step 3; if not configured, proceed without them (use the repo in general as fallback context).

## 0.1 Pre-check for ordering

Before identifying the change/fix, **always** check that it hasn't slipped ahead of a more recent one:

1. Run [`scripts/get-max-change-codes.py`](scripts/get-max-change-codes.py) from the repo root:

   ```
   python .claude/skills/pv-how/scripts/get-max-change-codes.py
   ```

   Returns a JSON with the highest existing `xxxx` in each of `inProgress`, `implemented` and `closed` (or `null` if that state has no numbered folder yet).

2. Compare those three codes against the `xxxx` about to be planned in this invocation. If the current `xxxx` is **lower** than any of the other three (ignoring `null`s), it means this change/fix was created before another one that has already moved further along the flow (implemented or closed) — warn the user about it.
   - Immediately re-analyze the entry per the rest of this skill (steps 1 onward), without simply accepting whatever was already in `plan.md` if it existed.
3. If the current `xxxx` isn't lower than any of the three, continue with planning normally from step 1.

## 1. Identify the change/fix

If the user, when invoking this skill, gives an `xxxx`, a folder name, or a description of the change/fix, resolve it by searching **only** within `{changesDir}/inProgress/`.

**If they give nothing** (e.g. they invoke `/pv-how` with no arguments): don't assume it refers to the last change/fix mentioned in the conversation nor any other piece of chat context — the only source of truth is `{changesDir}/inProgress/`. List the folders there (their `xxxx` and, if it has one, its `description.md`'s name/summary) and explicitly ask the user which one they want to plan. If there are none, tell them there's no pending change/fix and stop there.

```
These are the pending changes/fixes in `{changesDir}/inProgress/`:
- {xxxx} — {name/summary}
- ...

Which one do you want me to plan?
```

```
There's no pending change/fix in `{changesDir}/inProgress/`.
```

- If you don't find a matching folder within `{changesDir}/inProgress/`, **do nothing further**: if it exists with that `xxxx` under `{changesDir}/implemented/`, tell the user that change/fix is already implemented; if it doesn't exist anywhere, tell them you can't find it and ask for the correct `xxxx` or folder. Don't search or operate on folders outside `{changesDir}/inProgress/`.
- If you find it, that's `{xxxx}` and its folder `{changesDir}/inProgress/{xxxx}/` for the rest of the process.

## 1.1 Validate the change's documents before analyzing

Before gathering technical context or writing `plan.md`, read `{changesDir}/inProgress/{xxxx}/`'s `description.md` (and, if they exist, its `design_*.html`/`design_*.txt`/`design_navigation_*.md`/`design_data_*.md`) looking for inconsistencies or problems: requirements that contradict each other, contradictory information between `description.md` and the mockups/data tables, ambiguous steps or acceptance criteria, references to elements the mockups don't show (or vice versa), data `description.md` mentions but no `design_data_*.md` table records (or vice versa), gaps that prevent knowing what's being asked.

- **If you find nothing**: continue directly to step 2.
- **If you find something**: don't resolve it on your own nor proceed with the analysis. Lay out the problem to the user clearly (which documents are involved and what the inconsistency or gap consists of) and ask them how to resolve it.

  ```
  Before analyzing the technical solution, I found the following in `{xxxx}`'s documents:
  - {inconsistency or problem 1}
  - ...

  How should we resolve it?
  ```

  With the user's answer, update the affected definition document(s) yourself (`description.md` and/or the `design_*` ones) so they're consistent before continuing. If the fix requires generating or editing a visual mockup, invoke (Skill tool) the skill configured in `.claude/pv-context.json`'s `framework.skills.mockups` (if not configured, `pv-internal-mockups-html`) instead of editing the mockup's HTML/ASCII yourself. Repeat this validation on the now-corrected documents before considering the step done.

## 2. Check whether `plan.md` already exists

- **If `{changesDir}/inProgress/{xxxx}/plan.md` already exists**: use `AskUserQuestion` to ask the user whether they want to re-analyze the solution (regenerate `plan.md` from scratch, overwriting it — go to step 3) or implement directly what the current `plan.md` already says (go to step 3.1 without regenerating it).
- **If it doesn't exist**: go to step 3.

## 3. Analyze and write `plan.md`

1. Read the entry's functional document (`{changesDir}/inProgress/{xxxx}/description.md`, generated by `pv-internal-workflow`) to understand what's being asked. That document's **Type** field indicates whether it's a `fix` or a `change`.
   - **If it's a `fix`**: the analysis and solution must be strictly limited to correcting the documented bug — identify the minimal root cause and the smallest change that fixes it. Don't broaden scope, refactor, or touch code unrelated to the root cause, even if you see it could be improved along the way. If while analyzing you spot something broader that's needed or would help, note it as out of scope in the plan's section (a) instead of including it in the solution.
   - **If it's a `change`**: this restriction doesn't apply; the solution can have whatever scope the change requires.
2. If there are `{changesDir}/inProgress/{xxxx}/design_*.html` files (visual proposal generated by `pv-new`/`pv-fix`), open them, but treat them **only as visual reference** — take from them only the look they illustrate (layout, styles, iconography) for the elements they cover. The technical solution **must not be based on them** in any other sense: don't reuse or literally translate their HTML/CSS/SVG, their classes, or their markup structure, nor take them as a reference for architecture, components to create/reuse, or any other implementation decision — you decide all of that from the project's real code (step 5 in this section), exactly as if those files didn't exist.
3. If there are `{changesDir}/inProgress/{xxxx}/design_data_*.md` files (functional data definition generated by `pv-new`/`pv-fix`), treat them as **the source of truth for what data is needed** (which properties or fields, not how they're represented in code today): they're the mandatory starting point for deciding the real technical structure (types, where it's stored, how it's manipulated) when designing the solution — a decision that is indeed yours to make, unlike `design_*.html`'s visual look.
4. If there are technical doubts about how to approach it, resolve them with the user before writing the plan.
5. Gather additional context by invoking the `pv-internal-tech-analysis` skill (Skill tool), passing it a summary of the root cause or the change to design: it reads the technical documentation configured in `framework.docs.tech` first and only explores code (`sourcecodeDir`) if more information is needed to fill gaps, returning the gathered context and any inconsistency it detects between documentation and code (remember: in that case the code rules). If it reports any inconsistency, take it into account when designing the solution and when writing the plan's sections (c)/(d) (step 6) so it's reflected in the documentation update `pv-do` will do after implementing.
6. Write `{changesDir}/inProgress/{xxxx}/plan.md` following this skill's [`PLAN.template.md`](PLAN.template.md) template, starting with the **Creation date** field (`YYYY-MM-DD` format, today's date at the moment this `plan.md` is created — if it already exists because it's being regenerated, update it to this regeneration's date), followed by these sections. **Don't write the header's `**Risk**` field yet in this save** (not even with a placeholder value like "pending"/"TBD") — it's added in step 3.1, right after, because `pv-internal-tech-risks` needs this same `plan.md` already written as input:
   - **(a) Functional notes** — what's explicitly left out of scope, and the doubts resolved with the user (question and answer, briefly).
   - **(b) Technical solution** — a checklist (`- [ ]`) of concrete, explained tasks (what needs to be touched, where, and why), in the order they should be implemented, all unchecked when the plan is written. Don't mix manual verification steps in here — those go in (e).
   - **(c) Architecture changes** — *only if applicable*: if `docs.tech.architectureDocDir` is configured and this solution modifies the project's core architecture, state **which specific file(s)** in that folder need updating (there may be several candidates) and what needs to change in each. If it doesn't apply (no `docs.tech.architectureDocDir`, or the solution doesn't touch architecture), omit this section entirely — don't leave it empty or with "N/A".
   - **(d) Style changes** — *only if applicable*: if `docs.tech.styleBibleDocDir` is configured and this solution modifies or extends the project's visual style, state **which specific file(s)** in that folder need updating and what needs to change in each. If it doesn't apply, omit this section — don't leave it empty or with "N/A".
   - **(e) Verification** — a checklist (`- [ ]`) of observable results from the already-changed system, to check *after* completing all of section (b). Each item is written self-contained (what to do and what you should see), without referring back to a task number from (b) — a check may depend on several tasks at once, or be shared among several. Always include it unless the solution has no observable behavior to check.

## 3.1 Assess the change's risk

**Mandatory step, don't skip or postpone it.** Immediately after writing `plan.md` in the previous step (still without the `**Risk**` field), invoke the `pv-internal-tech-risks` skill (Skill tool) in this same turn, passing it the entry's `plan.md` and `description.md` — it's only invoked at this point, never before the technical solution is decided, because that's when there's enough information to assess risk. It returns the list of the 9 factors scored (0-10) and the final median.

Now edit `plan.md`'s header to add, right below **Creation date**, the field `**Risk**: {median}/10 — {description}`, where `{description}` is the "Meaning" text matching that median per the template's table (e.g. `5/10 — Moderate risk`). Don't show or write the 9 factors' detail at this point — only the median and its description.

**Check before continuing:** don't consider `plan.md` finished, nor move to step 3.2, without having confirmed the header already has the `**Risk**` field with a real value (never a placeholder, "pending", "TBD" or similar, and never the header without that field).

If at any later point (in this same conversation or when resuming the entry) the user asks for the risk detail, show it to them in chat (the list of the 9 factors with their value, plus the median) and also add that same table to `plan.md` in a new **(f) Risk analysis** section, at the end of the document — reuse `pv-internal-tech-risks`' result if you still have it in this same conversation's context; if not, invoke the skill again.

## 3.2 Ask whether to implement

With `plan.md` already written, ask the user if they want to implement it now.

```
The plan is written at `{changesDir}/inProgress/{xxxx}/plan.md`. Do you want me to implement it now?
```

- If they say yes, invoke the `pv-do` skill (Skill tool) directly on that same `xxxx` — don't ask the user to invoke it separately: continue chaining that flow yourself (implementation → documentation update → move to `implemented`), as `pv-do` defines it.
- If they say no, stop here: the change/fix stays documented and planned at `{changesDir}/inProgress/{xxxx}/`, pending implementation later (it can be resumed by invoking `pv-do` directly on that `xxxx`, or by invoking this same skill again if it's worth reviewing the plan first).

Don't implement anything yourself nor touch code directly — `pv-do` always does that, to keep a single place with that logic.
