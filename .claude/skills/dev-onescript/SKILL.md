---
name: dev-onescript
description: Develops pv.py, the framework's self-contained interactive launcher — adding menu options, submenus, or screen behavior while preserving its single-file design and the four-screen-helper model. Trigger: /dev-onescript, or when the user asks to add/change/fix something in pv.py, its menu, or its interactive screens.
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.1.0
  uses: []
---

# dev-onescript

Implements changes to `pv.py`, the `pv-*` framework's interactive one-file launcher. This skill owns the file's design consistency across every future change to it — it's the only entry point that should ever touch `pv.py`'s source.

**The master copy lives at `.claude/skills/pv-init/assets/pv.py`.** The repo-root `pv.py` is a generated artifact — `scaffold-project.py` (from `pv-init`) overwrites it unconditionally from the master copy, and `pv-init-update`'s audit (`pvpy-stale`) flags root `pv.py` as broken the moment it stops matching the master byte-for-byte. **Never edit `{repo root}/pv.py` directly** — always edit `.claude/skills/pv-init/assets/pv.py`, then propagate (step 5) by re-running `scaffold-project.py`, which copies it back to the root.

## 1. Read the design doc first, always

Before writing or even planning any change, read [`../../pv-design-onescript.en.md`](../../pv-design-onescript.en.md) in full (or its Spanish twin `pv-design-onescript.es.md` if you're operating in Spanish — both describe the exact same design, keep using whichever matches the conversation's language). This is not optional context, it's the spec: screen hierarchy, navigation flow, file block organization, the four screen helpers, style-per-screen-type rules, and the extension guide with its common-mistakes list. Do not skip this step even for a change that looks trivial — most of `pv.py`'s design mistakes come from a change that looked trivial in isolation but broke a global convention (color leaking between screen types, `hr()` defaulting to the wrong color, comparing `show_selection()`'s result the wrong way).

If the requested change isn't covered by the design doc's "How to Extend" guide (e.g. it's a change to the rendering primitives, the menu engine itself, or something structurally new), read the doc's "File Organization" and "Component Diagram" sections carefully before proposing where it belongs — don't guess.

## 2. Plan against the single-file constraint

`pv.py` is deliberately a single self-contained file — see the design doc's "Purpose" section for why (so `pv-init`'s `scaffold-project.py` can copy it to the repo root without depending on a package structure). Default to implementing the entire change inside `.claude/skills/pv-init/assets/pv.py`:

- Place new code in the file block it belongs to per the design doc's "File Organization" table — never intersperse it into another block just because it's near where it's used.
- Reuse the four screen helpers (`print_header`, `show_selection`, `show_info`, `confirm`) for every new screen — see "The Four Screen Helpers" and "What NOT to do" in the design doc. If a new option doesn't fit any of the four, decompose it into several helper calls rather than hand-rolling `hr()`/`print()`.
- Follow the "Guide for Extending pv.py" step by step for the specific kind of addition (read-only option, new submenu, state-mutating option) and check the "Common Mistakes" list before considering the change done.
- The "Single extension point" rule is a hard boundary, not a suggestion: `pv.py` orchestrates, it never contains business logic or writes file content. A purely read-only option (delegating to an existing or new `--terminal` script) or a simple, already-validated mutation (like moving a folder) confirmed via `confirm()` first — that's the entire menu of what belongs here.

### When the change can't stay inside pv.py

Some requests genuinely require touching another script — e.g. a new menu option needs a new `--terminal`-capable read-only script, or a new simple mutation needs its own validated script in the corresponding skill (mirroring `move-change.py`'s pattern). Before touching anything outside `.claude/skills/pv-init/assets/pv.py`:

1. **Identify every other consumer of the script(s) you'd change.** A script like `render_status.py`, `filter_status.py`, `list_todo.py`, `move-change.py`, or `sync-skill-models.py` is typically invoked by more than just `pv.py` — usually by its owning skill's own `SKILL.md` flow, and possibly by other skills. Grep for the script's filename across `.claude/skills/**/SKILL.md` and other scripts before assuming it's safe to change.
2. **Write a short risk plan** (in conversation, not a file) covering: which existing callers exist, what behavior they currently rely on (arguments, output format, exit codes), what the proposed change would alter, and whether it's additive (new optional flag, new script) versus modifying existing behavior. Prefer strictly additive changes (a new script, or a new optional argument with a safe default) over modifying an existing script's behavior.
3. **Present that plan to the user and get explicit confirmation before implementing anything outside `pv.py`.** This applies even if the change looks small — a script's output format changing by one line can break another skill's parsing of it.
4. Only once confirmed, implement the external change, then come back and wire `pv.py` to it via `run_script()`, following the same single-extension-point rules as any other option.

Never skip straight to editing an external script because it seems more convenient than extending `pv.py`'s own logic — the design's whole point is keeping `pv.py` as the single place non-technical users read to understand what the launcher can do.

## 3. Apply Python best practices

- Match the existing file's style: type hints on every function signature (`list[str]`, `tuple[str, str] | None`, etc.), short docstrings only on the four screen helpers and other non-obvious functions (see how sparse the existing docstrings are — most action functions have none, because their name and the calling convention already say what they do).
- No new imports unless truly necessary — the file currently only imports from the standard library (`json`, `os`, `re`, `subprocess`, `sys`, `textwrap`, `pathlib`). Keep it that way; a third-party dependency would break the "copy one file, run it anywhere" premise.
- No new top-level state beyond the existing `ROOT`/`*_SCRIPTS`/`CONTEXT_PATH` constants unless the new feature genuinely needs a new shared path — add it next to the others in the same block, not scattered.
- Keep functions small and single-purpose, consistent with the existing action functions (a `list_*()` data-gathering function separate from a `show_*()`/action function that renders it, as `list_states()`/`show_filtered_status()` and `list_versions()`/`show_version_changelog()` already do).
- Don't add error handling for scenarios the rest of the file doesn't already guard against (e.g. don't wrap `CONTEXT_PATH.read_text()` in a new try/except "just in case" — `work_root()` doesn't, and `main()` already checks `CONTEXT_PATH.is_file()` before any menu runs).

## 4. Implement

Edit `.claude/skills/pv-init/assets/pv.py` directly. If the module-level docstring's option summary (the "Most options are read-only..." paragraph near the top of the file) becomes inaccurate because of the change, update it in the same edit — it's the file's own quick-reference for anyone opening it without the design doc.

## 5. Propagate to the repo-root copy

After editing the master copy, refresh `{repo root}/pv.py` so it isn't left stale (which `pv-init-update`'s audit would flag as `pvpy-stale`). Run from the repo root:

```
python .claude/skills/pv-init/scripts/scaffold-project.py
```

This overwrites `{repo root}/pv.py` unconditionally from the master copy and leaves every other scaffolded path untouched (folders/placeholders are only created where missing, never overwritten) — safe to run after any `pv.py` change. Confirm afterward that the two files are identical (e.g. diff them) before considering the change done.

## 6. Test the change

Since this is an interactive terminal tool, static review isn't enough — actually run it:

```
python3 pv.py
```

from the repo root, and exercise the new/changed option end to end (including the "Press Enter to return..." pause behavior if you added or changed a submenu — verify `is_submenu = True` is set correctly per the design doc's step 2 of "Adding a new submenu", since forgetting it causes a double pause). Also sanity-check `NO_COLOR=1 python3 pv.py` if the change touches anything color-related, and confirm existing unrelated menu options still work (a regression check, not just the new path).

## 7. Update both design docs

Once the change is implemented, tested, and propagated, update **both** [`../../pv-design-onescript.es.md`](../../pv-design-onescript.es.md) and [`../../pv-design-onescript.en.md`](../../pv-design-onescript.en.md) to reflect it — always both, kept in sync as exact translations of each other, never one without the other. Depending on what changed, this typically means:

- A new root menu option or submenu → update "Screen Hierarchy", the Mermaid graph in "Navigation Flow", and possibly "External Dependencies" if it introduced a new script.
- A new external script dependency → add it to the "External Dependencies" tables and, if it introduces a new skill boundary, update the "Component Diagram".
- A new file-organization block → add it to the "File Organization" table.
- Any change to the four helpers' behavior or the style rules → update "The Four Screen Helpers" and/or "Style by Screen Type" precisely, since those sections are the contract other future changes will be checked against.

Do not consider the task finished until both documents are updated — an undocumented change to `pv.py` is exactly the kind of drift this skill exists to prevent.
