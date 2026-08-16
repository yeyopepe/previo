---
name: pv-init
description: Initializes the pv-* framework (change/fix/workflow) in the current project, generating .claude/pv-context.json with the required configuration (folder/file paths for the change-tracking process, plus language configuration). Trigger: /pv-init, or when any other pv-* skill needs .claude/pv-context.json and it doesn't exist (or is missing fields), or when the user asks to "set up"/"configure" this framework in a new project.
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.2
  uses: []
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
- **If it already exists**, the comparison against the required fields in [`schema.json`](schema.json) is done deterministically and for free in tokens by the script [`scripts/check-context.py`](scripts/check-context.py) (standard Python, no external dependencies) — don't eyeball it against the schema yourself. Run from the repo root:

  ```
  python .claude/skills/pv-init/scripts/check-context.py
  ```

  It prints a single JSON on stdout: `{"exists", "hasFramework", "missingRequired", "complete", "hasLanguage"}`. `framework` no longer has any field marked `required: true` in `schema.json` (`workFolder` is optional, with default `"/"`), so `missingRequired` always comes back empty — `complete` simply reflects whether the `framework` section exists. `hasLanguage` is `true` when `framework.interaction.language` exists in the file, regardless of its value — it's the only field whose absence unconditionally triggers the language question in step 3 (see below); `changes.language`/`versions.language`/`docs.*.language` are optional refinements asked in the same round but don't gate `hasLanguage`. To know which other optionals are still unconfigured, read `.claude/pv-context.json` yourself and compare it field by field against the `framework` properties in `schema.json` (`workFolder`, `docs.tech.architectureDocDir`, `docs.tech.styleBibleDocDir`, `docs.functional.featuresDocPathDir`, `sourcecodeDir`, `skillModels`) to build your own "unconfigured optionals" list. With both lists (the script's `missingRequired` + the optionals you detected):

  - **If `complete` is `true`, `hasLanguage` is `true`, and there are no other unconfigured optionals**: use `AskUserQuestion` to ask the user if they want to re-initialize the project from scratch. Make it clear that this erases the current context (`framework`) and repeats the whole question process as if it didn't exist. If they confirm, erase the current content and continue from step 2. If not, do nothing further — the framework is already ready as it stands.

    ```
    The `pv-*` framework is already initialized in this project. Do you want to reinitialize it from scratch? This erases the current configuration (`framework`) in `.claude/pv-context.json` and repeats all the questions as if it didn't exist.
    ```
  - **If `complete` is `false`** (the `framework` section doesn't exist yet): follow the normal process from step 2 onward — there's nothing to preserve with a merge.
  - **If `complete` is `true` but `hasLanguage` is `false` and/or there are other unconfigured optionals** (e.g. the user initialized once only confirming `workFolder` and declined the rest, or never got the language question because the project predates it): don't offer the destructive full reset up front. Ask first with `AskUserQuestion` whether they want to complete/review those specific optional fields (listing them, including language if `hasLanguage` is `false`) or leave things as they are; only if they explicitly ask to reset everything from scratch, follow the branch above. If they want to complete things, go to step 3 scoped to those fields and update in step 4 with a merge, same as with fields that were missing outright. If `hasLanguage` is already `true`, never ask about language again.

## 2. Explore the repo for clues

Before asking with a blank slate, look at the repo to propose reasonable defaults:

- Existing changes folder: `_changes`, `changes`, `CHANGELOG*`.
- Architecture/design document: a folder with `INDEX.md` under `docs/`, `design/` (current convention), or a loose `ARCHITECTURE.md`/`design_technical.md` (old convention, migratable).
- Features listing document: something under `docs/`, `design/`, or a `FEATURES.md`.
- Style guide (visual/interaction/writing): a folder with `INDEX.md` under `docs/`, `design/` (current convention), or a loose `STYLE_BIBLE.md` (old convention, migratable).
- Source code root folder: `src`, `app`, `lib`, or whichever carries the most weight in the repo.

## 3. Ask what's missing

Go through **all** the `framework` fields described in `schema.json`, section by section — none is assumed or left silently unresolved: required ones are always asked, optional ones are asked or explicitly confirmed (even if the most common answer is "use the default"), and only the pure fine-tuning ones (see below) may assume their default without asking. Use `AskUserQuestion` for any closed decision (confirming a detected path, choosing between options, yes/no); free text for open-ended things (project name/summary, desired style).

Fields to resolve — `framework` section:
- `workFolder` (optional, default `"/"`, but always ask/confirm it — don't assume it silently, same as `sourcecodeDir`): it's the only path the user chooses for all of the framework's work. Propose `"/"` (repo root) as the recommended option; if the repo already has an existing changes folder detected in step 2 (`_changes`, `changes`...) and it doesn't match the root, point this out to the user and offer to migrate its content into `{workFolder}/changes/` instead of creating both separately. Inside `workFolder`, the `changes/` and `versions/` subfolders always have fixed names — they're never asked about or configured, the relevant skills create them the first time they're needed.
- **Language** (new, always ask on a first-time init — see below for the partial-update case): use `AskUserQuestion` with these sub-questions, in this order:
  1. **Interaction language** (`framework.interaction.language`) — propose English as the default, making clear it can be any other language (free text, or an ISO 639-1 code like `es`, `fr`).
  2. **Language of in-progress change/fix documents** (`framework.changes.language`) — propose the same as interaction by default, only asking if they want a different one.
  3. **Language of the release changelog** (`framework.versions.language`) — same pattern, propose interaction's language by default.
  4. **Language of each `framework.docs` area already resolved in this same step** (`docs.functional.language`, `docs.tech.language`, whichever apply given what the user has configured) — same pattern.

  When you write or update `language`, also write (or complete) `framework._comments` with a short explanation of each configured `language` field — free text, one entry per field (e.g. `"changes.language": "team documents in-progress work in Spanish"`), ignored at runtime by every skill (same pattern as `skillModels._instructions`).
- `docs.tech.architectureDocDir`, `docs.tech.styleBibleDocDir` and `docs.functional.featuresDocPathDir` (optional in the schema, but **whether they're wanted is never asked** — all three are always generated, without exception, unless there's already content to preserve). Never ask "do you want technical/style/features documentation?": that decision is already made, you only confirm paths and content.
  - If the user **already has one as a folder** with `INDEX.md` (or you detected it in step 2), use that path as-is — don't regenerate it.
  - If the user has one in the **old convention** (a single file, e.g. `ARCHITECTURE.md`/`STYLE_BIBLE.md`/`FEATURES.md`), offer to migrate it: create the folder with an `INDEX.md` summarizing the file and a single content file (`01-contenido.md` or similar) with the rest, and delete the loose file.
  - If the user **is missing one of the three**, generate directly a **minimal first version** without asking anything first — use what you already know about the repo (step 2: project type, detected stack, existing files) and, if the repo is empty or doesn't give enough clues, a reasonable generic placeholder. Don't block generation waiting for the user's answers:
    - Architecture (default `design/docs/architecture/`): a folder with `INDEX.md` (minimal index table, a single sibling file for now) and `01-overview.md` with what's known about the project and its stack, as a starting point `pv-do` will keep expanding with each implemented change.
    - Style guide (default `design/docs/style/`): same `INDEX.md` + `01-overview.md` pattern; if there are no style/palette clues, fall back to the neutral black/white/grayscale palette already used as default.
    - Features (default `design/docs/features/`): a folder with an empty or minimal `INDEX.md` (listing of implemented features, which `pv-do` will fill in over time).

    Once all three are created, **tell the user you generated them** (paths and what each contains) and **then** ask them in free text what they want to contribute to the **technical** and **style** documentation (what the project is about, technologies, desired style/visual references) to enrich each `01-overview.md` with their answers — the features one isn't asked about, it's left for `pv-do` to fill in with each change. If the user doesn't contribute anything, leave the generated minimal version as-is.
  - If the user **explicitly decides they don't want one of the three** when shown the summary (e.g. they're not interested in maintaining a style guide), respect that decision: delete what was generated for that field and leave the field undefined in `pv-context.json` — the rest of the skills treat it as optional and skip it without asking anything.
- `sourcecodeDir` (optional but always ask/confirm it — don't assume it silently): propose the source code root folder detected in step 2 and ask for confirmation with `AskUserQuestion` (or the right name if detection failed). Used by `pv-how` as fallback context when `docs.tech.architectureDocDir` doesn't exist.
- `numberWidth` (optional, default `4`, no need to ask unless the user wants something different).
- `skills.mockups` (optional, default `pv-internal-mockups-html`, no need to ask unless the user wants a different skill/technology to generate `pv-new`/`pv-fix`'s `design_*.html` mockups).
- `skills.diagrams` (optional, default `pv-internal-tech-mermaid`, no need to ask unless the user wants a different skill/notation to generate `pv-internal-workflow`/`pv-new`/`pv-fix`/`pv-how`'s Mermaid diagrams).

`skillModels` section (optional, outside `framework`) — always mention it, even briefly, don't skip it silently: ask if the user wants to fix upfront a model/effort different from what each `SKILL.md` already has for some `pv-*` skill (e.g. dropping the more mechanical ones like `pv-status`/`pv-todo` to Haiku, or raising `pv-do`'s effort). If they don't want to touch anything now, skip the section entirely — the default is whatever each `SKILL.md` already carries in its own frontmatter. If they configure something, remind the user in step 5 that they must run `python .claude/skills/pv-init/scripts/sync-skill-models.py` for the change to actually take effect (this section alone isn't enough, see its `description` in `schema.json`).

**Partial update case**: if `complete` was already `true` but `hasLanguage` was `false` (project initialized before language support existed), include the language question in the same round as any other unconfigured optionals — don't create a separate round for it. If `hasLanguage` is already `true`, don't ask about language again in this run.

## 4. Write the file

Create `.claude/` if it doesn't exist. Write (or update with a merge, without overwriting fields already present that the user didn't ask to change) `.claude/pv-context.json` matching the shape of [`schema.json`](schema.json) — same field names, no properties outside what the schema declares (`additionalProperties: false` at every level).

## 5. Copy/update the `pv.py` launcher

Copy [`assets/pv.py`](assets/pv.py) to `{repo root}/pv.py`, overwriting whatever was there — it's a generated file, not user content, copy it as-is without modifying a single line of its content.

It's a single self-contained Python file meant for anyone on the team to check or close framework changes directly from a terminal (`python3 pv.py`), without going through Claude Code or having to remember script names, paths or parameters: running it shows an interactive menu. Today it exposes `pv-status`'s read-only queries (general report, listing filtered by state, `todo/` ideas) and closing an implemented entry (moving its folder from `changes/implemented/` to `changes/closed/`, delegating to `pv-internal-workflow`'s `move-change.py` — an operation that only moves the folder, without touching any file's content, and which the menu explicitly confirms before running). This is the only place the skill expands if some other script turns out to be fit for direct exposure in the future: either plainly read-only, or mutations just as simple and already validated by their own script (like moving a folder) that are also explicitly confirmed before running. More complex mutations (deleting, creating versions, files with content to draft...) stay out of here, since they need context that only the corresponding skill can provide.

This file is versioned in git like any other framework file (same as `.claude/pv-context.json`) — don't add it to `.gitignore`.

## 6. Verify and confirm

Before considering the initialization done:

1. Run `python .claude/skills/pv-init/scripts/check-context.py` again on the freshly written file and check it returns `"complete": true` (and `"hasLanguage": true` if language was configured in this run). If not, something was written wrong (e.g. the `framework` section ended up empty or was never written) — fix it before continuing, don't assume it's fine without checking.
2. If `docs.tech.architectureDocDir`/`docs.tech.styleBibleDocDir`/`docs.functional.featuresDocPathDir` were generated in this step, confirm that each folder and its files (`INDEX.md` + `01-overview.md`, as applicable) really exist on disk.
3. If any of the three was left undefined because the user explicitly declined it, confirm no trace was left on disk or in the JSON.
4. Confirm `{repo root}/pv.py` exists and matches [`assets/pv.py`](assets/pv.py).

Show the user a complete summary of what was configured: the file's path, every `framework` field resolved (including ones left unconfigured and why), the resolved language configuration (`interaction.language`/`changes.language`/`versions.language`/`docs.*.language`, and what was written to `framework._comments`), whether anything was set in `skillModels` (with the reminder to run `sync-skill-models.py` if applicable), and that they can now run `python3 pv.py` from the repo root to check the framework's status without going through Claude Code. Remind the user they can invoke this skill again to reconfigure any field later.
