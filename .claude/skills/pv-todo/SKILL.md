---
name: pv-todo
description: Notes and develops loose ideas for later without putting them into the project's workflow — saves them at {changesDir}/todo/{code}/description.md, a separate folder no other pv-* skill uses or takes into account. Works both for jotting down a new idea and for continuing to develop/expand one already noted. Trigger: /pv-todo [code] <idea>, or when the user asks to "note down"/"jot down" an idea for later, without asking for it to be documented as a change/fix.
argument-hint: "[code] <idea to note or develop>"
model: claude-haiku-4-5
effort: medium
metadata:
  version: 0.9.5b5
  uses: []
---

# pv-todo

The `pv-*` framework's idea notebook, but **outside** its workflow: it doesn't document a change/fix to implement, it just keeps a record of an idea to develop later, at a different pace from `pv-new`/`pv-fix`. There's no planning (`pv-how`/`pv-do`), no states (`inProgress`/`implemented`/`closed`), and no version: an idea noted here stays here until, if ever, someone decides to turn it into a real change/fix with `pv-new`/`pv-fix` (outside this skill already).

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. `description.md` follows `framework.changes.language` (default `interaction.language`, English if neither is configured) — except the four markdown headings themselves (`## Idea`, `## Code`, `## Creation date`, `## Notes`), which stay fixed in English always (see step 3: `pv-status`'s scripts parse them literally). If `language` is not configured anywhere, everything is English.

Lives at `{changesDir}/todo/`, a sibling subfolder to `inProgress`/`implemented`/`closed` but **entirely separate** from the rest of the framework: no other `pv-*` skill reads it, writes it, or counts its folders when numbering or looking up changes/fixes. The codes this skill uses have no relation to change/fix's numeric `xxxx` — they're just unique identifiers within `{changesDir}/todo/`.

## 0. Check that the framework is initialized

If `.claude/pv-context.json` doesn't exist at the repo root, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

From here on, `changesDir` is shorthand for `{workFolder}/changes` (a fixed-name subfolder inside `framework.workFolder`, which defaults to `"/"`, the repo root).

## 1. Decide whether it's a new idea or an expansion

If the user gives a code when invoking this skill (e.g. `/pv-todo a3f9k also add...`), check whether `{changesDir}/todo/{code}/` exists **exactly**.

- **If it exists**: it's an expansion of an already-noted idea. Go to the [Expanding an already-noted idea](#expanding-an-already-noted-idea) section.
- **If it doesn't exist**, or no code was given: it's a new idea. Continue to step 2.

If the user doesn't give any content (e.g. they just ask "what ideas do I have noted" or "list the todos"), jump straight to the [Listing noted ideas](#listing-noted-ideas) step without creating or modifying anything.

## 2. Generate a unique code

Generation and collision checking are handled deterministically and for free in tokens by the [`scripts/new-todo-code.py`](scripts/new-todo-code.py) script (standard Python, no external dependencies) — don't do it by hand. Run from the repo root:

```
python .claude/skills/pv-todo/scripts/new-todo-code.py
```

The script reads `workFolder` from `.claude/pv-context.json` (or uses `--work-folder` if you pass it), lists the subfolders already existing under `{changesDir}/todo/` (it doesn't need to exist yet — in that case there's nothing to collide with), generates a short alphanumeric code (`[a-z0-9]`, 5 characters by default, `--length` for a different size) that doesn't match any already there, and prints only that code on stdout. It doesn't check or take into account any other folder in the repo (not `inProgress`/`implemented`/`closed`, nor anything outside `{changesDir}/todo/`): the only uniqueness condition is not repeating within this subfolder. Use that value as-is for the code — don't recompute it by hand.

## 3. Note the idea

Without asking scope questions or proposing answers to functional gaps (that's what distinguishes this skill from `pv-new`/`pv-fix`: here the idea is noted as-is, even if incomplete or just a sketch), create:

```
{changesDir}/todo/{code}/description.md
```

**`description.md`** follows **exactly** the [`description.template.md`](description.template.md) template in this same folder: four markdown headings `## Idea`, `## Code`, `## Creation date` and `## Notes`, in that order, without bold or a trailing `:` on the heading (neither `## Idea:` nor `**Idea:**`) — `pv-status`'s `list_todo.py`/`collect_status.py` parse these headings with a literal regular expression (`^##\s*Idea\s*\n+`) and any variation (bold heading, colon, a different title like "Ide") makes the idea unreadable, showing up as "(no idea)" in `/pv-status todo`. **These four headings stay in English always, regardless of `changes.language`** — only the content under each one follows it.

- **Idea** — short name summarizing the idea.
- **Code** — the code generated in step 2.
- **Creation date** — today's date (`YYYY-MM-DD` format) at the moment this `description.md` is created.
- **Notes** — the idea's content, as the user raised it. Can be a loose sentence, a list of possibilities, open unresolved questions, or any other form the user wants to note it in — don't force `pv-new`/`pv-fix`'s `description.md` structure onto it (there's no separate "Original prompt" or "Full description").

If the idea has a clear visual component and the user wants to record it, you can also create some `design_*.html`, same as `pv-new` does (self-contained mockup, no real functionality) — but it's not mandatory nor this skill's focus; only do it if the user asks or provides that material.

## 4. Confirm to the user

Report the assigned code and the created file's path, and remind them that this idea stays noted at `{changesDir}/todo/` outside the workflow — if it's ever turned into a real change/fix, it needs to be documented again with `pv-new`/`pv-fix` (this skill doesn't do that conversion automatically).

## Expanding an already-noted idea

When step 1 detects that the given code already exists at `{changesDir}/todo/{code}/`:

1. Open `{changesDir}/todo/{code}/description.md` to see what's already noted.
2. Add the new content to the **Notes** section, leaving what's there as-is (don't delete or rewrite it) and appending the new content after it — like a notebook you keep writing in, not a document rewritten each time.
3. Confirm to the user that idea `{code}` has been updated.

## Listing noted ideas

If the user asks to see what ideas are noted: list `{changesDir}/todo/`'s subfolders and, for each one, its code and its `description.md`'s **Idea** field. If the folder doesn't exist or is empty, say so — there are no ideas noted yet.

## What this skill does NOT do

- It doesn't plan or implement anything (there's no `pv-how`/`pv-do` equivalent here).
- It doesn't move ideas between states or "close" them — there's no flow for that; if an idea stops being interesting, it's up to the user to delete it or leave it as-is.
- It doesn't number with the framework's `xxxx` nor invoke `pv-internal-workflow` — its numbering is independent and local to `{changesDir}/todo/`.
- It doesn't count as a source of intent for `pv-how`, `pv-do`, or any other framework skill: `{changesDir}/todo/` is `pv-todo`'s exclusive territory.
