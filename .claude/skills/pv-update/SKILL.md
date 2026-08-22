---
name: pv-update
description: Audits and repairs the pv-* framework's health in the current project — .claude/pv-context.json's shape against schema.json, referenced skills, on-disk paths, pv.py freshness, skillModels drift, the `[[[...]]]`-marked structural labels in every changes/**-derived document under workFolder, duplicate change codes, and version consistency (every pv-* skill sharing the same major.minor, and pv-context.json's last-verified version matching what's actually installed) — fixes everything it can determine unambiguously on its own and reports what it changed; only asks the user when pv-context.json is broken JSON or the installed version looks like a downgrade, neither of which it can safely resolve on its own. Trigger: /pv-update, or when pv-init itself detects a problem during its own checks and delegates here, or when another pv-* skill's step 0 finds its live version check doesn't match (or `frameworkStatus` missing/`blocked` true) and sends the user here, or when the user asks to "check"/"repair"/"diagnose"/"update" the framework's configuration.
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b10
  uses: []
---

# pv-update

Diagnoses and repairs the `pv-*` framework's configuration in the current project. Where `pv-init` bootstraps a project from scratch (or completes fields the user never configured), `pv-update` assumes the project was already initialized at some point and something has since drifted — a manual edit to `pv-context.json`, a moved/deleted folder, a framework upgrade that changed `schema.json` or `pv.py`, a `SKILL.md` edited by hand without re-running `sync-skill-models.py`, a template-derived document (`description.md`, `plan.md`, a feature file...) whose structural markers got translated or altered by hand, or a duplicate change code from two entries created independently.

**Informative, not interactive.** This skill doesn't ask the user whether to apply a fix — every problem it can determine unambiguously, it fixes on its own and reports afterward. There's no "apply all / apply some / apply none" choice and no severity tiers to weigh: everything found gets corrected, full stop. There are exactly **two** exceptions, both because guessing the right answer would be unsafe: `context-invalid-json` (`.claude/pv-context.json` itself isn't valid JSON — any fix is a guess at content that isn't recoverable from the file itself) and `version-check-downgrade` (the installed framework's real version is older than what was last verified — could be an intentional rollback or an accidental one, and only the user knows which). Both stop the fix loop and ask instead of resolving unilaterally.

**Language.** Use `framework.interaction.language` (default English) for everything said to the user — read it from `.claude/pv-context.json` if the file exists and is valid JSON; fall back to English if it doesn't (that itself may be one of the problems reported).

**Relationship with `pv-init`.** `pv-init` runs its own lightweight checks (`check-context.py`) as part of its normal flow. If those checks — or anything else during its run — reveal a problem beyond "this optional field was never configured" (invalid JSON, a referenced skill that doesn't exist, a configured path missing on disk, `pv.py` out of sync), `pv-init` stops its own flow and invokes this skill (`Skill` tool) instead of trying to fix things itself. Once `pv-update` finishes (fixes applied and reported, or stopped on the invalid-JSON case), control returns to whatever invoked it: if `pv-init` was the caller, it resumes its own flow only if there's still something left for it to do — otherwise the interaction ends here.

**Before any other step**, read [`workflow.audit.md`](workflow.audit.md) — it's the source of truth for this flow's sequence and branches (see `pv-design.en.md`'s "Workflow diagrams" section for the notation). If it doesn't exist or can't be followed, stop and report that instead of improvising the flow from the prose below. The numbered steps that follow are each node's detail (which script to run, what text to use) — the diagram governs sequence and branching; if the two ever disagree, the diagram wins and this prose gets corrected to match.

## 1. Load context (best-effort)

Read `.claude/pv-context.json` if it exists, purely to resolve `framework.interaction.language` for talking to the user. Don't validate it by hand here — the audit script in step 2 does that deterministically. If the file doesn't exist at all, tell the user the framework isn't initialized and that they should run `pv-init` instead — don't continue.

```
This project doesn't have `.claude/pv-context.json` yet. Run `pv-init` first — there's nothing for me to audit.
```

## 2. Run the audit

Everything checkable deterministically is checked, for free in tokens, by [`scripts/audit-context.py`](scripts/audit-context.py) — a read-only script, it writes nothing. Run from the repo root:

```
python .claude/skills/pv-update/scripts/audit-context.py
```

It prints a single JSON with `problems`: a list of `{id, severity, field, message, expected?, actual?}`. `severity` (`required`/`optional`) only reflects whether the underlying field was configured at all — it is **not** a priority order for deciding what to fix: every problem gets fixed regardless of severity, the field just distinguishes "the framework is broken" from "something configured doesn't match reality." Covers:

- Broken/invalid `pv-context.json` shape (invalid JSON, unknown fields, missing `framework`).
- `workFolder` or one of its fixed subfolders missing.
- `change-code-collision:*` — the same `{xxxx}` exists in both `inProgress/` and `implemented/`.
- `marker-missing:*` — a `description.md`/`plan.md` under `{workFolder}/changes/**` missing one of the `[[[...]]]`-marked structural labels its source template declares (see `pv-design.en.md`'s "Marker convention in templates"), almost always because the label was translated instead of left in English, or the document was hand-edited.
- A configured `docs.*Dir`/`sourcecodeDir` pointing at a path that doesn't exist.
- `skillModels` drifting from a `SKILL.md`'s real frontmatter (someone edited the file by hand without running `sync-skill-models.py`, or vice versa).
- `pv.py` missing or stale against `assets/pv.py`.
- A referenced skill (`skills.mockups`/`skills.diagrams`/`skillModels.overrides`) that doesn't exist on disk.
- `skill-version-mismatch:*` — a `pv-*` skill whose `metadata.version` differs in major.minor from the majority of the others (a partial/interrupted framework update).
- `version-check-outdated` / `version-check-downgrade` — `framework.frameworkStatus.lastVerifiedVersion` (only checked if that field exists) compared against `pv-init/SKILL.md`'s real, current `metadata.version`: newer real version means an update was installed since the last `pv-update` run; older real version means a downgrade or inconsistency.

The marker check only ever looks inside `{workFolder}/changes/**` (never outside `workFolder`, and never above it) — it walks `description.md` under `inProgress/*`, `implemented/*` and `todo/*`, and `plan.md` under `inProgress/*`, comparing each against the `[[[...]]]` labels its source template (`pv-internal-workflow/description.template.md`, `pv-how/PLAN.template.md`, `pv-todo/description.template.md`) declares — the template is read fresh every run, so the check never drifts from what the templates actually mark.

What the script does **not** check (out of scope, needs judgment or is handled elsewhere): semantic quality of `INDEX.md` content, whether `docs/*` numbering is sequential without gaps, anything `pv-status`/`pv-how` already validate at their own invocation time. Don't try to replicate those checks by hand here — stay scoped to what the script reports.

If `problems` is empty **and** `framework.frameworkStatus.lastVerifiedVersion` is already set, tell the user the framework configuration is healthy and stop — nothing else to do. If `problems` is empty but `lastVerifiedVersion` is absent (a project that has never run `pv-update` before), skip straight to step 3.5 to write it for the first time, then report that in step 4 — there's no fix loop to run, but the version still needs recording.

## 3. Fix every problem deterministically

For every entry in `problems`, apply the fix below — no approval step, no batching, no picking a subset. Keep a running list of `{id, what you did}` as you go, in the order the script returned them: this becomes the report in step 4.

- **`context-invalid-json`** — the one case that isn't auto-fixed (see "Informative, not interactive" above). Stop the fix loop here: show the parse error to the user, offer to help locate the syntax error, and ask them to fix the JSON by hand or tell you what the intended structure was. Once it's valid, re-run the audit from step 2 — everything else in this list still needs to run against the corrected file.
- **`workfolder-dir-missing` / `workfolder-subfolder-missing:*`**: re-run `scaffold-project.py` (from `pv-init`) to recreate the missing fixed subfolders. Never invent content for `changes/`, `versions/`, `stuff/` — they're meant to start empty (`.gitkeep`).
- **`change-code-collision:*`**: keep the code on the **older** entry (by `description.md`'s `**Creation date**`, whichever is available and reliable — if both are ambiguous, `git log`'s earliest commit touching that folder is the tiebreaker) and renumber every other colliding entry. Compute each new code the same way `pv-internal-workflow/scripts/next-change-number.py` does (lowest unused `xxxx` across every state under `changes/`, skipping `todo/`) — run it for real after each rename, not just once, since the previous rename changes what's "next." Renaming means moving the whole folder in place, to a sibling `{xxxx}` under the same state (`git mv` if the repo is a git repo and the folder is tracked, plain move otherwise) — there's no dedicated script for an in-place rename (`move-change.py` only moves between states like `inProgress`→`implemented`, not within one). Update the renamed entry's `description.md`'s `**Code**` field to match the new folder name; never touch the older entry that keeps its code.
- **`unknown-top-level-field` / `unknown-framework-field`**: if it looks like a typo of a real field (e.g. `worFolder`), rename it to the real field name, preserving its value. Otherwise remove it — it's ignored by every skill and violates `schema.json`'s `additionalProperties: false`.
- **`sourcecodedir-missing` / `framework.docs.*-missing-dir`**: look around the repo for where the content actually moved to and update the path to match. If you can't find it anywhere, recreate it empty via `scaffold-project.py` (for `docs.*`) or, for `sourcecodeDir`, create the folder itself — never leave a configured path dangling.
- **`*-missing-index`**: regenerate a minimal `INDEX.md` (same template `scaffold-project.py` uses) rather than inventing content.
- **`pvpy-missing` / `pvpy-stale`**: re-copy `assets/pv.py` over `{repo root}/pv.py` — always safe, it's a generated file never hand-edited.
- **`skill-ref-missing:*` / `skillmodel-override-missing-skill:*`**: if a same-named skill folder exists under a slightly different name, fix the typo to point at it. Otherwise fall back to the schema default (`pv-internal-mockups-html`, `pv-internal-tech-mermaid`) for `skills.*`, or remove the stale entry for `skillModels.overrides`.
- **`skillmodel-drift:*`**: `pv-context.json`'s `skillModels` is the source of truth — run `sync-skill-models.py` so the `SKILL.md` frontmatter matches what's configured there. (If the hand-edit to `SKILL.md` was actually the intended change, the user would edit `pv-context.json` to match and re-run `pv-update` themselves — this skill doesn't need to ask which direction is "correct," it always converges frontmatter toward what `pv-context.json` declares.)
- **`marker-missing:*`**: restore the missing label(s) — listed in `expected` — to their exact English form from the source template, in the same spot (bold-inline `**Label**:` or heading `## Label`, matching whatever the rest of that document already uses), without touching the value/content that follows the label or translating it back. This is mechanical: the translated or reworded label is still visible in the document, you're only restoring the label itself.
- **`skill-version-mismatch:*`**: don't autocorrect by rewriting `metadata.version` by hand — that would falsify which version is actually installed. Report it with the specific skill(s) affected, their version, and the majority's version (from `expected`/`actual`), and recommend re-running `install.sh`/`install.ps1` for a clean reinstall of `.claude/skills/pv-*/` — this skill only diagnoses, it doesn't reinstall files itself.
- **`version-check-outdated`**: no fix of its own here — it resolves automatically via step 3.5 below, once every other problem in this loop has been handled.
- **`version-check-downgrade`** — the second non-auto-fixed exception (see "Informative, not interactive" above). First run `scripts/mark-verified.py --block "<short reason citing expected/actual>"` so the block is persisted immediately (an interrupted conversation shouldn't leave this undetected). Then show the user `expected`/`actual`, offer to inspect `git log`/`git diff` on the affected `pv-*/SKILL.md` files and on `.claude/pv-context.json` to help reconstruct what happened, and ask how to proceed:
  - If the user confirms the downgrade was intentional: run `scripts/mark-verified.py --confirm-downgrade` (sets `lastVerifiedVersion` to the current real version, clears `blocked`).
  - If it wasn't intentional: guide them toward restoring the correct files or re-running `install.sh`/`install.ps1`, and tell them to invoke `/pv-update` again once done. `blocked=true` stays in place meanwhile, protecting every other skill.

## 3.5 Update the verified version

Once every problem from step 3 has been handled (or the only thing left is an unresolved `version-check-downgrade`, in which case skip this step — `blocked` must stay `true`), run:

```
python .claude/skills/pv-update/scripts/mark-verified.py --clear
```

This writes `framework.frameworkStatus.lastVerifiedVersion` = the real current version of `pv-init/SKILL.md`, and `blocked=false`. It prints the resulting `frameworkStatus` JSON — keep it for the report in step 4.

## 4. Report what was found and fixed

After the fix loop finishes (or stops on `context-invalid-json`/an unresolved `version-check-downgrade`), show the user a single report, structured as: what was found, what was changed to fix it, one line each — grouped by area (config shape, workFolder/paths, change codes, structural markers, `pv.py`, `skillModels`, framework version) rather than by the raw `id`. For the "framework version" area specifically: say whether `lastVerifiedVersion` was updated (and to what, from step 3.5's output), whether any `skill-version-mismatch` was found and what you recommended, and — if a `version-check-downgrade` is still unresolved — call that out explicitly as a pending blocker, don't bury it among the rest. If nothing needed fixing (step 2 already covers the "problems empty" case), this step doesn't run.

Re-run [`scripts/audit-context.py`](scripts/audit-context.py) after applying fixes to confirm every fixed problem is actually gone and nothing new was introduced by the fixes themselves (e.g. a renumbered folder colliding with another rename in the same batch). If anything remains, say so plainly — don't claim "100% healthy" if the re-run still reports something.

This is a report, not a request for confirmation: don't ask "should I have done this" after the fact, and don't offer to undo anything — if the user disagrees with a specific fix, they can tell you and you correct it as a follow-up, same as any other edit.
