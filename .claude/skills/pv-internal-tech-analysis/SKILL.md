---
name: pv-internal-tech-analysis
description: Shared, project-agnostic procedure to gather technical context before analyzing a change/fix or assessing whether a change is trivial. First reads the technical documentation configured in framework.docs.tech (architecture, style bible), and only explores the real code if more information is needed. If the topic touches any interface or data structure, requires having its complete definition (signature, input, return, fields) before considering the context gathered, and confirms with the user any definition doubt not resolved by documentation or code. If it detects that code and documentation don't match, flags the code as the source of truth and returns the inconsistency as part of the analysis. When done, checks the change against pv-internal-tech-security's security checklist and adds its pending items to the result. Edits nothing. Internal use by the pv-new, pv-fix and pv-how skills.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b4
  uses: [pv-internal-tech-security]
---

# pv-internal-tech-analysis

A single, shared procedure to obtain reliable technical context before making any decision about a change/fix (designing a solution, assessing root cause, or judging whether a change is trivial enough for `pv-fix`'s `fast` shortcut). Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**This skill writes or edits nothing.** It's purely analysis/reading: it gathers context and, if any, reports inconsistencies between documentation and code to the caller. What to do with those inconsistencies (update the document right away, note it for later, or use it as a reason to rule out a fast path) is always decided by the calling skill, per its own rules. The only exception to not interacting on its own is a specific one (see step 3): if a definition doubt remains that blocks having complete context, it confirms it directly with the user before returning the result.

## Expected input from the caller

The caller must pass a brief summary of **what's being analyzed** (the specific change/fix/doubt, not the whole conversation) — used to scope step 2's code exploration, instead of exploring the entire repo aimlessly.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root (if you haven't already this session). Don't validate here that the framework is initialized — the calling skill has already checked that before invoking this one; if `framework` were missing entirely, just treat all of `docs.tech` as unconfigured and go straight to step 2 with `sourcecodeDir` (or the repo in general) as the sole source.

## 1. Read the existing technical documentation first

Before touching code, look at `framework.docs.tech` in `.claude/pv-context.json`:

- **If you already read a specific file earlier this session** and it hasn't changed since, don't reread it — reuse what you already have in context. This rule applies per individual file, not the whole directory: `architectureDocDir`/`styleBibleDocDir`'s documents are several small files, so in a typical cycle (invoked from `pv-new`/`pv-fix`, then again from `pv-how`) only `INDEX.md` needs rereading the second time, checking whether the already-read sibling files are still the relevant ones — reread only the missing ones, never the whole directory again. This is strictly more efficient than rereading a full monolithic file twice per cycle.
- For each of `architectureDocDir` and `styleBibleDocDir` that's configured **and** really exists as a folder in the repo:
  1. Always read `{dir}/INDEX.md` first (if you don't already have it from this session).
  2. With the summary of what's being analyzed (received as input) and `INDEX.md`'s index table (what each sibling file covers), decide which sibling files are relevant and read only those.
  3. When in reasonable doubt about whether a file is relevant, read it — better to overshoot than fall short.
- Skip the ones not configured, or configured but whose folder doesn't exist yet — it's not an error, that source is simply unavailable.
- If `framework.docs.tech` doesn't exist at all, or neither field is configured, there's nothing to read in this step: go straight to step 2.

Return to the user the list of documents you have in `.claude/pv-context.json` and which you found and which you didn't.

With this, build preliminary context (architecture/layers, style conventions, file and symbol map) before reading a single line of source code.

## 2. Fill in with real code only if needed

If step 1's context already resolves what the caller needs to know, don't explore any more code. If information is missing (no documentation configured, what's there doesn't cover the topic, or the caller needs to confirm a specific implementation detail), explore **only the part of the code relevant to the given topic** — using `framework.sourcecodeDir` as the starting point if configured, or the repo in general if not.

## 3. Completeness of interfaces and data structures

If the analyzed topic involves any **interface** (HTTP endpoint, public function/method, event, message between components, contract between layers) or **data structure** (model, schema, table, DTO, type), the context isn't complete with a generic summary — the exact definition is needed:

- **Interface**: exact path/name, verb or invocation form, every input parameter (name, type, whether required/optional), the complete shape of the output/return (fields and types), and relevant error codes or failure cases if any.
- **Data structure**: all its fields, each one's type, constraints (nullability, keys, defaults) and relation to other structures, to the extent relevant to the analyzed topic.

This is the only exception to step 2's "don't over-explore": if what was read in steps 1-2 leaves a relevant interface or structure half-defined, go back and explore the code (or the documentation, if it has one) specifically until you have the complete definition — an approximate description isn't enough context to design against.

### Doubts neither documentation nor code resolve

If after this a genuine definition doubt remains (e.g. what an ambiguous field represents, what exact format a parameter expects, why an interface has a shape that's neither documented nor evident from the code) that neither `framework.docs.tech` nor the code clarify, don't accept it with a silent assumption: formulate the solution that seems most reasonable to you and confirm it with the user before considering the context gathered. This applies only to specific definition doubts blocking complete context — not to design decisions about the solution itself, which remain the responsibility of whoever invokes this skill.

## 4. Detecting inconsistencies: the code rules

While reading code during step 2, compare what you find against what step 1's documentation said (if any). If something doesn't match (a layer that no longer works as some `architectureDocDir` file describes, or a `styleBibleDocDir` convention the code no longer follows):

- The real code is always the source of truth, never what the document says.
- Don't fix the document yourself here. Add the inconsistency to the result you return to the caller (see below) as a pending documentation change, so that skill decides how and when to apply it (e.g. `pv-how` integrates it into its `plan.md`'s sections (c)/(d), which `pv-do` will apply in its documentation-update step; `pv-new`/`pv-fix` can note it in **Technical notes**; `pv-fix` can take it as a reason not to qualify as trivial for its `fast` shortcut).

## 5. Check against the security checklist

Before returning the result, invoke the `pv-internal-tech-security` skill (Skill tool) passing it the summary of what's being analyzed (the same input received) and the context already gathered in steps 1-4. That skill explores nothing on its own nor decides design: it only checks the change against its security category checklist and returns which ones apply and, of those, which are still pending review.

This step always runs, not only when the analyzed topic "sounds" security-related — apparently unrelated changes (UI, text, configuration) can incidentally touch a checklist category (e.g. a new form that does imply input validation). It's `pv-internal-tech-security` itself that decides which categories apply, not this skill.

## 6. Return the result to the caller

Don't draft any file. Return to the calling skill, in the same turn:

- **Gathered context** — the relevant summary for the given topic, already synthesized (don't paste the entire documents or the raw code), including the complete definition of any relevant interface or data structure from step 3.
- **Detected inconsistencies** — a list (empty if none) with, for each one: which document contains it, what it said, what the code actually shows, and the suggested documentation change.
- **Pending security points** — the "Categories pending review" list returned by `pv-internal-tech-security` in step 5 (empty if none). Don't include here the categories that skill marked as already covered — those need no action from the caller.

The caller decides what to do with each inconsistency and each pending security point (resolve it with the user, note it in `plan.md`, use it as a reason not to qualify as trivial); this skill doesn't intervene on that again.
