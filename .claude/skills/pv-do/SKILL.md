---
name: pv-do
description: Implements a change/fix whose plan.md is already written at {changesDir}/inProgress/{xxxx}/ — edits the code per the technical solution, updates the synced documentation, and moves the entry to {changesDir}/implemented. Part of the pv-* framework. Trigger: /pv-do <xxxx>, or when the user asks to implement a change/fix already planned by pv-how (normally chained automatically from it).
argument-hint: <xxxx of the already-planned change/fix>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b11
  uses: [pv-internal-workflow, pv-internal-doc-features, pv-internal-doc-technical]
---

# pv-do

Takes an entry from `{changesDir}/inProgress/{xxxx}/` whose technical solution is already written in `plan.md` (by the `pv-how` skill) and carries it through to implemented: edits the code, updates the synced documentation, and moves the folder to `{changesDir}/implemented/{xxxx}/`.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. When updating `docs.functional.featuresDocPathDir` (via `pv-internal-doc-features`), use `docs.functional.language`; when updating `docs.tech.architectureDocDir`/`styleBibleDocDir`, use `docs.tech.language` (fallback `interaction.language` in both cases) — **not** `changes.language`, even though the source (`plan.md`) is in another language: translating the content when writing it into the final reference document is your responsibility. In the legacy single-file case (step 2.2) where you write `FEATURES.template.md` yourself, the labels wrapped in `[[[...]]]` there (`Available in`, `Code`) stay fixed in English always — write them without the brackets (see the "Marker convention in templates" section of `pv-design.en.md`); `migrate-legacy-features-doc.py` parses `**Available in**` literally when the project later migrates to a folder. If `language` is not configured anywhere, everything is English.

**Source of truth.** This entry's `plan.md` is the guide for what to implement. If during implementation something doesn't line up with the real code, the code rules — stop and tell the user instead of improvising a different solution without telling them (see step 2). If the entry has a `history.md`, don't open it: it's prompt history for the exclusive use of `pv-new`/`pv-fix`, never information to take into account when implementing or documenting (step 2.1), and reading it would only spend context without adding anything.

**Never use git destructively nor commit without permission.** This skill edits code/documentation files and moves the change's folder (step 3), but never goes further on its own:

- Don't run `git commit` (nor `git add` followed by commit) unless the user explicitly asked for it in this turn. Finishing the implementation is not implicit authorization to commit.
- Don't run `git restore`, `git checkout -- <file>`, `git reset`, `git clean`, or any other command that discards changes in the working tree, even if the affected file seems unrelated to this entry. If running `git status`/`git add` shows changes from other work in progress (yours or the user's) that you don't want to include, say so and ask how to proceed — don't discard them yourself.
- If you need to check the repo's state (`git status`, `git diff`), do it only to verify your own work, never as a step before cleaning up or discarding files you haven't touched in this implementation.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

`docs.tech.architectureDocDir`, `docs.functional.featuresDocPathDir` and `docs.tech.styleBibleDocDir` are optional and used in step 2.1; if not configured, skip the corresponding updates without asking anything.

## 1. Identify the entry to implement

If the user, when invoking this skill, gives an `xxxx`, a folder name, or a description of the change/fix, resolve it by searching **only** within `{changesDir}/inProgress/`, and check that it has `plan.md`:

- If the folder exists but does **not** have `plan.md` yet: don't continue. Tell the user that entry doesn't have a planned technical solution yet and that `pv-how` must be invoked on that `xxxx` first.
- If you don't find a matching folder within `{changesDir}/inProgress/`: if it exists with that `xxxx` under `{changesDir}/implemented/`, tell the user that change/fix is already implemented; if it doesn't exist anywhere, tell them you can't find it and ask for the correct `xxxx` or folder.

**If they give nothing** (e.g. they invoke `/pv-do` with no arguments): don't assume it refers to the last change/fix mentioned in the conversation nor any other piece of chat context. List only the `{changesDir}/inProgress/` folders that already have `plan.md` (ready to implement) — their `xxxx` and, if it has one, its `description.md`'s name/summary — and explicitly ask the user which one they want to implement. If none has `plan.md` yet (even if there are unplanned entries in `inProgress`), tell them there's no change/fix ready to implement and that it needs to be planned with `pv-how` first.

```
These changes/fixes already have `plan.md` and are ready to implement:
- {xxxx} — {name/summary}
- ...

Which one do you want me to implement?
```

```
There's no change/fix with `plan.md` ready to implement. Use `pv-how` first to plan one of the pending ones in `{changesDir}/inProgress/`.
```

Once identified, that's `{xxxx}` and its folder `{changesDir}/inProgress/{xxxx}/` for the rest of the process.

## 2. Implement

Implement everything `plan.md` says. Its checklists (`(b)` and, if present, `(e)`) are the only reliable task list — don't trust what you remember from reading them earlier, go box by box:

- Go through section **(b) Technical solution** **one task at a time, in order**: implement that specific task (edit code, verify it compiles / tests pass if there are any) and, right after considering it done, edit `plan.md` marking that box as `- [x]` before moving to the next. Don't implement several tasks in a row and mark them all at the end — marking immediately is what avoids skipping one without noticing.
- If `plan.md` has section **(c) Architecture changes**, apply those changes to the `docs.tech.architectureDocDir` file(s) that section names, as part of this implementation.
- If `plan.md` has section **(e) Verification**, once every box in (b) is checked, go through each item in (e) **one at a time** and verify the described observable result truly holds (by reading the resulting code/DOM/styles, not assuming the (b) task that produces it went fine). Check its box `- [x]` only once you've verified it this way. If an item doesn't hold, fix it before checking it off — don't consider it done nor mention it to the user as pending.
- **Before moving to step 3**, reread the entire `plan.md` looking for unchecked `- [ ]` boxes in (b) or (e). If you find any, that task or check was left pending without you noticing: complete it now, don't ignore it or treat it as implicit.

If during implementation you discover the plan isn't viable as written, stop and tell the user instead of improvising a different solution without telling them.

## 2.1 Update documentation after implementing

Once the above is implemented in code, always update the following before moving the folder:

- **`docs.tech.architectureDocDir`/`styleBibleDocDir` writing style.** Before drafting or editing any content for either of the two points below, invoke `pv-internal-doc-technical` (Skill tool, no parameters) to load its writing rules and follow them for whatever you write in this step — these documents are read by AI (`pv-internal-tech-analysis`, future `pv-do`/`pv-how` cycles), not by a human, so they favor dense fact fragments over explanatory prose. Skip this invocation only if neither `architectureDocDir` nor `styleBibleDocDir` is configured.
- **`docs.tech.architectureDocDir`** — if configured, review the file(s) in that folder matching the touched area and make sure they faithfully reflect the resulting technical state. Apply whatever section (c) of the plan says if it had one; if it didn't but implementation turned out to touch something that folder describes, update it anyway — it doesn't depend solely on the plan having anticipated it. If the solution introduces a new topic that doesn't fit any existing file in that folder, create a new one with the next free number (`NN-slug.md`, without reusing or renumbering existing ones) and add it to `INDEX.md`'s index table. If not configured, skip this point without asking anything. **Write it in `docs.tech.language`** (fallback `interaction.language`), never in `changes.language` — even if `plan.md` (your source) is in a different language, draft this content fresh in the target language, don't carry over its sentences verbatim.
- **`docs.functional.featuresDocPathDir`** — if configured, it's **functional** documentation, not a changelog: it describes what the app can do today, organized by functional area/module, not a chronological list of changes/fixes. In either of the two cases below, if what was implemented extends or modifies a feature that already has its own entry, **edit it in place** so it keeps faithfully describing the current behavior (never add a new entry for the same thing), adding this entry's `xxxx` to its **Code** field; if it's a new feature, create an entry in the matching functional area (create the area if it doesn't exist yet) with this entry's `xxxx` in **Code**. **Write it in `docs.functional.language`** (fallback `interaction.language`), never in `changes.language` — even when the two happen to coincide (so translation isn't needed), draft the body fresh in that language rather than copying phrasing straight from `description.md`/`plan.md`.
  - **Functional diagrams.** If this entry's `description.md` contains a **functional** Mermaid diagram (the ones generated in `pv-new`/`extend-entry.md`'s step 2), or the entry's folder has one or more `design_navigation_*.md` (UI navigation diagrams — `pv-new` may have generated several, one per distinct use case), and any of those diagrams represents a flow of the feature you're documenting here, carry it over to the feature entry too — as-is, without rewriting it. If two or more of those diagrams reference each other (e.g. one says "see diagram 1" or names a state/node defined in another file), always carry them over together, all or none — never include a diagram that references another without that other one too, to avoid leaving a broken reference in the feature documentation. **Never** carry over technical diagrams (`plan.md`'s: technical flow, technical sequence, nor `docs.tech.architectureDocDir`'s) — those are internal implementation, not user-facing. If the feature entry already had its own diagrams from a previous version of the feature, keep them unless this change leaves them outdated (in that case, replace them with the new ones instead of accumulating both).
  - **If `featuresDocPathDir` is a folder** (the recommended convention — check by seeing whether it exists as a directory, or if it doesn't exist yet but the value doesn't end in `.md`): invoke the `pv-internal-doc-features` skill (Skill tool) with `action=find` and a brief description of the implemented feature, to know whether it already has its own file. Draft the final content (body, functional diagrams per the previous point, `Available in`, full `Code` list) yourself with the criteria above, and save it by invoking `pv-internal-doc-features` with `action=upsert` (passing `diagrams` only if there's one to include) — passing `existing_file` if `find` returned a match, or omitting it if it's a new entry.
  - **If `featuresDocPathDir` is a single file** (projects that haven't migrated to a folder yet): edit it yourself with the same criteria (including functional diagrams), using this skill's [`FEATURES.template.md`](FEATURES.template.md) as the template for a new entry; create it from that template if it doesn't exist yet.
  - If `docs.functional.featuresDocPathDir` isn't configured, skip this point without asking anything.
- **`docs.tech.styleBibleDocDir`** — if configured, review the matching file(s) in that folder and update them if what was implemented introduces or modifies style conventions (visual, interaction, writing, etc.) relevant to the project. Same as with `architectureDocDir`, if the topic doesn't fit any existing file create a new one with the next free number and add it to `INDEX.md`'s index table. If not configured, or what was implemented doesn't affect any style convention, skip this point without asking anything. **Write it in `docs.tech.language`** (fallback `interaction.language`), same rule as `architectureDocDir` above.

## 3. Move the folder to `implemented`

Invoke the `pv-internal-workflow` skill (Skill tool) with `action=move`, `xxxx`, `from=inProgress` and `to=implemented` — don't move the folder yourself.

## 4. Confirm to the user

State what was implemented, which documentation was updated (`docs.tech.architectureDocDir`/`docs.functional.featuresDocPathDir`/`docs.tech.styleBibleDocDir`, as applicable), and that the folder was moved to `{changesDir}/implemented/{xxxx}/`.
