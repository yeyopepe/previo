# How to compile this project's deliverable

`pv-version`'s own file (not part of `.claude/pv-context.json`): describes this repo's specific shell/build procedure for generating the playable deliverable. Filled in by `pv-version` the first time it's invoked and the file doesn't exist yet, by asking the user; on later invocations it's read and followed as-is, without asking again. Also updated whenever the user reports a change to this procedure.

If the deliverable is generated with a single command, directly describe "Command(s) to run" and "Generated file(s)" as in the example below. If the process consists of **several independent steps that generate distinct artifacts** (all part of the same complete deliverable, e.g. building the game + building a rules PDF), document each one as a separate "Step N: {name}", each with its own "Command(s) to run" and "Generated file(s)" — in that case, all resulting artifacts are copied to `files/`, one per step.

## Command(s) to run

[Exact command or sequence of commands, in the order they need to run, from the repo root. Include the interpreter/tool (e.g. `python`, `npm run`) and any needed flags.]

## Generated file(s)

[Path (or path pattern, if the name includes an auto-incrementing version) where the deliverable ends up after running the command(s) above, and how to identify the most recent one if there are several candidates.]

## Notes

[Any other relevant detail: prerequisites, side effects of the build (files that also get updated), warnings about what NOT to touch manually, etc. Optional section — omit it if there's nothing to note.]
