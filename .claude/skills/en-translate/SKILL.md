---
name: en-translate
description: Editorial review and English translation of any technical or end-user-facing text (documentation, user manuals, UI copy, error messages, contextual help, README, release notes...). If the text is already in English, does an editorial review pass (clarity, tone, grammar, consistent terminology); if it's in another language, translates it into English under those same criteria instead of translating literally. Preserves code, markup, variables/placeholders, and document structure. Trigger: /en-translate, or whenever the user asks to translate or review a technical or user-facing text in English.
argument-hint: <text to translate/review, or path to a file>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5-beta1
  uses: []
---

# en-translate

Translates into English, or gives an editorial review in English, of any technical or end-user-facing text, always prioritizing a result that's **clear, natural, and readable** for whoever reads it — never a literal word-for-word translation or stilted English. This is a standalone skill, invoked directly by the user; it doesn't depend on the `pv-*` framework or on `.claude/pv-context.json`.

It covers both **documentation/long-form text** (manuals, guides, README, changelogs) and **UI microcopy** (labels, buttons, error messages, tooltips, notifications) — the quality bar is the same for both, but space constraints and tone differ: microcopy must be as short as possible without losing clarity.

## 1. Determine the input and the source language

- If the user passed the text directly in the prompt, work on that text.
- If they passed a file path, read it with the `Read` tool. For a large file or one with many independent sections (e.g., documentation with several chapters), you can process it section by section, but keep terminology consistent across all of them.
- Detect the source language. If it's already in English, the task is an **editorial review** (step 3). If it's in any other language, the task is a **translation** (step 3), applying the same quality criteria as the review — not a mechanical conversion.
- If the text mixes fragments that shouldn't be touched (code, command names, file paths, product proper nouns) with prose that should, tell them apart before you start (see step 4).

## 2. Understand the audience and the register

Before translating/reviewing, identify the type of text so you can calibrate the register:

| Text type | Register |
|---|---|
| Technical documentation (architecture, API, developer guides) | Precise, direct, consistent technical terminology. Assumes a technically knowledgeable reader. |
| User manual / help / onboarding | Plain, no unnecessary jargon, task-oriented for what the user is trying to accomplish. Assumes a non-technical reader. |
| UI microcopy (buttons, labels, tooltips, error/success messages) | Very short, imperative or nominal depending on the element, unambiguous, fits the available space. |
| Communications (changelog, release notes, emails) | Clear and direct, approachable but professional tone, no filler. |

If the category isn't obvious, ask the user before assuming it — the register changes the result quite a bit.

## 3. Translate or review

Always apply these criteria, whether you're translating or reviewing text that's already in English:

- **Naturalness over literalness.** If a literal translation reads forced or unnatural in English, rewrite the whole sentence instead of translating word by word. The result should read as if it had been originally written in English, not like a translation.
- **Short, direct sentences.** Prefer simple sentences over chained subordinate clauses. Split long sentences into several if it improves readability.
- **Active voice and imperative mood.** Use active voice by default. For instructions to the user, use the second-person imperative ("Select the file", not "The file should be selected" or "You should select the file").
- **Consistent terminology.** Use the same English term for the same concept throughout the whole text — don't vary it for stylistic variety. If the text belongs to a product with established terminology (function names, button labels, domain concepts), keep it; if you don't know it, ask before inventing a translation for a key term that recurs.
- **No unnecessary jargon or Latinisms.** Avoid "utilize" (use "use"), "in order to" (use "to"), "leverage" (use "use"/"take advantage of" only if it adds real nuance), and in general any fancier word when a plainer, clearer one exists.
- **Standard technical-English conventions** (Microsoft/Google style): "Select", not "Click on"; avoid semicolons in microcopy; use "can't"/"don't" for an approachable tone or "cannot"/"do not" for a formal one, but stay consistent throughout the text; spell out numbers 0-9 except in UI (where digits are used); Oxford comma in lists of three or more items.
- **Tone matching the register from step 2.** A user manual shouldn't sound like API documentation, and vice versa.
- **No ambiguity.** If the source text is ambiguous (e.g., a pronoun with no clear referent, an instruction that could be read two ways), don't carry the ambiguity over as-is: resolve it with the most likely meaning and flag it as a note when delivering the result (step 5), or ask if the text is short and the ambiguity is critical.

## 4. Preserve what shouldn't be translated

Don't translate or alter:

- Code blocks, variable names, commands, file paths, configuration values.
- Interpolation placeholders (`{name}`, `%s`, `{{var}}`, etc.) — keep them exactly as they are and in the same relative position if English grammar allows it; if the natural English word order forces the placeholder to move within the sentence, move it, but verify it's still syntactically valid in its new context.
- Product/brand proper nouns, or terms the user explicitly says should stay unchanged.
- Markup (Markdown, HTML, JSX, etc.): keep the same heading, list, link, and emphasis structure as the original, translating only the visible text.

## 5. Deliver the result

- If the input was text pasted directly in the prompt, deliver the result in the same turn, ready to copy.
- If the input was a file, ask the user whether they want you to edit the file directly (or create a new file, if it's a translation meant to live alongside the original in another language) or receive the result in chat — don't assume which one they want.
- If you had to resolve any ambiguity in the source, or made a non-obvious terminology call (e.g., a domain term with no single established translation), list them briefly at the end under **Translation notes** — don't mix them into the delivered text itself.
</content>
