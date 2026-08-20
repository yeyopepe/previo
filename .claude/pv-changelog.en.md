# Previo v0.9.5b10 changelog (from v0.9.21)

## Index

- ⭐ [New](#new)
  - Configurable multi-language support
  - Framework version verification gate
  - Added the `pv-update` skill
  - Added a shared writing-style skill for technical documentation
  - Framework now ships a user guide
  - Risk indicator surfaced in status reports
  - Search added to the terminal status view
  - New fixed subfolder for miscellaneous framework files
- ✏️ [Changed](#changed)
  - "Fast" fix risk threshold relaxed
  - `pv-init`'s default working folder changed and setup streamlined
  - Placeholder documentation created empty instead of pre-drafted
  - `pv-init` now hands off drift/corruption repair to `pv-update`
  - Reordered and relabeled the in-progress breakdown in `pv-status`
  - `pv-status` no longer errors on a brand-new project
  - Internal staging excluded from status counts
  - Terminal status report restructured into pages
  - Changelog drafting now stages entries in isolation
  - Fixed incorrect folder resolution for custom working-folder configurations

## ⭐New

- **Configurable multi-language support** — `pv-init` now asks, on first setup, for a chat interaction language and, optionally, separate languages for in-progress change/fix documents, the release changelog, feature docs, and technical docs. All skills that write or speak to the user (`pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`, `pv-todo`, `pv-version`, and the shared `pv-internal-doc-features`, `pv-internal-mockups-ascii`/`html`, `pv-internal-tech-mermaid`, `pv-internal-workflow`, `pv-internal-changelog` skills) now honor these settings instead of always writing in English, while keeping a fixed set of structural field labels (e.g. `Area`, `Available in`, `Code`, `Since`) always in English so parsing scripts keep working. Consuming projects should re-run `pv-update`/`pv-init` to pick up the new configuration fields.
- **Framework version verification gate** — `pv-context.json` now tracks a `frameworkStatus` field recording the last verified framework version and whether it's currently blocked. Before doing any work, `pv-do`, `pv-fix`, `pv-how`, `pv-init`, `pv-new`, `pv-status`, `pv-todo`, and `pv-version` now compare it against the installed framework version and stop, directing the user to run `pv-update`, if they don't match or the framework is flagged as blocked. Consuming projects should run `pv-update` after upgrading the framework so this status gets recorded.
- **Added the `pv-update` skill** — a new skill that audits the framework's configuration and installed state in a project (the shape of `pv-context.json`, referenced skills, on-disk paths, freshness of the distributed launcher script, model/effort drift, structural markers in change documents, duplicate change codes, and version consistency across skills) and automatically fixes what it can determine unambiguously, only pausing to ask the user when configuration is unparseable or an installed version looks like a downgrade.
- **Added a shared writing-style skill for technical documentation** — `pv-internal-doc-technical` prescribes a dense, fact-first writing style (fragments over prose, tables for parallel data, fixed English status tags) for the architecture and style-bible documents, since they're read by other framework skills rather than by a human. `pv-do` now follows it whenever it drafts or edits that documentation.
- **Framework now ships a user guide** — added a `pv-guide` document (English and Spanish) that walks through setting up and using the framework end to end: initial setup, folder structure, the core document → plan → implement workflow, preparing a release, a full worked example, and customization options.
- **Risk indicator surfaced in status reports** — `pv-status` now reads the technical risk score that `pv-how` calculates for a plan and displays it in the general report, the filtered per-state listing, and the terminal detail views, alongside a new total version count shown at the top of the report.
- **Search added to the terminal status view** — the terminal status screen can now look up an entry by its code or by matching text in its description, across all workflow states, instead of only filtering by a single state.
- **New fixed subfolder for miscellaneous framework files** — a `stuff/` subfolder was added alongside the existing `changes/`/`versions/` folders, created automatically during setup, and the build-procedure reference file now lives there.

## ✏️Changed

- **"Fast" fix risk threshold relaxed** — `pv-fix`'s criteria for treating a change as trivial ("fast", skipping planning) now allows up to 10% risk to the rest of the application, instead of requiring exactly zero risk.
- **`pv-init`'s default working folder changed and setup streamlined** — the default working folder is no longer the repository root; it's a dedicated `previo-sdd` subfolder, and it's no longer asked about during setup (written automatically, like the mockup/diagram skill choices). Documentation folder paths (architecture, style bible, features) are now resolved relative to that working folder instead of the repository root, and `pv-init` offers to move an existing doc folder into it if one is found elsewhere. Consuming projects should re-run `pv-init` to adopt the new folder layout.
- **Placeholder documentation created empty instead of pre-drafted** — when `pv-init` sets up new documentation folders, it now creates them empty and defers filling in real content to a later step, instead of generating best-guess placeholder content up front.
- **`pv-init` now hands off drift/corruption repair to `pv-update`** — if `pv-init` finds a broken or inconsistent `pv-context.json` (invalid JSON, a configured path that no longer exists, an outdated launcher script, or a skill/config mismatch), it now stops and delegates the repair to `pv-update` instead of attempting to fix it itself, resuming afterward only if configuration is still incomplete.
- **Reordered and relabeled the in-progress breakdown in `pv-status`** — the "planned, pending implementation" group is now listed before "pending technical analysis," reflecting the more natural order of progress.
- **`pv-status` no longer errors on a brand-new project** — a missing changes folder is now treated the same as an empty one, so a project with nothing tracked yet gets a normal "no entries" report instead of failing.
- **Internal staging excluded from status counts** — `pv-status` now skips the internal folder used while a release is being staged, so it no longer affects totals or listings.
- **Terminal status report restructured into pages** — the terminal rendering now splits into paced summary/detail/warnings pages instead of one long dump, and ends with an interactive prompt to pull up a specific entry's detail.
- **Changelog drafting now stages entries in isolation** — when drafting the release changelog, closed entries are moved into an isolated staging copy before being read and classified, and only that staged copy is read from and deleted afterward. This means entries closed while a release is being prepared no longer risk interfering with the changelog draft in progress, and deleting the folded-in entries after drafting no longer needs separate user confirmation, since it only touches the isolated copy.
- **Fixed incorrect folder resolution for custom working-folder configurations** — the change-numbering and folder-move logic used across the framework fixed a bug where a leading slash in a custom working-folder setting could cause the rest of the configured path to be silently discarded, targeting the wrong folder. Projects using a non-default working folder should update to get correct path resolution.
