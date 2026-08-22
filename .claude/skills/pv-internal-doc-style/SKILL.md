---
name: pv-internal-doc-style
description: Shared, project-agnostic procedure defining what content docs.tech.styleBibleDocDir must hold and how to write it — a checklist of style categories (writing/naming, and, only for projects with a presentation layer, visual design, interaction, accessibility, reusable components) plus dense, AI-oriented writing rules (extends pv-internal-doc-technical's fixed-tag/table/code conventions with style-specific guidance). Receives a summary of what's being documented and the context already gathered, and returns which categories apply, what each must record, which are already covered versus pending, and the writing rules to apply — without drafting content, deciding the document's structure, or writing anything itself. Internal use by pv-do.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b11
  uses: []
---

# pv-internal-doc-style

A single, shared procedure defining **what** `docs.tech.styleBibleDocDir` content must cover and **how** to write it. Where `pv-internal-doc-technical` only prescribes writing style (dense fact fragments, tables, code spans, fixed English tags) and leaves topic/structure entirely free, this skill goes one step further specifically for the style bible: it also names the categories of style convention a project typically needs to keep documented, and — for projects with a presentation layer — the good practices particular to that kind of documentation (visual design tokens, interaction states, accessibility, reusable components). Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**This skill writes or edits nothing, nor does it draft any content.** It only states which style categories are relevant to what's being implemented, what each category is expected to record, which of those are already covered by the caller's context versus still pending to document, and the writing rules to apply once the caller drafts the actual prose. Deciding the document's file/section structure, drafting the content, and writing it to disk is always the caller's job (`pv-do`, following `docs.tech.styleBibleDocDir`'s folder convention — `INDEX.md` + numbered files — same as `docs.tech.architectureDocDir`).

**Language.** This skill doesn't talk to the user and doesn't read `.claude/pv-context.json` itself. Category names and guidance returned to the caller are in English, as internal framework vocabulary — the caller translates as needed when drafting into `docs.tech.language`. The fixed English tags this skill's writing rules define (see "Writing rules" below) stay in English regardless of `docs.tech.language`, same convention `pv-internal-doc-technical` already uses.

**Relationship with `pv-internal-doc-technical`.** The two are complementary, not redundant: `pv-internal-doc-technical` is the general writing style shared by both `architectureDocDir` and `styleBibleDocDir` (dense fragments, tables, code spans, no narrative). This skill adds the style-specific layer on top of it, only for `styleBibleDocDir` — a content checklist plus a handful of writing rules unique to style/UI conventions (e.g. always show the token or value, never just describe it). The caller invokes both: `pv-internal-doc-technical` for the shared baseline, this skill for the style-specific checklist and additions.

## Expected input from the caller

- A brief summary of **what's being implemented/documented** (the specific change/fix, not the whole conversation).
- The **context already gathered** so far (touched code, `plan.md`, mockups (`design_*.html`/`.txt`) generated or referenced by this entry, existing `styleBibleDocDir` files for the touched area) — to avoid repeating exploration already done, and to mark a category as already covered when the context makes that clear.
- Whether the project **has a presentation layer** (any UI the end user directly sees/interacts with — web, desktop, mobile, **or a CLI/terminal application**: a CLI's colored output, tables, spinners, progress bars, and interactive prompts are as much a presentation layer as a GUI, just rendered in a terminal instead of a screen, and the categories below apply to it the same way, expressed in that medium's own vocabulary — e.g. "visual design tokens" becomes ANSI color codes/highlight rules, "layout" becomes column widths/wrapping, "accessibility" becomes `NO_COLOR`/plain-output fallback and screen-reader-friendly output). A project only lacks a presentation layer if nothing it ships is ever directly seen or operated by an end user — a library, an internal backend service, a headless daemon. If the caller doesn't know, it can infer it from `sourcecodeDir`'s content (UI frameworks/markup/stylesheets, or a CLI/terminal-formatting dependency) or from whether `design_*` mockups exist anywhere in `{workFolder}/changes/**` — but resolving that is the caller's responsibility, not this skill's; this skill only reacts to what it's told.

## 1. The category checklist

For each category, assess two things: (a) whether it's **applicable** to what's being documented (most changes only touch one or two categories, not all of them) and (b) if applicable, whether the caller's context already makes clear how it's resolved, or whether it's **pending to document**.

The first category always applies to any project; the rest only apply when the caller states the project has a presentation layer — same as `pv-internal-tech-security`, a category not applicable to the change simply isn't mentioned in the result, it isn't forced to fit.

| Category | What to check | Presentation layer only? |
|---|---|---|
| Writing / naming conventions | Does the change introduce or rely on naming rules for identifiers, files, commit messages, user-facing copy tone, terminology/glossary consistency? | No |
| Visual design tokens | Does it introduce or change colors (or ANSI codes/highlight rules in a CLI), spacing scale (or column widths/padding in a CLI), typography (family/size/weight), border radius, shadows, iconography (or glyphs/symbols in a CLI)? | Yes |
| Layout and composition | Does it establish or change grid/breakpoints/responsive behavior (or terminal width handling/wrapping in a CLI), alignment/spacing rules between components? | Yes |
| Interaction patterns | Does it introduce or change how a component responds to user action — hover/focus/active/disabled states (or selected/highlighted/inactive in a CLI menu), loading/empty/error states (spinners, progress bars), transitions/animation, feedback (toasts, inline validation, or exit codes/stderr conventions in a CLI)? | Yes |
| Accessibility | Does it affect color contrast, keyboard navigation/focus order, ARIA roles/labels, screen-reader behavior, motion-reduction handling (or, in a CLI, `NO_COLOR`/`--no-color` support, plain-text fallback when not a TTY, screen-reader-friendly output ordering)? | Yes |
| Reusable components / design system | Does it add a new reusable component or variant, or change an existing one's public API/appearance in a way other screens should follow (or a new reusable output pattern — table format, prompt style — other commands should follow, in a CLI)? | Yes |
| Content and microcopy | Does it introduce or change patterns for labels, button text, error/empty-state messages, tone of voice (or help text, error messages, prompt copy, flag naming conventions, in a CLI)? | Yes |

## 2. Check against the received context

For each category marked applicable in step 1:

- If the caller's context already makes clear how that category is addressed for this change — e.g. it reuses an existing documented token/component, already follows a pattern the style bible already records — don't mark it as pending: flag it as **covered**, in one sentence, citing the specific existing convention that resolves it.
- If the context doesn't make it clear, or the change introduces a new convention with nothing already documented to follow, mark it as **pending to document**, with a sentence on what specifically needs recording (e.g. "new button variant's disabled-state color has no documented token yet").
- Don't over-explore code just to resolve this: if deciding needs more digging than the context already gathered, that itself is a sign the category stays pending — not a reason to launch additional exploration on your own.

## 3. Writing rules

These extend `pv-internal-doc-technical`'s baseline (still invoke that skill too — this doesn't replace it) with rules specific to style/UI documentation:

1. **Always give the concrete value, never just a description.** A color, spacing, or type rule is written as its actual value (`#1A73E8`, `8px`/`0.5rem`, `font-weight: 600`) in a code span or table cell — never as prose like "a shade of blue" or "medium spacing".
2. **One row per token/state/variant, in a table.** Any enumerable set (color tokens, spacing scale, component states, breakpoints) is a table with at minimum `Name | Value | Usage` — never a paragraph listing them in prose. This is `pv-internal-doc-technical`'s table rule made concrete for the shapes this kind of documentation actually has.
3. **State the condition that triggers each interaction/state**, not just its appearance. `hover`, `disabled`, `loading`, `error` etc. as fixed English tags (own convention, same spirit as `pv-internal-doc-technical`'s `[breaking]`/`[async]`), each followed by what changes visually and, if non-obvious, why (e.g. `[disabled]` also drops the element from tab order).
4. **Accessibility facts are stated, never assumed compliant.** If a component/pattern has a contrast ratio, a required ARIA role, or specific keyboard behavior, write the actual figure/attribute/key — "accessible" or "follows a11y best practices" alone is not a fact, it's a claim with nothing to verify against.
5. **Point at the mockup or component source instead of re-describing its look.** If a `design_*.html`/`.txt` or a real component file already shows the exact visual, reference it (`file:component` or the mockup's path) rather than retyping measurements or colors visible there — same "point at the source" principle `pv-internal-doc-technical` applies to code signatures.
6. **Group by category, not by change/fix.** Style documentation is organized by the categories in step 1 (or the finer-grained topics they split into, one numbered file each, same convention as `architectureDocDir`) — never a chronological log of "what change N added"; that history already lives in `changes/closed` and the changelog.

## 4. Return the result to the caller

Don't draft any file nor show anything to the user directly. Return to the caller, in the same turn:

- **Applicable categories covered**: a list (can be empty) of `{category}: {why it's already resolved}`.
- **Categories pending to document**: a list (empty if none) of `{category}: {what needs recording}`.
- **Writing rules** from step 3, for the caller to apply verbatim while drafting (in addition to invoking `pv-internal-doc-technical` for the shared baseline).
- Categories not applicable (including every presentation-layer-only category when the caller said there isn't one) aren't even mentioned in the result.

The caller decides what to do with the pending items (document them now as part of this change, note them for later, or judge that they don't warrant documentation) — this skill doesn't intervene on that again, nor does it check back after the caller writes.
