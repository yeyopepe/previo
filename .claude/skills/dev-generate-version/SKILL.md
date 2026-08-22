---
name: dev-generate-version
description: Cuts a new release of the pv-* framework itself — sets every pv-*/SKILL.md to a single confirmed version, regenerates the framework's own changelog, and tags the current branch. Trigger: /dev-generate-version, or when the user asks to "cut"/"generate"/"release" a new framework version.
argument-hint: "[target version, e.g. 1.0.1b1]"
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.1.0
  uses: [dev-changelog]
---

# dev-generate-version

Cuts a new release of the `pv-*` framework itself (this repo's own versioning — the skills distributed to consuming projects), not to be confused with `pv-version`, which prepares a release of a project *using* the framework. This skill is dev-only: it's never installed into a consuming project.

## 1. Confirm the target version and the previous version to compare against

If the skill was invoked with an argument (`argument-hint`), propose it as the target version; otherwise ask directly. Either way, **confirm it explicitly with `AskUserQuestion`** before changing anything — e.g. `1.0.1b1`. Don't infer it from the highest existing git tag or from any `SKILL.md`'s current version; the user decides the target.

While confirming, check `git tag --list` for a tag already matching that exact name — if one exists, tell the user and ask for a different version instead of proceeding (a tag is never overwritten silently).

In the same round, also confirm the **previous version** to diff against for the changelog (step 3) — the base ref `dev-changelog` needs. Propose the current highest existing tag (`git tag --list`, sorted) as the likely candidate, but always ask; don't assume the highest tag is the right base without the user's confirmation (e.g. they may want to compare against an older tag if intermediate ones were never actually released). Keep both confirmed values (target version, previous version) for the rest of this flow.

## 2. Set every skill's version

Run from the repo root, passing the confirmed version:

```
python tools/set-skill-versions.py <version>
```

It rewrites the `metadata.version` frontmatter field in every `.claude/skills/pv-*/SKILL.md` to `<version>` and prints which files it changed (and which it skipped for having no `version:` field — that would be unexpected here, flag it to the user if it happens instead of ignoring it). Don't hand-edit any `SKILL.md` yourself for this — the script is the single source of truth for this mechanical rewrite.

## 3. Generate the changelog

Invoke `dev-changelog` (Skill tool), passing it the previous version confirmed in step 1 as its base ref (a tag name is a valid base ref for that skill's step 2). It will still resolve/confirm the current version (`XXX`) itself by reading the just-updated `SKILL.md` frontmatter from step 2 — that's expected and fine to let it re-confirm, since it doesn't know it was this skill that just set it. What it must **not** do is ask the user again for the previous version/base ref: since it was already confirmed in step 1, provide it directly so `dev-changelog` treats it as already resolved instead of asking a second time.

## 4. Tag the current branch

Once the changelog files are written, create a git tag named exactly the target version (no `v` prefix, matching the existing tag convention in this repo, e.g. `1.0.1b1`) pointing at the current branch's `HEAD`:

```
git tag <version>
```

Don't push the tag — that's a separate, explicit action the user takes themselves when ready. Confirm the tag was created by listing it (`git tag --list <version>`) before reporting success.

## 5. Confirm to the user

Tell the user the version is ready: the version now set across every `pv-*/SKILL.md`, the changelog files written, and the tag created (name and that it points at the current `HEAD`, not pushed). Remind them the tag still needs an explicit `git push --tags` (or `git push origin <version>`) whenever they want it published, since this skill never pushes on its own.
