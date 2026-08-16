- **Creation date**: [YYYY-MM-DD]
- **Risk**: [median 0-10 returned by pv-internal-tech-risks] — [description of the "Meaning" matching that median per the table in section (f)]

## (a) Functional notes

**Out of scope:** [what's explicitly left out of this solution — if it's a fix, what additional improvements were spotted but not included. If there's nothing to exclude, say so explicitly ("no other behavior is touched") instead of omitting the field.]

**Doubts resolved with the user:** [question and answer, briefly. If there were none, say so explicitly ("no open questions...") instead of omitting the field.]

## (b) Technical solution

- [ ] **`[file]` — [brief summary of the task].** [Exactly what needs to be touched (function, variable, CSS rule...), where, and why — with enough detail to implement without having to make any more design decisions. If a snippet or exact value is needed (a CSS rule, a class name, a condition), include it literally instead of describing it in prose.]
- [ ] **`[file]` — [brief summary of the next task].** [...]
- [ ] [...]

Order the tasks in the order they should be implemented. Don't include manual verification/checking steps here — those go in (e). Checklist format (`- [ ]`) is mandatory: whoever implements should check each box `[x]` only when that specific task is done, never all at once at the end.

## (c) Architecture changes

*Only if `docs.tech.architectureDocDir` is configured and this solution modifies the project's core architecture.* [Which specific file(s) in that folder need updating and what to change in each. Omit the entire section if it doesn't apply.]

## (d) Style changes

*Only if `docs.tech.styleBibleDocDir` is configured and this solution modifies or extends the project's visual style.* [Which specific file(s) in that folder need updating and what to change in each. Omit the entire section if it doesn't apply.]

## (e) Verification

- [ ] [An observable result from the already-changed system — not one more implementation step. Write it self-contained (what to do and what you should see), without referring back to a task number from (b): the same check may depend on several tasks at once, or a task may have no check of its own and only contribute to a shared one. The list is gone through in full *after* finishing all of section (b), as a closing checklist.]
- [ ] [...]

Always include this section (unless the solution has no observable behavior to check, which is rare) — it's what lets the implementation be considered done with confidence, even by whoever runs it with no more context than this document. Checklist format (`- [ ]`) is mandatory, same as in (b).

## (f) Risk analysis

*Only if the user asked for the risk detail — by default this section is omitted and only the header's **Risk** field remains.* List of the 9 factors evaluated by `pv-internal-tech-risks` with their 0-10 value, and the final median.

| Factor | Value |
|---|---|
| Shared usage | [0-10] |
| Scope | [0-10] |
| Depth of change | [0-10] |
| Test coverage | [0-10] |
| Flow criticality | [0-10] |
| Reversibility | [0-10] |
| Persistent data | [0-10] |
| Security surface | [0-10] |
| Sensitive data | [0-10] |

**Median**: [0-10]

| Value | Meaning |
|---|---|
| 0 | No risk — fully isolated change, impossible for it to affect anything else |
| 1–2 | Minimal risk — local change, with a safety net (tests) or easily reversible |
| 3–4 | Low risk — touches some shared surface or several spots, but doesn't touch contracts or data |
| 5–6 | Moderate risk — shares code with other parts, partial test coverage, or touches a contract/signature used by others |
| 7–8 | High risk — deep change in heavily shared and/or untested code, in a relevant flow, persistent data, or security |
| 9 | Very high risk — structural change in a critical business flow, hard to revert, untested |
| 10 | Extreme risk — deep, broad change in critical, heavily shared code, untested, not easily reversible, touching data and/or security at once |
