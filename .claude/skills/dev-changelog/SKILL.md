---
name: dev-changelog
description: Compares the framework's distributed content (.claude/skills/pv-* and .claude/pv-doc/pv-guide*) between a base commit and the current state, and writes .claude/pv-changelog.en.md with New/Changed/Deleted sections. Trigger: /dev-changelog, or when the user asks to generate/update the framework's changelog.
argument-hint: "[base commit or ref]"
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.1.0
  uses: []
---

# dev-changelog

Generates `.claude/pv-changelog.en.md`: a changelog of the `pv-*` framework as it's actually distributed to projects — `.claude/skills/pv-*/**` and `.claude/pv-doc/pv-guide*` only. Nothing else in the repo (dev-only skills like `dev-onescript`, `pv-doc` design docs other than `pv-guide*`, tests, this very skill) is in scope: those aren't shipped to consuming projects, so they don't belong in a changelog aimed at the framework's users.

`.claude/pv-changelog.en.md` is itself distributed content — `install.sh`/`install.ps1` copy it into consuming projects alongside `pv-guide*`, the same way `pv-internal-changelog`'s output isn't. Keep it a single English file (no `.es.md` twin): the changelog documents the framework's own releases for whoever maintains/updates an installation, independent of `interaction.language`.

## 1. Resolve the current version (`XXX`)

Read the `metadata.version` frontmatter field from every `.claude/skills/pv-*/SKILL.md` (all of them, including `pv-internal-*`). They're expected to share a single version across the whole framework.

- If they all agree, that value is `XXX`. **Still confirm it explicitly with the user** before continuing ("current version is `{value}`, correct?") — don't assume silence means yes, wait for their reply.
- If they disagree, tell the user which skills report which versions and ask them directly which one is `XXX` — don't guess or take a majority vote.

## 2. Resolve the previous version (`YYY`) and the base commit

Always ask the user — never infer it from `git log`, tags, or file history. Two things are needed and both must come from the user:

- **`YYY`**: the previous version number to show in the title.
- **The base commit**: the git ref to diff from (a commit hash, tag, or branch). If the user invoked this skill with an argument (`argument-hint`), treat it as the proposed base commit and still confirm `YYY` with them; otherwise ask for both together.

Don't proceed past this step without an explicit answer for both.

## 3. Diff the distributed content only

Run from the repo root:

```
git diff --stat <base-commit>..HEAD -- .claude/skills/pv-* .claude/pv-doc/pv-guide*
```

to get an overview, then the full diff for content analysis:

```
git diff <base-commit>..HEAD -- .claude/skills/pv-* .claude/pv-doc/pv-guide*
```

If the diff is empty, tell the user nothing changed in the distributed framework content between `<base-commit>` and `HEAD` and stop here — don't write an empty changelog file.

Also check for renames/deletions explicitly, since `git diff` can obscure a whole-skill removal among many line-level hunks:

```
git diff --summary <base-commit>..HEAD -- .claude/skills/pv-* .claude/pv-doc/pv-guide*
```

## 4. Classify by reading the actual diff content

Base every entry on what the diff shows — not on commit messages (commit history for this range may be unrelated squashes or WIP messages and isn't a reliable functional description). For each distinct piece of functionality that changed (typically one skill, or one clearly separable capability within a skill):

- **New** — a new `pv-*` skill directory appears, or a new capability/step is added inside an existing skill that didn't exist in the base commit.
- **Changed** — an existing skill's behavior, flow, or documented capability is modified (including `pv-guide*` content describing existing functionality differently).
- **Deleted** — a `pv-*` skill directory is removed, or a capability/step present at the base commit is removed.

**Informational focus: functional changes only, by default.** Write from a functional perspective (what the framework now does differently for someone using/interacting with it), not a technical one — no file paths, function names, script internals, or line-level detail. One or two sentences per entry, changelog tone, past tense.

**Exception — technical/structural changes that need user action.** Only include a technical-level entry when the diff shows one of these, since consuming projects need to act on it when updating:

- An **architecture** change to how the framework itself is built or wired (e.g. a skill's invocation contract changes, a new required config field appears in `pv-context.json`'s schema, an internal skill's calling convention changes).
- A **folder structure** change in what the framework distributes (e.g. `workFolder`'s expected subfolder layout changes, a skill moves/is renamed, `pv-guide*`'s own location changes).

For these, state plainly what changed structurally and what action the user must take when updating (e.g. "re-run `pv-init-update`", "move `X` to `Y` manually"). Skip this exception entirely if nothing in the diff rises to this level — most changes won't, and the changelog should stay functional by default. Don't invoke `pv-internal-changelog` or read `{workFolder}/changes/`; this skill's classification is independent, based only on the real git diff from step 3.

## 5. Write the file

Write `.claude/pv-changelog.en.md` following [`dev-changelog.template.md`](dev-changelog.template.md): title line `"Previo v{XXX}" changelog (previous version v{YYY})`, then the **New**, **Changed**, **Deleted** sections in that order. Omit an entire section if it has no entries — don't leave the heading with nothing under it. If the file already exists, overwrite it (this skill always regenerates the full comparison from scratch, it doesn't append).

## 6. Confirm to the user

State the path written (`.claude/pv-changelog.en.md`), the base commit used, and how many entries landed in each section (New/Changed/Deleted).
