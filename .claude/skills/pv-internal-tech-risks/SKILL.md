---
name: pv-internal-tech-risks
description: Shared, project-agnostic procedure to assess the risk of breaking something when implementing the technical solution already written in a change/fix's plan.md. Evaluates 9 factors (shared usage, scope, depth, test coverage, criticality, reversibility, persistent data, security surface, sensitive data) scored 0-10, and returns the factor=value list plus the median. Internal use by the pv-how skill, invoked only once plan.md is already written.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b4
  uses: []
---

# pv-internal-tech-risks

A single, shared procedure to assess the risk of breaking something when implementing an already-designed technical solution. Only invoked by `pv-how`, and only after `plan.md` is written — with the solution already decided is when there's enough information to assess risk, not before. Not meant for direct invocation by the user.

**Language.** This skill writes or edits nothing and doesn't talk to the user, so `language` doesn't apply to it — it always works and returns the 9 factor names in English, as internal framework vocabulary (see step 5). It's `pv-how`'s responsibility to translate them to `changes.language` if it dumps them into `plan.md`'s section (f).

**This skill writes or edits nothing.** It's purely analysis: it evaluates and returns the result to the caller. What to do with that result (what gets written to `plan.md`, how much detail is shown to the user) is always `pv-how`'s decision.

## Expected input from the caller

- The path (or already-read content) of the entry's `plan.md`, with the technical solution already written.
- The path (or already-read content) of that same entry's `description.md`, as functional context.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root (if you haven't already this session). Don't validate here that the framework is initialized — `pv-how` has already checked that before invoking this skill.

## 1. The 9 risk factors

Evaluate each of these 9 factors with an integer value from 0 to 10, using the anchor at 0, the anchor at 10, and the general meaning table in the next section to interpolate intermediate values.

| # | Factor | Guiding question | Anchor 0 | Anchor 10 |
|---|--------|---------------|---------|----------|
| 1 | Shared usage | Who else uses the code being touched? | New code exclusive to this change, nobody else uses it | Core function/module consumed by many different features |
| 2 | Scope | How many distinct spots are touched? | 1 single file, 1 function | Many files scattered across different layers (UI, logic, data...) |
| 3 | Depth of change | Is internal behavior changed, or a contract? | Internal detail not observable from outside | Signature/interface/schema change that others depend on directly |
| 4 | Test coverage | Is there an automatic safety net? | Code well covered by tests that would fail if something breaks | No test at all exercises this code |
| 5 | Flow criticality | How serious is it if this fails? | Secondary or cosmetic functionality | Critical business flow (auth, payments, core data) |
| 6 | Reversibility | How costly is it to undo if it goes wrong? | Reverting the commit is enough, no trace left | Requires undoing a data/state migration in production |
| 7 | Persistent data | Is how data is stored being touched? | No schema or stored data format is touched | Schema/data migration in production |
| 8 | Security surface | Is user input or access control being touched? | No user input or access control involved | Change in authentication, authorization, or input validation |
| 9 | Sensitive data | Is something handled that shouldn't leak? | No credentials, PII, tokens, or secrets involved | The change handles or could expose credentials, PII, tokens, or secrets |

## 2. Risk value meaning table (reference for interpolating and presenting the result)

| Value | Meaning |
|---|---|
| 0 | No risk — fully isolated change, impossible for it to affect anything else |
| 1–2 | Minimal risk — local change, with a safety net (tests) or easily reversible |
| 3–4 | Low risk — touches some shared surface or several spots, but doesn't touch contracts or data |
| 5–6 | Moderate risk — shares code with other parts, partial test coverage, or touches a contract/signature used by others |
| 7–8 | High risk — deep change in heavily shared and/or untested code, in a relevant flow, persistent data, or security |
| 9 | Very high risk — structural change in a critical business flow, hard to revert, untested |
| 10 | Extreme risk — deep, broad change in critical, heavily shared code, untested, not easily reversible, touching data and/or security at once |

## 3. Gather the necessary information

1. Read the entry's `plan.md` (specifically section (b) Technical solution, and (c)/(d) if present) and `description.md`.
2. With that, assess how many of the 9 factors can already be scored with confidence. For the ones you can't (e.g. whether tests cover a specific file, or whether a function is used by other parts of the project), specifically explore the real code using `framework.sourcecodeDir` (if configured, or the repo in general if not) — only as much as needed to confirm that specific factor, without exploring the whole repo aimlessly.

## 4. Score and compute the median

1. Assign an integer value 0-10 to each of the 9 factors.
2. Compute the median of the 9 values (the central value when sorted) — with 9 values it's always an integer, no rounding needed.

## 5. Return the result to the caller

Don't draft any file nor show anything to the user directly. Return to `pv-how`, in the same turn:

- **Factor list**: each of the 9 as `{factor} = {value}`, in the same order as step 1's table.
- **Final median**: the integer value computed in step 4.

The caller decides what to do with this result (what it writes to `plan.md`, what it shows the user); this skill doesn't intervene on that again.
