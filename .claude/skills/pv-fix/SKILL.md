---
name: pv-fix
description: Analyzes a bug/broken behavior or a very small, almost-zero-analysis change (typo, tweaking a value/constant, text, a one-off style tweak...) requested by the user. If the analysis reveals it's trivial (bug or not), it applies and documents it directly in the same turn, without going through `plan.md`. If it's not trivial and it's a bug, documents it in {changesDir}/inProgress and implements it by chaining pv-how (which in turn chains pv-do), with the analysis strictly scoped to the fix. If it's not trivial and not a bug (new functionality or a major intentional change), warns and invokes pv-new instead. Trigger: /pv-fix, or when the user explicitly asks for "a fix"/to fix a bug, or "something quick"/"a fast one" for a trivial change or fix.
argument-hint: <description of the bug or change to apply>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b8
  uses: [pv-internal-workflow, pv-internal-tech-analysis, pv-internal-mockups-html, pv-internal-tech-mermaid, pv-new, pv-how]
---

# pv-fix

Analyzes, documents and implements a fix (broken behavior) on the project, and is also the `pv-*` framework's fast path for **very small, almost-zero-analysis** changes (a typo, a piece of text, a one-off value/constant, an isolated style tweak — whether or not they're a bug). For new functionality or non-trivial intentional changes use the `pv-new` skill, not this one. Part of the `pv-*` framework.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation, including the fixed messages below. `description.md` (and its `## Applied changes` section in the fast-track branch) and the sample text inside `design_*.html`/`design_data_*.md` follow `framework.changes.language` (default `interaction.language`, English if neither is configured) — `description.md`'s own `[[[...]]]`-marked field labels are `pv-internal-workflow`'s concern (which actually writes the file, including in the fast-track branch): see its "Language." note. `## Applied changes` itself isn't marked in any template — it's free-text prose you write directly, and follows `changes.language` like the rest. If `language` is not configured anywhere, everything is English.

A non-trivial fix is, by nature, a scoped change: the analysis and solution must focus **solely and exclusively on correcting the reported bug**, with the smallest possible change. No taking the opportunity to refactor, rename, or touch code unrelated to the root cause — if that's needed, it's a separate `pv-new`.

**Never use git destructively nor commit without permission.** This skill's fast-track branch edits code directly, but that doesn't authorize going further:

- Don't run `git commit` (nor `git add` followed by commit) unless the user explicitly asked for it in this turn. Finishing the change is not implicit authorization to commit.
- Don't run `git restore`, `git checkout -- <file>`, `git reset`, `git clean`, or any other command that discards changes in the working tree, even if the affected file seems unrelated to this fix. If you see changes from other work in progress (yours or the user's) that you don't want to include, say so and ask how to proceed — don't discard them yourself.

**First assess whether the change is trivial.** Before deciding how to handle it, this skill always checks whether the request qualifies as "fast" (see step 2). If it qualifies, it's applied and documented as already implemented in the same turn, without going through `{changesDir}/inProgress/` with `plan.md` nor chaining `pv-how`/`pv-do`. **This isn't a shortcut to skip analysis for something that actually needs it** — it's only for what truly requires none. If you have reasonable doubts about whether it qualifies, don't force it: treat it as not qualifying.

If the request isn't trivial:
- If it's a bug, follow this skill's normal flow (document + chain `pv-how`/`pv-do`).
- If it's not a bug (new functionality or an intentional behavior modification that isn't trivial), this skill doesn't take it on: warn the user and invoke `pv-new` with the request as-is, so it starts its own definition process.

For a non-trivial fix, this skill implements nothing itself: it documents the intent and directly chains the `pv-how` skill, which analyzes the technical root cause and writes `plan.md`, and which in turn (if confirmed) chains `pv-do` to implement.

**Mockups and diagrams are the central axis of a non-trivial fix's definition, not an optional add-on.** Whenever the fix allows it, the expected behavior must be pinned down with a visual representation — not just prose — and that representation must be **validated by the user**, not just generated. Valid cases (not mutually exclusive): **visual or style changes** → HTML mockup(s) (`design_*.html`, step 4); **broken flows or interactions** (a sequence of steps, a state transition) → a Mermaid diagram inside `description.md` (step 3); **data with its own structure** (the fix defines or uses something that needs a list of properties or associated data) → data table(s) (`design_data_*.md`, step 4.1). Only skip all three if the fix truly has no representable visual, flow, or structured-data dimension. A fast-tracked (trivial) change never generates mockups, diagrams, or data tables — by definition it has no design decision to pin down.

**Source of truth.** To distinguish what the project actually does today from what the user believes it does, the only source of truth is the technical documentation and the real code — not assumptions or conversation memory. To gather that context, invoke the `pv-internal-tech-analysis` skill (Skill tool) passing it a summary of what's being analyzed, instead of reading `framework.docs.tech` yourself or exploring the code blindly: it reads the configured technical documentation first and explores code only if needed, returning the gathered context and any inconsistency between documentation and code (in that case the code rules). If it detects any inconsistency, note it in **Technical notes** when documenting (non-trivial fix, step 3) or take it as a reason not to qualify as trivial (step 2). The content of other changes/fixes under `{changesDir}/**` (their `description.md` or `plan.md`, whether in `inProgress`, `implemented` or `closed`) also doesn't count as a source of truth: they're another entry's intent or analysis, not the project's real state.

## 0. Check that the framework is initialized

If `.claude/pv-context.json` doesn't exist at the repo root, or is missing the `framework` section (or fields of it that are needed), don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

## 1. Understand the request at the functional level

If there's ambiguity about which behavior is correct (for a bug) or exactly what needs to change (for a small change), ask. There's no need to locate the root cause in code yet — if the change turns out not to be trivial, `pv-how` does that when analyzing the fix in detail.

## 2. Assess whether the change is "fast"

Invoke the `pv-internal-tech-analysis` skill (Skill tool) passing it a summary of the request, to gather the necessary technical context (it reads the configured `framework.docs.tech` documentation first, and only explores code if needed). With that context gathered, assess the request against these criteria — to qualify as `fast` it must meet **all** of them, whether or not it's a bug:

- What needs to change is unambiguously clear from a single read of the request — no relevant information is missing and no design or scope decision needs to be made. If applying it would require asking the user quite a bit, it's not `fast`.
- It touches few files, in a very localized way (a constant, a piece of text, a value, a style rule, a one-off condition, a typo). If it affects more than 3 files, it's not `fast`, however small the change in each one.
- If the change carries 0%-10% risk for the rest of the application (it doesn't modify any function's interface, or modifies it while fully guaranteeing backward compatibility; doesn't change any response; doesn't change any flow; doesn't change any value used by other parts of the application besides the one being modified), it's `fast`.
- It doesn't introduce new behavior nor change an existing flow or interaction — at most it adjusts a value, text, or aspect of something that already exists.
- It has no relevant edge cases to analyze, nor does it affect how different parts of the project coexist with each other.
- If it's a bug: it's nowhere close to one whose root cause needs investigating — if digging is needed to find out why something fails, it's not `fast` (but it's still a fix: go to step 3).
- If the change affects **`docs.tech.architectureDocDir`** or **`docs.tech.styleBibleDocDir`** (if configured in `.claude/pv-context.json`) only in constant or parameter values, it's `fast`.
- If the change affects **`docs.tech.architectureDocDir`** or **`docs.tech.styleBibleDocDir`** (if configured in `.claude/pv-context.json`) in a meaningful way (an architecture decision, a visual/interaction/writing style convention), it's not `fast`, even if the code change itself is small. If `pv-internal-tech-analysis` reports any inconsistency between those documents and the code, it also doesn't qualify as `fast`: an inconsistency with the technical documentation is, by definition, something that affects those documents.
- If the change affects **`docs.functional.*`** it's not `fast`.

Illustrative examples that would qualify: fixing a text or typo, changing a one-off color/size/margin, adjusting a constant's or config's value, fixing a misspelled link or path, renaming a visible label, or an obvious at-a-glance bug (e.g. an inverted condition in a single spot).

Examples that would **not** qualify (even if the user asks for them as "quick"): any new functionality, any change that alters how something behaves (not just its look/value), any fix whose cause isn't obvious at a glance, any change touching more than 2 files or several related flows/components, any change affecting architecture or the style bible.

If you have reasonable doubts about whether it qualifies, don't force it: treat it as not qualifying.

**If it qualifies as `fast`**, go to the "Fast-track branch" section below — don't continue with this skill's remaining numbered steps.

**If it doesn't qualify:**
- And it's a bug (even if it didn't qualify as `fast` because of its root cause, it's still a fix): continue with step 3.
- And it's not a bug (new functionality or an intentional behavior modification): warn the user explicitly stating which criterion isn't met, and then, without waiting for further confirmation, directly invoke the `pv-new` skill (Skill tool) passing it the user's request as-is, so it starts its own definition process at `{changesDir}/inProgress/`. Don't continue with this skill's remaining steps: from here on `pv-new` continues the process.

  ```
  This doesn't qualify as a "fast" change nor is it a bug: {specific unmet criterion}. I'll document it with `pv-new` to analyze and plan it properly.
  ```

## 3. Document the intent (non-trivial fix)

Invoke the `pv-internal-workflow` skill (Skill tool) with `action=create`, `type=fix`, the functional summary of what's wrong and what's expected instead, and `promptOriginal` (the request exactly as the user wrote it, without rephrasing), so it can number the fix and create `description.md` and `history.md` at `{changesDir}/inProgress/{xxxx}/`.

If the functionality being described involves a flow, a sequence of steps/decisions, or an interaction between states or components from the user's point of view (e.g. how a screen transitions, the order of an operation, chained edge cases), invoke (Skill tool) the diagrams skill configured in `.claude/pv-context.json`'s `framework.skills.diagrams` (if not configured, `pv-internal-tech-mermaid`), asking it for a `functional`-type diagram per distinct use case or user story that has that flow — never mix several into the same diagram. Include the diagram(s) it returns, along with the essential notes, when passing this to `pv-internal-workflow`, instead of only describing it in prose — that's how it ends up in `description.md`. Use prose when there's no clear flow/relationship to represent.

## 4. Generate the visual proposal (non-trivial fix)

If the change has a visual component (there's something to say for step 1's "High-level visual definition" point), invoke (Skill tool) the mockups skill configured in `.claude/pv-context.json`'s `framework.skills.mockups` (if not configured, `pv-internal-mockups-html`), passing it the destination folder (`{changesDir}/inProgress/{xxxx}/`) and, for each distinct visual element in the proposal, its description and what it should show (e.g. one element for the deck-selection modal, another for the progress bar), marking the action as `create`. Note the `design_*.html` paths it returns. If the change has no visual component (internal logic, data, backend), skip this step entirely — don't invoke the mockups skill "just in case".

## 4.1 Define the necessary data (non-trivial fix)

If the fix defines or uses something that needs a list of properties or associated data (an object's properties, a database table's content, a configuration's fields, etc.), write one or more `design_data_<description>.md` files directly at `{changesDir}/inProgress/{xxxx}/` — one per clearly distinct entity or data set. Each file contains one or more Markdown tables listing that data (suggested columns: data name, functional description, required/possible values as applicable). It's **a functional definition of what data is needed**, not of how it's stored or manipulated — `pv-how` decides that afterward from this table. If the fix needs no list of properties or structured data, skip this step entirely.

## 5. Validate the visual representation with the user (non-trivial fix)

If step 3 included a Mermaid diagram, step 4 generated a `design_*.html`, or step 4.1 generated a `design_data_*.md`, present them to the user (path of each `design_*.html`/`design_data_*.md` and the diagram) and ask them to confirm whether they reflect the expected behavior or what they'd change, before chaining to planning. If they ask for changes, adjust and present it again until they confirm. If the fix didn't generate any diagram, `design_*.html`, or `design_data_*.md`, skip this step.

## 6. Chain the planning (non-trivial fix)

Invoke the `pv-how` skill (Skill tool) directly on that same `xxxx`, explicitly stating that it's a fix and that its analysis and solution must be strictly limited to correcting the documented bug — minimal change, without broadening scope or touching anything unrelated to the root cause. Don't ask the user to invoke `pv-how` separately: continue that flow yourself (analysis → `plan.md` → confirmation → `pv-do` implements → moves to `implemented`), as `pv-how` defines it.

Don't write the fix document yourself nor compute the `xxxx` number — `pv-internal-workflow` does that, to keep a single place with that logic. `design_*.html` files are generated by the configured mockups skill (`pv-internal-mockups-html` by default) — don't write them yourself. Step 3's Mermaid diagram code is generated by the configured diagrams skill (`pv-internal-tech-mermaid` by default) — don't draft it yourself either. `design_data_*.md` files (step 4.1), however, you do write directly yourself — they're not the responsibility of any internal skill. Don't write `plan.md` yourself nor touch code directly — `pv-how` and `pv-do` do that, to keep a single place with that logic.

## Fast-track branch (trivial change, bug or not)

If step 2 concluded the change is `fast`, follow these steps instead of the ones above:

1. **Document the intent.** Invoke the `pv-internal-workflow` skill (Skill tool) with `action=create`, `type=fast`, the functional summary of what's being asked (what was wrong or what text/value/style is being adjusted) and `promptOriginal` (the request exactly as the user wrote it, without rephrasing), so it can number the entry and create `{changesDir}/inProgress/{xxxx}/description.md` and `.../history.md`. Note the `xxxx` it returns.
2. **Apply the change.** Implement the change directly in the code with your normal engineering process (edit, verify it compiles/tests pass if there are any). It's still a real change to the project: apply it with the same care as any other edit, even though it doesn't go through `plan.md`.

   A `fast` change must **never** touch `docs.tech.architectureDocDir` or `docs.tech.styleBibleDocDir` (see step 2 above) — don't update them, nor `docs.functional.featuresDocPathDir`, as part of this branch. If during implementation you discover that architecture or the style bible really does need touching, or that the change spreads to more files than expected, that's a sign the change wasn't so trivial after all: stop immediately, don't apply it halfway (undo whatever you already touched if you got that far), and instead follow step 3 (if it's a bug) or the warning + invoking `pv-new` (if it's not) described in step 2 above.
3. **Document the change already applied.** Add a new section at the end of the `description.md` created in point 1, `## Applied changes`, with a brief technical detail of what was touched (files and what changed in each).
4. **Move the entry to `implemented`.** Invoke the `pv-internal-workflow` skill (Skill tool) with `action=move`, the `xxxx` from point 1, `from=inProgress` and `to=implemented` — don't move the folder yourself.
5. **Confirm to the user.** State what was implemented and the documentation file's path (`{changesDir}/implemented/{xxxx}/description.md`).
