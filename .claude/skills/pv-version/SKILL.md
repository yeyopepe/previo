---
name: pv-version
description: Prepares a project release/version at {workFolder}/versions/{XXXX}/ — generates the deliverable, copies the current technical documentation, and chains pv-internal-changelog for the functional changelog. Part of the pv-* framework. Trigger: /pv-version <XXXX>, or when the user asks to prepare/package a deliverable version.
argument-hint: <XXXX of the version to prepare>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b6
  uses: [pv-internal-changelog]
---

# pv-version

Orchestrates preparing a project release: resolves change/fix entries pending closure, generates the deliverable, copies the current technical documentation, and chains `pv-internal-changelog` to draft the functional changelog from `{workFolder}/changes/closed/`.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation, including the fixed messages below. Copying technical documentation and generating the deliverable are copy/build operations, not new prose (`language` doesn't apply); it chains `pv-internal-changelog` for `changelog.md`. If `language` is not configured anywhere, everything is English.

`{workFolder}` is `.claude/pv-context.json`'s `framework.workFolder` value (default `"/previo-sdd"`, never asked/confirmed by `pv-init`). Inside it, `changes/`, `versions/` and `stuff/` are fixed-name subfolders the framework creates by itself — not asked about or configured separately. `{workFolder}/versions/{XXXX}/` is a free-text numbering space, chosen by the user on each invocation, with no relation to change/fix's `xxxx` nor to any other folder called "versions" that might exist in the repo (e.g. a build script's own output): this skill never reads or writes outside `{workFolder}/versions/`.

## 0. Framework initialized

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

## 0.1. Process diagram, on demand

At any point during invocation, if the user asks how the process works or explicitly asks for "the diagram"/"the flow", show [`version-flow-diagram.template.md`](version-flow-diagram.template.md)'s full content as-is (without regenerating or paraphrasing it) and continue wherever the flow had gotten to.

## 0.2. Purely informational invocation about the build process

The user might invoke this skill only to report a change in the build/deliverable-generation procedure (e.g. "the build now also generates a rules PDF", "change the build command to..."), without explicitly asking to prepare a release right now.

If that's the intent: update `{workFolder}/stuff/how-to-compile-version.md` with the new information, following [`how-to-compile-version.template.md`](how-to-compile-version.template.md) (including its support for multi-step/multi-artifact processes if applicable — see the template itself), and **don't continue with the rest of the flow**. Explicitly ask the user whether they want to launch the versioning process now with this now-updated procedure. Only if they specifically confirm, continue with step 0.5; if they don't confirm (or don't answer that), stop here.

## 0.5. Guardrail: `implemented/` must be empty before starting

When starting the versioning process there can be no change/fix in the `implemented` state. List `{workFolder}/changes/implemented/`'s folders; if there's any, **there's no way to proceed at all** (not creating the version's folder, nor anything that follows) until all of them are resolved.

For each folder found, explicitly ask the user whether that change/fix moves to `closed`:

- If they confirm, run (from the repo root):

  ```
  python .claude/skills/pv-internal-workflow/scripts/move-change.py --xxxx <xxxx> --from implemented --to closed
  ```

- If they don't confirm, **wait for the user's confirmation** without continuing the flow — the entry isn't skipped or ignored, there's no "continue anyway".

Repeat until `implemented/` is empty; only then continue with step 1.

## 1. Resolve `XXXX`

If not given when invoking, ask explicitly — don't assume it. It's free text chosen by the user, not computed or validated against `numberWidth` (a numbering space independent from change/fix's).

## 2. Create the version's folder

Run from the repo root:

```
python .claude/skills/pv-version/scripts/init-version-folder.py --xxxx <XXXX>
```

Creates `{workFolder}/versions/{XXXX}/` with empty `files/` and `docs/` subfolders, and prints the created path. If `{workFolder}/versions/{XXXX}/` already exists, the script exits with an error without touching anything — in that case, ask the user whether they want to continue over what already exists (regenerate) or choose another `XXXX`, and return to this step with the new value if applicable.

## 3. Check `how-to-compile-version.md`

Look for `{workFolder}/stuff/how-to-compile-version.md` (the project's own file, not the skill's nor `pv-context.json`'s: it's a shell/build procedure, not declarative configuration).

- **If it doesn't exist**: ask the user for this project's exact procedure to generate the deliverable (which command(s) to run, where the resulting file ends up and how to identify it — or, if the process has several steps generating different artifacts, each step with its own command and resulting file), and write it following [`how-to-compile-version.template.md`](how-to-compile-version.template.md). Don't continue with step 4 in the same reply without having saved the file.
- **If it already exists**: read it and follow it as-is, without asking again.

## 4. Generate the version

Run the command(s) `how-to-compile-version.md` gives (one per step, if the procedure has several) and locate the resulting file(s) as it describes. If any command fails or the expected file doesn't show up, stop and explain it to the user instead of improvising an alternative solution.

With all artifacts located, copy them to `{workFolder}/versions/{XXXX}/files/` by running from the repo root (one `--source` per artifact, even if it comes from a single step):

```
python .claude/skills/pv-version/scripts/copy-build-artifacts.py --xxxx <XXXX> --source <artifact-path-1> [--source <artifact-path-2> ...]
```

## 5. Copy technical and functional documentation

Only if step 4 generated the deliverable correctly. Run from the repo root:

```
python .claude/skills/pv-version/scripts/copy-docs.py --xxxx <XXXX>
```

Reads `.claude/pv-context.json`'s `framework.docs.tech.architectureDocDir`, `framework.docs.tech.styleBibleDocDir` and `framework.docs.functional.featuresDocPathDir` (whichever are configured; if none are, it's skipped without asking, same as `pv-do` does), zips each one (the whole folder with all its files, including its `INDEX.md`; or the single `.md` file, if that path isn't a folder) and saves it at `{workFolder}/versions/{XXXX}/docs/`. Note what was copied and what was skipped (the script returns this in its JSON output) for step 7's summary.

## 6. Generate the changelog

Invoke the `pv-internal-changelog` skill (Skill tool) passing it the destination folder `{workFolder}/versions/{XXXX}/`.

## 7. Confirm to the user

Summarize what was generated: the deliverable in `files/`, zipped docs in `docs/` (or which ones were skipped for not being configured), and that the changelog ended up in `changelog.md` — use the summary `pv-internal-changelog` returns to you (number of entries per section, including Fixes, and whether `{workFolder}/changes/closed/`'s folders were deleted or not).
