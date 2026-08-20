---
name: pv-init
description: Initializes the pv-* framework (change/fix/workflow) in the current project, generating .claude/pv-context.json with the required configuration (folder/file paths for the change-tracking process, plus language configuration). Trigger: /pv-init, or when any other pv-* skill needs .claude/pv-context.json and it doesn't exist (or is missing fields), or when the user asks to "set up"/"configure" this framework in a new project.
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b8
  uses: [pv-update]
---

# pv-init

Bootstraps the `pv-*` framework in the current project: creates (or completes) `.claude/pv-context.json`, the single file that `pv-internal-workflow`, `pv-new`, `pv-fix`, `pv-how` and `pv-do` all depend on to work in any repo with nothing hardcoded.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation, once it's known — see step 3 below for how it gets resolved on a first-time run. `.claude/pv-context.json` itself is configuration, not prose, so it stays as-is regardless of `language`.

Read [`schema.json`](schema.json) first if you haven't already this session — it's a JSON Schema that defines the exact shape of the file (the `framework` section), with every field documented in its `description` (required or not, what it's for, which skill uses it) and complete examples in `examples`.

## 0. Check the dev environment and required tooling

Before touching `.claude/pv-context.json`, verify that the command-line tools the `pv-*` framework depends on are installed and working. This step comes first because there's little point leaving the framework configured if `pv-new`/`pv-fix`/`pv-how`/`pv-do` then fail for lack of a tool.

Base tools, always needed (used by the framework itself, regardless of the project):

- **Git** — the repo is already a git repository, but check the CLI responds: `git --version`.
- **Python 3** — used by `pv-internal-workflow` (invoked by `pv-new`/`pv-fix`) to compute the sequential change code via [`../pv-internal-workflow/scripts/next-change-number.py`](../pv-internal-workflow/scripts/next-change-number.py). Check `python --version` or `python3 --version` (whichever alias resolves on this system).

Conditional tools — look at the repo (same as the exploration in step 2) to know which apply before asking anything:

- If there's a `package.json` → Node/npm: `node --version`, `npm --version`.
- Any other interpreter or CLI relevant to the detected project type — if it turns out to be a tool not already checked here, verify it on the spot before treating it as supported.

How to check: run the version commands with the shell tool for the system (`Bash` or `PowerShell` depending on the environment's `Platform`/`Shell`). A command that doesn't exist or returns a "not found" error counts as a missing tool.

If any tool is missing:

1. Tell the user clearly what's missing and what the framework needs it for (use the list above as reference).
2. Propose how to install it on their OS (e.g. `winget install`/`choco install` on Windows, `brew install` on macOS, `apt install` on Linux) — be specific about the package and the exact command proposed.
3. **Never install anything without the user's explicit confirmation** — installing software affects the system outside the repo. Ask first (`AskUserQuestion` or a direct confirmation) and, if they agree, run the install command with their help.
4. After installing, re-check the tool (repeat the version command) to verify it installed and configured correctly (on `PATH`, expected version, etc.) before continuing.
5. If the user doesn't want to or can't install something right now, ask explicitly whether they'd rather continue the initialization anyway (noting that this part of the framework won't work until it's resolved) or stop here. Don't assume which they prefer.

Only once the base tools are available (and the conditional ones that can already be determined at this point, or the user has explicitly decided to proceed without them) continue to step 1.

## 1. Check current state

- **If `.claude/pv-context.json` doesn't exist**: follow the normal process from step 2 onward (exploration + questions + full write).
- **If it exists but isn't valid JSON, or `check-context.py` below fails to run for any reason**: don't try to diagnose or fix it yourself — stop this flow and invoke `pv-update` (`Skill` tool) instead. It owns everything beyond "which optional fields were never configured": broken JSON, unknown fields, referenced skills/paths that don't exist on disk, a stale `pv.py`, `skillModels` drift, etc. Once it finishes (fixes applied and approved, or the user declined), re-run `check-context.py` and resume this step from the top — only continue the normal `pv-init` flow below if the file is now valid and there's still something left to configure.
- **If it already exists and is valid JSON**, the comparison against the required fields in [`schema.json`](schema.json) is done deterministically and for free in tokens by the script [`scripts/check-context.py`](scripts/check-context.py) (standard Python, no external dependencies) — don't eyeball it against the schema yourself. Run from the repo root:

  ```
  python .claude/skills/pv-init/scripts/check-context.py
  ```

  It prints a single JSON on stdout: `{"exists", "hasFramework", "missingRequired", "complete", "hasLanguage"}`. `framework` no longer has any field marked `required: true` in `schema.json` (`workFolder` is optional, with default `"/"`), so `missingRequired` always comes back empty — `complete` simply reflects whether the `framework` section exists. `hasLanguage` is `true` when `framework.interaction.language` exists in the file, regardless of its value — it's the only field whose absence unconditionally triggers the language question in step 3 (see below); `changes.language`/`versions.language`/`docs.*.language` are optional refinements asked in the same round but don't gate `hasLanguage`. To know which other optionals are still unconfigured, read `.claude/pv-context.json` yourself and compare it field by field against the `framework` properties in `schema.json` (`workFolder`, `docs.tech.architectureDocDir`, `docs.tech.styleBibleDocDir`, `docs.functional.featuresDocPathDir`, `sourcecodeDir`, `skillModels`) to build your own "unconfigured optionals" list. With both lists (the script's `missingRequired` + the optionals you detected):

  - **If `complete` is `true`, `hasLanguage` is `true`, and there are no other unconfigured optionals**: use `AskUserQuestion` to ask the user if they want to re-initialize the project from scratch. Make it clear that this erases the current context (`framework`) and repeats the whole question process as if it didn't exist. If they confirm, erase the current content and continue from step 2. If not, skip straight to step 5 (see the rule below) and then step 6 — don't stop here without touching anything.

    ```
    The `pv-*` framework is already initialized in this project. Do you want to reinitialize it from scratch? This erases the current configuration (`framework`) in `.claude/pv-context.json` and repeats all the questions as if it didn't exist.
    ```
  - **If `complete` is `false`** (the `framework` section doesn't exist yet): follow the normal process from step 2 onward — there's nothing to preserve with a merge.
  - **If `complete` is `true` but `hasLanguage` is `false` and/or there are other unconfigured optionals** (e.g. the user initialized once only confirming `workFolder` and declined the rest, or never got the language question because the project predates it): don't offer the destructive full reset up front. Ask first with `AskUserQuestion` whether they want to complete/review those specific optional fields (listing them, including language if `hasLanguage` is `false`) or leave things as they are; only if they explicitly ask to reset everything from scratch, follow the branch above. If they want to complete things, go to step 3 scoped to those fields and update in step 4 with a merge, same as with fields that were missing outright. If `hasLanguage` is already `true`, never ask about language again. Either way (completed now or left as-is), continue to step 5 per the rule below.

  **Beyond `check-context.py`'s own checks**, if at any point in this step (or later, while exploring the repo or writing the file) you notice something `check-context.py` doesn't cover — a path configured in `pv-context.json` that doesn't exist on disk, `framework.skills.mockups`/`diagrams` naming a skill folder that isn't there, `{repo root}/pv.py` missing or clearly stale, a `{xxxx}` change code duplicated between `inProgress`/`implemented` — don't try to fix it inline as part of this normal flow: stop and invoke `pv-update` (`Skill` tool) instead, same as the invalid-JSON case above. Resume this flow afterward only if there's still configuration left for `pv-init` itself to handle.

  **Step 5 always runs, on every invocation of this skill, regardless of which branch above was taken** — including a run where the user declines every question and nothing in `.claude/pv-context.json` changes. This is what keeps `{repo root}/pv.py` current after installing a newer version of the framework's skill files: `scaffold-project.py` always overwrites `pv.py` unconditionally and only creates folders/placeholders that don't yet exist, so re-running it against an already-configured, unchanged project is safe and idempotent — never skip straight from step 1 to "done" without it.

## 2. Explore the repo for clues

Before asking with a blank slate, look at the repo to propose reasonable defaults:

- Architecture/design document: a folder with `INDEX.md` under `docs/`, `design/` (current convention), or a loose `ARCHITECTURE.md`/`design_technical.md` (old convention, migratable).
- Features listing document: something under `docs/`, `design/`, or a `FEATURES.md`.
- Style guide (visual/interaction/writing): a folder with `INDEX.md` under `docs/`, `design/` (current convention), or a loose `STYLE_BIBLE.md` (old convention, migratable).
- Source code root folder: `src`, `app`, `lib`, or whichever carries the most weight in the repo.

## 3. Ask what's missing

Go through **all** the `framework` fields described in `schema.json`, section by section — none is assumed or left silently unresolved: required ones are always asked, optional ones are asked or explicitly confirmed (even if the most common answer is "use the default"), and only the pure fine-tuning ones (see below) may assume their default without asking. Use `AskUserQuestion` for any closed decision (confirming a detected path, choosing between options, yes/no); free text for open-ended things (project name/summary, desired style).

Fields to resolve — `framework` section:
- `workFolder`: always write the fixed default `"/previo-sdd"` silently, without asking or confirming it — same pattern as `skills.mockups`/`skills.diagrams` below, never mentioned in the questions nor in the step 6 summary. If the user ever wants a different `workFolder`, they change it themselves directly in `pv-context.json`, at their own risk — `pv-init` never offers or migrates towards an alternative. Inside `workFolder`, the `changes/`, `versions/` and `stuff/` subfolders always have fixed names — they're never asked about or configured; [`scripts/scaffold-project.py`](scripts/scaffold-project.py) (step 5) creates them right after the file is written.
- **Language** (new, always ask on a first-time init — see below for the partial-update case): first ask only the interaction language (`framework.interaction.language`) with `AskUserQuestion` — propose English as the default, making clear it can be any other language (free text, or an ISO 639-1 code like `es`, `fr`). Then ask, as a separate yes/no `AskUserQuestion`, whether they want that same language for everything else the framework writes, or want to set a different language per area. If they want the same for everything: set `changes.language`, `versions.language`, `docs.functional.language` and `docs.tech.language` to the interaction language and move on — don't ask the four questions below. If they want to configure areas individually, ask these four, in this order, each proposing the interaction language as its default and only diverging if the user says so:
  1. **Language of in-progress change/fix documents** (`framework.changes.language`) — language of the documents for a change/fix in progress (`description.md`, `plan.md`, `history.md`, and the sample text in `design_*.html`/`.txt` mockups) under `{workFolder}/changes/**`.
  2. **Language of the release changelog** (`framework.versions.language`) — language of `changelog.md`, generated by `pv-internal-changelog` under `{workFolder}/versions/{XXXX}/` from `changes/closed`.
  3. **Language of the feature documentation** (`framework.docs.functional.language`) — language of the feature listing (`featuresDocPathDir`) that `pv-do` keeps up to date after every implemented change/fix. Only ask if `docs.functional.featuresDocPathDir` is being configured in this same run.
  4. **Language of the technical documentation** (`framework.docs.tech.language`) — language shared by the architecture documentation (`architectureDocDir`) and the style bible (`styleBibleDocDir`) that `pv-do` keeps up to date after every implemented change/fix. Only ask if `docs.tech.architectureDocDir` and/or `docs.tech.styleBibleDocDir` are being configured in this same run.

  When you write or update `language`, also write (or complete) `framework._comments` with a short explanation of what each configured `language` field affects and why it was set that way — free text, one entry per field, ignored at runtime by every skill (same pattern as `skillModels._instructions`). Base each explanation on the field's description above (what it affects), plus the user's stated reason if they gave one.
- `docs.tech.architectureDocDir`, `docs.tech.styleBibleDocDir` and `docs.functional.featuresDocPathDir` (optional in the schema, but **whether they're wanted is never asked** — all three are always generated, without exception, unless there's already content to preserve). Never ask "do you want technical/style/features documentation?": that decision is already made, you only confirm paths and content.
  - Every one of the three is stored **relative to `workFolder`** (same as `changes/`/`versions/`/`stuff/` — the only path in `pv-context.json` relative to the repo root instead is `sourcecodeDir`), so it must physically live under `{workFolder}/`.
  - If the user **already has one as a folder** with `INDEX.md` (or you detected it in step 2) **and it's already under `workFolder`**, use that path as-is — don't regenerate it.
  - If the user **already has one as a folder** with `INDEX.md` but it lives **outside `workFolder`** (e.g. `docs/architecture` at the repo root while `workFolder` is `/previo-sdd`), offer to move it as-is into `{workFolder}/docs/...`, preserving its content — don't leave a duplicate copy outside `workFolder`.
  - If the user has one in the **old convention** (a single file, e.g. `ARCHITECTURE.md`/`STYLE_BIBLE.md`/`FEATURES.md`), offer to migrate it: create the folder under `{workFolder}/docs/` with an `INDEX.md` summarizing the file and a single content file (`01-contenido.md` or similar) with the rest, and delete the loose file.
  - If the user **is missing one of the three**, don't generate anything yourself here — leave its path (default or user-confirmed) written in `pv-context.json` as-is. [`scripts/scaffold-project.py`](scripts/scaffold-project.py) (step 5, run right after the file is written) creates the empty folder with its minimal placeholder deterministically, for free in tokens, instead of the model drafting it by hand on every init.
  - If the user **explicitly decides they don't want one of the three** when shown the summary in step 6 (e.g. they're not interested in maintaining a style guide), respect that decision: delete what `scaffold-project.py` generated for that field in step 5 and leave the field undefined in `pv-context.json` — the rest of the skills treat it as optional and skip it without asking anything.
- `sourcecodeDir` (optional, default `"/src"`, but always ask/confirm it — don't assume it silently): propose the source code root folder detected in step 2 and ask for confirmation with `AskUserQuestion` (or the right name if detection failed). Write it with a leading `/` (e.g. `/src`, `/app`), relative to the repo root — the same convention as `workFolder`, to make it visually obvious it's not relative to `workFolder` like `docs.*` is. Used by `pv-how` as fallback context when `docs.tech.architectureDocDir` doesn't exist.
- `numberWidth` (optional, default `5`, no need to ask unless the user wants something different): always write it to `pv-context.json` — the default value if the user doesn't want something else, same as `skills.mockups`/`skills.diagrams` below — never leave the field absent. The scripts that consume it (`next-change-number.py`, `get-max-change-codes.py`) have no fallback of their own and fail if it's missing.
- `skills.mockups` and `skills.diagrams`: always write their defaults (`pv-internal-mockups-html`, `pv-internal-tech-mermaid`) to the file silently, without asking about them or mentioning them anywhere in this init — not in the questions, not in the step 6 summary. If the user ever wants to swap the underlying skill/technology, they'll find that documented in `schema.json` themselves.

`skillModels` section (optional in the schema, but **always written** by `pv-init`, even on a run where the user changes nothing) — compute the baseline deterministically and for free in tokens with:

```
python .claude/skills/pv-init/scripts/collect-skill-models.py
```

It reads every `pv-*/SKILL.md`'s real `model`/`effort` frontmatter and returns the proposed `default` (the most common pair) plus `overrides` (one entry per skill whose frontmatter differs from that pair) — a straight mirror of what's already on disk, so `pv-context.json` never claims a baseline that doesn't match reality. Write that result as-is into `skillModels.default`/`skillModels.overrides`, and always mention it (even briefly) don't skip it silently: ask if the user wants to change anything upfront on top of that mirrored baseline (e.g. dropping another mechanical skill to Haiku, or raising some skill's effort). If they don't want to touch anything now, still write the mirrored baseline — never leave the section absent. If they configure something different from the mirrored baseline, remind the user in step 5 that they must run `python .claude/skills/pv-init/scripts/sync-skill-models.py` for the change to actually take effect on the `SKILL.md` files (this section alone isn't enough, see its `description` in `schema.json`) — a freshly mirrored baseline with no user changes is already in sync and doesn't need that run.

**Partial update case**: if `complete` was already `true` but `hasLanguage` was `false` (project initialized before language support existed), include the language question in the same round as any other unconfigured optionals — don't create a separate round for it. If `hasLanguage` is already `true`, don't ask about language again in this run.

## 4. Write the file

Create `.claude/` if it doesn't exist. Write (or update with a merge, without overwriting fields already present that the user didn't ask to change) `.claude/pv-context.json` matching the shape of [`schema.json`](schema.json) — same field names, no properties outside what the schema declares (`additionalProperties: false` at every level).

## 5. Scaffold the base structure and the `pv.py` launcher

Run [`scripts/scaffold-project.py`](scripts/scaffold-project.py) from the repo root:

```
python .claude/skills/pv-init/scripts/scaffold-project.py
```

It reads the `.claude/pv-context.json` just written in step 4 and deterministically creates, only where nothing already exists (never overwrites or touches existing content):

- `workFolder`'s fixed subfolders — `changes/{inProgress,implemented,todo,closed}`, `versions/`, `stuff/` — empty, with a `.gitkeep` so git tracks them.
- The folder + placeholder for whichever of `docs.tech.architectureDocDir`/`docs.tech.styleBibleDocDir`/`docs.functional.featuresDocPathDir` are configured. `docs.functional.featuresDocPathDir` follows a different convention from the other two (an `INDEX.md` regenerated via `pv-internal-doc-features`, never hand-written, and no `01-overview.md`) — the script already applies that difference on its own, nothing to decide here.

It also copies [`assets/pv.py`](assets/pv.py) to `{repo root}/pv.py`, always overwriting whatever was there — it's a generated file, not user content, copied as-is without modifying a single line of it.

It prints a single JSON on stdout naming what it created and what it skipped because something already existed at that path — read it to know what to report in step 6, instead of inspecting the disk by hand.

For each of `docs.tech.architectureDocDir`/`docs.tech.styleBibleDocDir` the script just created (`status: "created"` in its output, not `"skipped"` or `"not_configured"`), **tell the user you generated it** (path and that it's a minimal placeholder) and **then** ask them in free text what they want to contribute to enrich its `01-overview.md` (what the project is about, technologies, desired style/visual references; if there are no style/palette clues either from the user or from step 2, fall back to the neutral black/white/grayscale palette already used as default). Edit that file yourself with their answer. If the user doesn't contribute anything, leave the generated minimal version as-is. `docs.functional.featuresDocPathDir` is never asked about this way — it's left for `pv-do` to fill in with each implemented change.

`pv.py` is a single self-contained Python file meant for anyone on the team to check or close framework changes directly from a terminal (`python3 pv.py`), without going through Claude Code or having to remember script names, paths or parameters: running it shows an interactive menu. Today it exposes `pv-status`'s read-only queries (general report, listing filtered by state, `todo/` ideas) and closing an implemented entry (moving its folder from `changes/implemented/` to `changes/closed/`, delegating to `pv-internal-workflow`'s `move-change.py` — an operation that only moves the folder, without touching any file's content, and which the menu explicitly confirms before running). This is the only place the skill expands if some other script turns out to be fit for direct exposure in the future: either plainly read-only, or mutations just as simple and already validated by their own script (like moving a folder) that are also explicitly confirmed before running. More complex mutations (deleting, creating versions, files with content to draft...) stay out of here, since they need context that only the corresponding skill can provide.

`pv.py` and the folders `scaffold-project.py` creates under `workFolder` (kept non-empty in git via their `.gitkeep`) are versioned in git like any other framework file (same as `.claude/pv-context.json`) — don't add them to `.gitignore`.

## 6. Verify and confirm

Before considering the initialization done:

1. Run `python .claude/skills/pv-init/scripts/check-context.py` again on the freshly written file and check it returns `"complete": true` (and `"hasLanguage": true` if language was configured in this run). If not, something was written wrong (e.g. the `framework` section ended up empty or was never written) — fix it before continuing, don't assume it's fine without checking.
2. Check step 5's `scaffold-project.py` output: every folder it reports as `"created"` or `"skipped"` should be configured and real on disk — a `docs.*` field with no matching entry in that JSON means it wasn't picked up correctly. If any of the three was left undefined because the user explicitly declined it, confirm no trace was left on disk or in the JSON (see step 5's decline handling).
3. Confirm `{repo root}/pv.py` exists and matches [`assets/pv.py`](assets/pv.py) (step 5's `pvPy.status` should read `"overwritten"`).

Show the user a complete summary of what was configured: the file's path, every `framework` field resolved (including ones left unconfigured and why), the resolved language configuration (`interaction.language`/`changes.language`/`versions.language`/`docs.*.language`, and what was written to `framework._comments`), the `skillModels` baseline written (`default`, and `overrides` if any skill differs from it — always written now, even with no customization), with the reminder to run `sync-skill-models.py` only if the user changed something beyond the mirrored baseline, and that they can now run `python3 pv.py` from the repo root to check the framework's status without going through Claude Code. Remind the user they can invoke this skill again to reconfigure any field later.
