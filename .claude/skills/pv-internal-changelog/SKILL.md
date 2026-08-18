---
name: pv-internal-changelog
description: Drafts changelog.md from the entries accumulated in {workFolder}/changes/closed (staged into closed/temp/ so later closures don't interfere), from a strictly functional perspective, and deletes the folded-in folders after confirmation. Internal use by the pv-version skill.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b4
  uses: []
---

# pv-internal-changelog

Drafts `changelog.md` for a release in preparation, from the entries accumulated in `{workFolder}/changes/closed/` (staged into `closed/temp/` at the start, so anything closed later while this runs doesn't interfere), and deletes those folders after explicit user confirmation. Only invoked by `pv-version` — not meant for direct invocation by the user.

**Language.** Use `framework.interaction.language` (default English) for the guardrail message and the deletion confirmation with the user. `changelog.md` follows `framework.versions.language` (default `interaction.language`, English if neither is configured). If `language` is not configured anywhere, everything is English.

## Invocation guardrail — read before anything else

This skill **does not run if invoked directly** (e.g. the user typed `/pv-internal-changelog`, or asked in plain text to "run/invoke pv-internal-changelog"). It should only run when `pv-version`'s own content has instructed you to invoke it as part of its process, with the destination folder already resolved.

If you were invoked without that context, **stop here** and tell the user that `pv-internal-changelog` is for internal framework use: to prepare a release they should use `/pv-version`. Do nothing else in that case.

```
`/pv-internal-changelog` is for internal use by the `pv-*` framework and isn't invoked directly. To prepare a release use `/pv-version`.
```

**Expected input from the caller:** destination folder `{workFolder}/versions/{XXXX}/` (the version being prepared).

## 1. Move `closed/` into `closed/temp/`

Run from the repo root:

```
python .claude/skills/pv-internal-changelog/scripts/stage-closed-entries.py
```

Moves every entry currently in `{workFolder}/changes/closed/` into `{workFolder}/changes/closed/temp/` (creating it if needed). From this point on, the rest of this process reads and writes only `closed/temp/` — any change/fix closed afterwards, while this version is still being prepared, lands in `closed/` and doesn't affect this run.

## 2. List `temp`'s entries

Run from the repo root:

```
python .claude/skills/pv-internal-changelog/scripts/list-closed-entries.py
```

Returns a JSON with, for each subfolder of `{workFolder}/changes/closed/temp/`, its `xxxx` and the path to its `description.md`. If `entries` comes back empty, tell the caller there's nothing to fold in and stop here — don't create `changelog.md` nor touch anything else (there's nothing to clean up either, since nothing was staged).

## 3. Locate the previous version's changelog

Run from the repo root:

```
python .claude/skills/pv-internal-changelog/scripts/find-previous-version.py --xxxx <XXXX>
```

Walks `{workFolder}/versions/`, excludes the `{XXXX}` folder being generated, and returns the most recently created one (or `"found": false` if there's no other).

- If `"found": true`: **confirm with the user** that that `xxxx` is the correct previous version before using it (show it to them explicitly) — if the user gives another, use that one instead. If `"changelogExists": true`, read that `changelog.md` as a reference for what functionality was already recorded. If `"changelogExists": false` (a previous version half-prepared, with no changelog yet), treat it the same as if there were no previous version.
- If `"found": false`: there's no previous version — everything goes to **New** in step 3.

## 4. Draft `changelog.md`

For each entry in `closed/temp/`, read its `description.md` and take its **Name**, **Type** and **Full description** fields (already drafted in purely functional terms by `pv-internal-workflow` when it created them — don't reread code or technically reinterpret them). Classify it into one of four sections:

- **Fixes** — if **Type** is `fix` or `fast`: always goes here directly, without comparing against the previous version (they're corrections or trivial changes, not new functionality nor a behavior change to document as such).
- In any other case (**Type** `change`), compare it against the previous version's `changelog.md` (if any) and classify it into:
  - **New** — functionality that didn't exist before (or there's no previous version to compare against).
  - **Changed** — modifies or extends something that already appeared in the previous changelog.
  - **Removed** — removes or disables something that appeared in the previous changelog.

Write `{workFolder}/versions/{XXXX}/changelog.md` following the [`changelog.template.md`](changelog.template.md) template: a header with the version's `XXXX`, the date, and the item count for each section (New, Changed, Removed, Fixes — count the ones at 0 too), followed by the four sections (omit an entire section if it's empty), each entry with a bold name + a one- or two-sentence functional summary (changelog tone, past tense), without mentioning files, functions, or technical details.

## 5. Confirm deletion with the user before deleting anything

Show the list of `xxxx` folded into the changelog and explicitly ask for confirmation that their folders in `{workFolder}/changes/closed/temp/` can be deleted (irreversible action). If the user doesn't confirm, leave `changelog.md` as already written but don't delete anything, and tell the caller (`pv-version`) in step 8 — they'll be moved back to `closed/` in step 7 regardless.

## 6. Delete the folded-in entries

Only after confirmation, run from the repo root:

```
python .claude/skills/pv-internal-changelog/scripts/delete-closed-entries.py --xxxx-list <comma-separated list of folded-in xxxx>
```

Deletes only those specific folders under `{workFolder}/changes/closed/temp/`, never "all of `closed/temp/`" blindly, in case the deletion was only partially confirmed.

## 7. Clean up `closed/temp/`

Always run this step, whether or not deletion was confirmed (and whether it was full or partial). Run from the repo root:

```
python .claude/skills/pv-internal-changelog/scripts/cleanup-temp-entries.py
```

Moves any folder still left in `closed/temp/` (not deleted) back to `{workFolder}/changes/closed/` — so nothing declined for deletion is lost — and removes `closed/temp/` once it's empty.

## 8. Confirm to the caller

State the generated `changelog.md`'s path, how many entries landed in each section (New/Changed/Removed/Fixes), whether `closed/temp/`'s folders were deleted or not (and if so, which ones), and which ones (if any) were moved back to `closed/` in step 7.
