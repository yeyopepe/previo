# Previo v0.9.5b11 changelog (from v0.9.21)

## Index

- ⭐[New](#new)
  - Framework configuration audit and repair (`pv-update`)
  - Every skill now blocks until the framework configuration is verified
  - Per-document-type language configuration
  - Writing style rules for technical documentation
  - Automatic project scaffolding
  - Documentation generation for pre-existing codebases
  - Existing documentation can be adopted as-is
  - Risk score surfaced in status reports
  - Release count in the status summary
  - Collaborative refinement when promoting a todo idea
  - Ability to delete a todo idea
  - Changelog drafting is now isolated from concurrent closures
- ✏️[Changed](#changed)
  - Working folder is no longer configurable at setup, and its default changed
  - Build-procedure file moved to a renamed project folder
  - Placeholder documentation is generated after scaffolding, not during questioning
  - Change-code numbering width increased
  - `skillModels` baseline is always recorded
  - Status report tolerates a missing changes folder
  - "In progress" ordering changed in the status report
  - Closed-changes staging folder excluded from status counts
  - Standalone `pv.py` script expanded

## ⭐New

- **Framework configuration audit and repair (`pv-update`)** — A new skill audits `pv-context.json` against the framework's schema, checks that referenced skills and on-disk paths exist, verifies change/fix documents weren't altered or mistranslated, detects duplicate change codes, confirms every `pv-*` skill shares the same version, and reconciles the installed version against what was last verified. It fixes what it can determine unambiguously and only stops to ask the user when `pv-context.json` can't be parsed or a downgrade is detected. `pv-init` now hands off to it when its own checks find something broken.
- **Every skill now blocks until the framework configuration is verified** — `pv-new`, `pv-fix`, `pv-how`, `pv-do`, `pv-status`, `pv-todo`, and `pv-version` now check the installed framework version against `pv-context.json`'s recorded "last verified" version at startup, and refuse to continue if they don't match, if verification was never recorded, or if a downgrade was flagged. **Action required when updating: run `pv-update` once before using any other `pv-*` skill.**
- **Per-document-type language configuration** — The framework can now be configured with separate languages for chat interaction, in-progress change/fix documents, the release changelog, functional feature documentation, and technical documentation, instead of one implicit language for everything. `pv-init` asks about this on first setup, and every `pv-*` skill that writes user-facing content now writes it in the language configured for that document type. This adds new fields to `pv-context.json`'s schema.
- **Writing style rules for technical documentation** — A new `pv-internal-doc-technical` skill enforces how architecture and style-bible documentation is written (dense fact fragments, code/signatures instead of explanatory prose, tables for parallel structures, fixed vocabulary tags), since this documentation is read by other framework steps rather than by a person. `pv-do` now loads these rules before drafting or editing that documentation.
- **Automatic project scaffolding** — `pv-init` now creates the framework's full base folder structure itself right after writing the configuration, instead of leaving folder creation to whichever skill needed it first.
- **Documentation generation for pre-existing codebases** — When `pv-init` runs on a project that already has source code, it now offers to analyze that code and generate architecture, style, and feature documentation from it, at a "minimum" or "complete" depth chosen by the user.
- **Existing documentation can be adopted as-is** — If a project already has architecture, style, or feature documentation living outside the framework's working folder, `pv-init` now offers to move it in unchanged, rather than only recognizing docs already in place or requiring a full migration.
- **Risk score surfaced in status reports** — `pv-status` reports now show each planned entry's risk score alongside its other details; entries not yet planned show as unscored.
- **Release count in the status summary** — The main `pv-status` report now also shows how many releases have been prepared, alongside the existing per-state totals.
- **Collaborative refinement when promoting a todo idea** — Converting a todo idea into a documented change now explicitly offers to develop the idea further in conversation before writing it up, instead of documenting it as-is.
- **Ability to delete a todo idea** — A queued idea in the todo backlog can now be deleted outright, rather than only ever being promoted into the normal change/fix flow.
- **Changelog drafting is now isolated from concurrent closures** — `pv-internal-changelog` now stages every pending closed entry into an isolated working copy before drafting the changelog, so a change/fix closed elsewhere while a release is being prepared can no longer interfere with the changelog currently being written.

## ✏️Changed

- **Working folder is no longer configurable at setup, and its default changed** — `pv-init` no longer asks where the framework should keep its work: it's now always set to a fixed, dedicated subfolder at the repo root (previously the repo root itself was the default, and the user was always asked to confirm or change it). Anyone wanting a different location must now edit `pv-context.json` by hand.
- **Build-procedure file moved to a renamed project folder** — The project-specific build procedure that `pv-version` reads and writes now lives under a folder named `stuff/` instead of `framework/`. Existing projects need this file relocated to the new folder; `pv-update` covers this in its repair pass.
- **Placeholder documentation is generated after scaffolding, not during questioning** — Previously, `pv-init` drafted an initial version of missing architecture, style, and feature docs by hand while asking setup questions. Now the scaffolding step creates the folders with a minimal placeholder first, and only afterward asks what the user wants to add.
- **Change-code numbering width increased** — The default zero-padded width for change/fix codes increased from 4 to 5 digits, and is now always written explicitly to configuration.
- **`skillModels` baseline is always recorded** — `pv-init` now always inspects and writes each installed skill's actual model/effort as the `skillModels` baseline, even when the user customizes nothing; previously this section was written only if the user asked to change something.
- **Status report tolerates a missing changes folder** — `pv-status` no longer errors on a freshly initialized project with no changes folder yet; it's now reported the same as an existing-but-empty one.
- **"In progress" ordering changed in the status report** — Within the full status report, entries already planned (pending implementation) are now listed before entries pending technical analysis, the reverse of before.
- **Closed-changes staging folder excluded from status counts** — `pv-status` now recognizes the transient staging area used while a changelog is being drafted and excludes it from totals and listings, instead of counting it as a real entry.
- **Standalone `pv.py` script expanded** — The `pv.py` tool distributed into every project (usable without Claude Code) gained a settings/configuration submenu, a way to browse past releases and read their changelog, search-by-id and search-by-content lookups, and an idea-deletion option, alongside exposing the framework changes above (such as skill-model sync).
