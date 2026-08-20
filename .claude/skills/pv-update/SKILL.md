---
name: pv-init-update
description: Audits the pv-* framework's health in the current project — .claude/pv-context.json's shape against schema.json, referenced skills, on-disk paths, pv.py freshness, and skillModels drift — reports every inconsistency found with a proposed fix, and only applies fixes the user explicitly approves. Trigger: /pv-init-update, or when pv-init itself detects a problem during its own checks and delegates here, or when the user asks to "check"/"repair"/"diagnose" the framework's configuration.
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b8
  uses: []
---

# pv-init-update

Diagnoses and repairs the `pv-*` framework's configuration in the current project. Where `pv-init` bootstraps a project from scratch (or completes fields the user never configured), `pv-init-update` assumes the project was already initialized at some point and something has since drifted — a manual edit to `pv-context.json`, a moved/deleted folder, a framework upgrade that changed `schema.json` or `pv.py`, a `SKILL.md` edited by hand without re-running `sync-skill-models.py`.

**Read-only until approved.** This skill never writes anything before showing the full report to the user and getting explicit approval for each fix (or a batch approval — see step 4). It does not ask configuration questions the way `pv-init` does; it only proposes corrections for things that are objectively broken or inconsistent with what's already configured.

**Language.** Use `framework.interaction.language` (default English) for everything said to the user — read it from `.claude/pv-context.json` if the file exists and is valid JSON; fall back to English if it doesn't (that itself may be one of the problems reported).

**Relationship with `pv-init`.** `pv-init` runs its own lightweight checks (`check-context.py`) as part of its normal flow. If those checks — or anything else during its run — reveal a problem beyond "this optional field was never configured" (invalid JSON, a referenced skill that doesn't exist, a configured path missing on disk, `pv.py` out of sync), `pv-init` stops its own flow and invokes this skill (`Skill` tool) instead of trying to fix things itself. Once `pv-init-update` finishes (user approved fixes, or declined and exited), control returns to whatever invoked it: if `pv-init` was the caller, it resumes its own flow only if there's still something left for it to do — otherwise the interaction ends here.

## 1. Load context (best-effort)

Read `.claude/pv-context.json` if it exists, purely to resolve `framework.interaction.language` for talking to the user. Don't validate it by hand here — the audit script in step 2 does that deterministically. If the file doesn't exist at all, tell the user the framework isn't initialized and that they should run `pv-init` instead — don't continue.

```
This project doesn't have `.claude/pv-context.json` yet. Run `pv-init` first — there's nothing for me to audit.
```

## 2. Run the audit

Everything checkable deterministically is checked, for free in tokens, by [`scripts/audit-context.py`](scripts/audit-context.py) — a read-only script, it writes nothing. Run from the repo root:

```
python .claude/skills/pv-init-update/scripts/audit-context.py
```

It prints a single JSON with `problems`: a list of `{id, severity, field, message, expected?, actual?}`. `severity` is either:

- **`required`**: the framework is effectively broken or internally inconsistent (invalid JSON, unknown fields not in `schema.json`, a referenced skill folder that doesn't exist, `workFolder` or one of its fixed subfolders missing, a duplicate `{xxxx}` change code between `inProgress`/`implemented`, `pv.py` missing or stale against `assets/pv.py`, a `skillModels.overrides` entry pointing at a skill that no longer exists).
- **`optional`**: something configured doesn't match reality, but only because the corresponding field is *configured* — an unconfigured optional field (e.g. no `docs.tech.architectureDocDir` at all) is never reported as a problem. Covers: a configured `docs.*Dir`/`sourcecodeDir` pointing at a path that doesn't exist, or `skillModels` drifting from a `SKILL.md`'s real frontmatter (someone edited the file by hand without running `sync-skill-models.py`, or vice versa).

What the script does **not** check (out of scope, needs judgment or is handled elsewhere): semantic quality of `INDEX.md` content, whether `docs/*` numbering is sequential without gaps, anything `pv-status`/`pv-how` already validate at their own invocation time. Don't try to replicate those checks by hand here — stay scoped to what the script reports.

If `problems` is empty, tell the user the framework configuration is healthy and stop — nothing else to do.

## 3. Turn each problem into report + proposed fix

For every entry in `problems`, in the order the script returned them (required first, since the script lists them that way), think through **one concrete proposed fix** — don't just restate the problem. Use `expected`/`actual` from the script as the factual basis, but the fix itself needs judgment, for example:

- `workfolder-dir-missing` / `workfolder-subfolder-missing:*`: propose re-running `scaffold-project.py` (from `pv-init`) to recreate the missing fixed subfolders — never invent content for `changes/`, `versions/`, `stuff/`, they're meant to start empty (`.gitkeep`).
- `change-code-collision:*`: this one is **not** auto-fixable — flag it clearly as needing manual resolution (which folder is the real one, whether the other is stale) and don't propose an automatic fix; explain the risk of guessing wrong (losing a change's history).
- `unknown-top-level-field` / `unknown-framework-field`: propose removing the field (it's ignored by every skill and violates `schema.json`'s `additionalProperties: false`) — unless it looks like a typo of a real field (e.g. `worFolder`), in which case propose the rename instead and say so explicitly.
- `sourcecodedir-missing` / `framework.docs.*-missing-dir`: propose either updating the path to where the content actually lives (if you can find it — look around the repo) or, if truly gone, ask whether the user wants it recreated (delegate to `scaffold-project.py` for the `docs.*` ones) or the field cleared.
- `*-missing-index`: propose regenerating a minimal `INDEX.md` (same template `scaffold-project.py` uses) rather than inventing content.
- `pvpy-missing` / `pvpy-stale`: propose re-copying `assets/pv.py` over `{repo root}/pv.py` — always safe, it's a generated file never hand-edited.
- `skill-ref-missing:*` / `skillmodel-override-missing-skill:*`: propose either fixing the typo (if a same-named skill folder exists under a slightly different name) or falling back to the schema default (`pv-internal-mockups-html`, `pv-internal-tech-mermaid`) / removing the stale override, and say which.
- `skillmodel-drift:*`: propose running `sync-skill-models.py` if `pv-context.json` should win (the common case — someone changed `default`/`overrides` but forgot to sync), or updating `skillModels` in `pv-context.json` to mirror the file instead if the hand-edit to `SKILL.md` was the intended change — ask which direction is correct rather than assuming.
- `context-invalid-json`: not auto-fixable in general — show the parse error and ask the user to fix the JSON manually (offer to help locate the syntax error), since guessing the intended structure of broken JSON is unsafe.

## 4. Present the report and ask before touching anything

Show the user a single structured report, grouped by severity (`required` problems first, then `optional`), each with: what's wrong (in plain language, not just the raw `id`), why it matters, and the proposed fix. Then ask (via `AskUserQuestion` when the choice is closed, e.g. picking a fix direction) whether to:

- Apply all proposed fixes,
- Apply only a subset (let them pick which),
- Apply none and leave the report as information only.

**Never apply a fix the user didn't approve**, and never batch-approve silently just because most problems have an obvious fix — the collision and invalid-JSON cases in particular always need an explicit human decision, never a default action.

## 5. Apply approved fixes

Apply only what was approved, using the same underlying scripts `pv-init` itself uses wherever one exists (`scaffold-project.py` for folders/`pv.py`, `sync-skill-models.py` for frontmatter sync) instead of reimplementing that logic here. For fixes with no existing script (field rename/removal in `pv-context.json`, updating a path, clearing a stale override), edit `.claude/pv-context.json` directly, keeping its shape valid against `schema.json` (same rule as `pv-init` step 4: no properties outside what the schema declares).

After applying fixes, re-run [`scripts/audit-context.py`](scripts/audit-context.py) to confirm the approved problems are actually gone and nothing new was introduced. Show the user a short before/after summary: which problems were fixed, which were left (declined or not auto-fixable), and remind them to run `sync-skill-models.py` themselves if a `skillModels` fix was written to `pv-context.json` but they chose not to have it applied automatically in this same run.
