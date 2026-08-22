---
name: pv-internal-doc-technical
description: Shared, project-agnostic writing style for docs.tech.architectureDocDir and docs.tech.styleBibleDocDir. Not a template — each document's topic and structure stay free, but how it's written is fixed: dense fact fragments meant for an AI reader (pv-internal-tech-analysis, pv-do, pv-how in later cycles), not prose meant for a human. Internal use by pv-do when it drafts or edits docs.tech content.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b11
  uses: []
---

# pv-internal-doc-technical

A shared ruleset for **how** to write `docs.tech.architectureDocDir`/`styleBibleDocDir` content — not a template. Architecture and style topics vary too much in shape to force into one structure (unlike `pv-internal-doc-features`'s fixed fields), so this skill doesn't prescribe sections or headings. It prescribes a writing style, applied regardless of topic or configured `docs.tech.language`.

**This skill writes nothing itself and takes no parameters.** Invoke it (Skill tool) right before drafting or editing `docs.tech` content, to load these rules into context; the caller (`pv-do`) still drafts and edits the file directly, applying the rules below instead of its default writing style.

**Language.** This skill doesn't decide or write the document's language — it only prescribes writing style, applied on top of whatever `docs.tech.language` the caller (`pv-do`) has already resolved (default `interaction.language`). Only the fixed English tags in rule 6 stay in English regardless of that language.

## Audience: these documents are for me, not for a human

`docs.tech` exists to be read by `pv-internal-tech-analysis` and, from there, by `pv-do`/`pv-how` in future cycles — not by a person browsing the repo. That changes what "clear" means: dense and fact-first beats narrative and explanatory. Every sentence that could be a fragment, and every fragment that could be a table row, is wasted context.

## Writing rules

1. **One fact per line, no connective narrative.** Cut framing phrases ("this allows...", "in order to...", "it's worth noting that..."). State the fact directly.
2. **Signatures, types and values as code, never described in prose.** `funcName(param: type) -> type` in a fenced or inline code span — not "the function receives a parameter and returns...".
3. **Tables for parallel structures.** Any list of items sharing the same shape (fields, endpoints, states, layers) goes in a table, not repeated paragraphs — a table strips the connective tissue and its columns scan faster than sentences.
4. **Don't restate what a signature or name already says.** Reserve prose for what code doesn't show: invariants, side effects, rationale, edge cases, non-obvious decisions.
5. **Point at the source instead of duplicating its shape.** Reference `file:symbol` for exact structure. `pv-internal-tech-analysis` already falls back to the real code when a doc under-specifies something, so retyping a full class/schema here is redundant, not safer — and it's one more copy that can drift from the code.
6. **Fixed English tags for recurring properties, regardless of `docs.tech.language`.** `[breaking]`, `[async]`, `[idempotent]`, `[deprecated]`, etc. as literal prefixes: a closed, consistent vocabulary to pattern-match, instead of a sentence to re-parse every time — and immune to phrasing drift across edits or languages. Same convention `pv-internal-doc-features` already uses for its structural field labels (`**Area**`, `**Since**`...), which also stay English regardless of the doc's language.
7. **No introductions, summaries, or conclusions.** Skip "this document describes...", "in summary...". Start at the first fact, end at the last.
8. **Flat lists over nested paragraphs.** Prefer `-`/table structure over paragraph indentation — structure is cheap to parse, prose is not.

## Language-independence

These rules must hold no matter what `docs.tech.language` resolves to, so anything whose compression relies on a specific language's grammar was deliberately left out:

- **No telegraphic/headline compression** (dropping articles, prepositions, or verbs to shorten a sentence). That's an English-specific technique — English tolerates a headline like "user token expired"; the equivalent grammatical dropping in other languages (e.g. Spanish) produces broken or ambiguous text, not a compressed one. Compress by **removing whole sentences that add no fact**, never by mutilating the grammar of the ones you keep — rule 1 achieves the same context reduction without this risk.
- **No compound-noun stacking** ("user auth token expiry check") to save words. It's a valid English construction but doesn't shorten equivalently in languages that need prepositions for the same relationship, so it isn't a reliable density technique across `docs.tech.language` values. Use rule 2 (code/signatures) or rule 3 (tables) instead when a relationship needs to be dense.
- Everything else above (fragments over narrative, code over prose, tables, omission of the obvious, pointing at source, fixed English tags, no framing text, flat structure) is structural rather than grammatical, so it transfers unchanged to any `docs.tech.language`.
