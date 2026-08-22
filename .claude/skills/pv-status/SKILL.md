---
name: pv-status
description: Collects and presents the current project status per the pv-* framework — totals by item type (todo/change/fix/fast) and by state ({changesDir} folders). Returns the report as a chat reply; writes no file unless the user explicitly asks. Trigger: /pv-status, or when the user asks for a summary/overview of the project's status, how many changes/fixes are pending, etc. Accepts optional arguments for filtered listings: `todo` (only ideas from `{changesDir}/todo/`) or the name of any other existing state folder (e.g. `closed`, `implemented`, `inProgress`).
argument-hint: "[todo|<state>]"
model: claude-haiku-4-5
effort: medium
metadata:
  version: 0.9.5b11
  uses: []
---

# pv-status

Gives an overview of the project's status within the `pv-*` framework, based exclusively on `{changesDir}`'s content (its state subfolders: `todo`, `inProgress`, `implemented`, `closed`, or any other that exists).

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation — including the "not initialized" message in step 0. **The report itself always stays in English**, regardless of `interaction.language` (see the note in step 2) — it's produced by deterministic Python scripts, not the LLM, precisely so it costs no tokens and stays consistent; only the sentence introducing it (if you add one, which step 3 says not to) would ever follow `interaction.language`. If `language` is not configured anywhere, everything is English anyway.

This skill is read-only: it doesn't create, move, or modify any `{changesDir}` folder or file. The report is delivered as a chat reply; **nothing is written to any file unless the user explicitly asks** (see step 4).

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize the framework, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

## 1. Detect the invocation mode

Before running any script, look at how the skill was invoked — each mode uses a different script and **only one** runs:

- `todo` argument (`/pv-status todo`, or "just the todo ideas"/"list the todos") → go to **1.b**.
- Argument naming an existing state folder in `{changesDir}` other than `todo` (e.g. `/pv-status closed`, `/pv-status implemented`, `/pv-status inProgress`, or "the full list of what's in `<state>`") → go to **1.c**.
- No argument, or any other case (general report) → go to **2**.

Don't run `collect_status.py` directly in any mode: it's an internal module that `list_todo.py` and `render_status.py` import and reuse on their own, not a script meant to be invoked from the skill — its JSON output brings nothing the skill needs to show or reformat.

All three scripts (`list_todo.py`, `filter_status.py`, `render_status.py`) also accept a `--terminal` flag that switches the output to plain text without markdown, plus a `--width` flag (default 70) controlling that plain-text output's column width — the caller decides the width, not the script. It's for the exclusive use of `pv.py` (the framework's terminal menu, which passes its own width via `--width` so delegated screens match its menu); this skill, invoked from chat, must **never** pass `--terminal`/`--width` — the default markdown is always the right format for a chat reply.

## 1.b `todo` mode: list ideas only

Run [`scripts/list_todo.py`](scripts/list_todo.py) directly — don't run `collect_status.py` for this mode, it's not needed:

```
python .claude/skills/pv-status/scripts/list_todo.py
```

The script already applies the [`STATUS.todo.template.md`](STATUS.todo.template.md) template internally and prints the ready-to-show markdown listing on stdout (code + full untruncated text of each `description.md`'s `## Idea` section, explicitly flagging ideas without that section, or the "no ideas" message if `todo/` is empty) — it's not JSON, don't reapply the template yourself or reformat anything.

Your chat reply must be **exactly** the script's stdout, with nothing added before or after (no "Here's the listing:", summaries, or comments of your own). Don't save it to a file unless the user asks (step 4).

## 1.c `<state>` mode: filtered listing of one state folder

Run [`scripts/filter_status.py`](scripts/filter_status.py) directly with that folder's name as argument — don't run `collect_status.py` for this mode, it's not needed:

```
python .claude/skills/pv-status/scripts/filter_status.py <state>
```

If the given state doesn't exist as a `{changesDir}` folder, the script fails with a message listing the available states — your reply must be exactly that error message, as-is, without improvising your own list.

The script already applies the [`STATUS.filtered.template.md`](STATUS.filtered.template.md) template internally and prints the ready-to-show markdown report on stdout (Code/Type/Description/Risk/Date table, or the "no entries" message if the state is empty) — it's not JSON, don't reapply the template yourself or reformat anything.

Your chat reply must be **exactly** the script's stdout, with nothing added before or after (no "Here's the report:", summaries, or comments of your own). Don't save it to a file unless the user asks (step 4).

## 2. Generate the report

All the mechanics of collecting and mapping the data onto the [`STATUS.template.md`](STATUS.template.md) template (totals table, the three "In progress" lists, fast changes, `todo/` ideas, warnings) are handled, deterministically and for free in tokens, by the [`scripts/render_status.py`](scripts/render_status.py) script — don't repeat that field-by-field mapping yourself, don't draft the lists by hand, and don't run `collect_status.py` first: `render_status.py` collects the data internally on its own, it doesn't depend on anything from step 1. Run from the repo root:

```
python .claude/skills/pv-status/scripts/render_status.py
```

The script collects `{changesDir}`'s data on its own (same logic as `collect_status.py`) and applies the full mapping (including the rule that the Fast column only appears in `implemented`/`closed`, the three "In progress" lists with their empty cases, and fully omitting the "Implemented fast changes"/"Warnings" sections when they don't apply) and prints the ready-to-show markdown report on stdout — it's not JSON, don't reapply the template yourself or reformat anything. **The report's text — headings, table columns, state labels — is always in English, regardless of `framework.interaction.language`**: paste it verbatim, don't translate it.

By default the **"Implemented fast changes" section is omitted**, even if fast entries exist (the Fast column's total in the table still shows). Only include it if the user explicitly asks for it in this turn (e.g. "show me the fast ones too", "detail the fast changes"), by adding the `--show-fast` flag:

```
python .claude/skills/pv-status/scripts/render_status.py --show-fast
```

Don't invent data that isn't in the script's output (e.g. don't assign a type to an `unknown` entry just by guessing it from the folder name).

## 3. Present the report

Your chat reply must be **exactly** the stdout of the script run in step 2, with nothing added before or after (no "Here's the report:", summaries, comments of your own, or extra text outside the markdown the script printed). Don't save it to any file at this step.

## 4. Save to a file (only if the user asks)

If the user, in this same turn or a later one, explicitly asks for the report to be saved (e.g. "save it", "put it in a file"), and hasn't given a specific path, ask them where they want it saved (e.g. `{changesDir}/STATUS.md` or another path of their choice) before writing anything — don't assume a default path.
