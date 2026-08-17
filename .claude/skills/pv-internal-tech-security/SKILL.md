---
name: pv-internal-tech-security
description: Shared, project-agnostic procedure to check a change/fix against a security category checklist (authentication, authorization, input validation/injection, secrets, transport, sensitive data, dependencies, infrastructure, API, logging, client hardening). Receives a summary of what's being analyzed and the context already gathered, and returns only the applicable categories — split between already covered by the context and pending review — without deciding the design or editing anything. Internal use by pv-internal-tech-analysis (when finishing its own analysis) and pv-how (when assessing risk alongside pv-internal-tech-risks).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5-beta1
  uses: []
---

# pv-internal-tech-security

A single, shared procedure to check a change/fix against a security category checklist and flag which ones are relevant and not already resolved by the available context. Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**Language.** This skill writes or edits nothing and doesn't talk to the user, so `language` doesn't apply to it — it always works and returns its category names and explanations in English, as internal framework vocabulary. It's the caller's responsibility to translate them if it dumps them into a document written in another language.

**This skill writes or edits nothing, nor does it design the security solution.** It only states which checklist categories apply to the change and, of those, which remain a pending point for review because they're not already covered by the received context. What to do with those pending items (resolve them now, note them in `plan.md`, ask the user, use them as a reason not to qualify as trivial) is always decided by the caller.

## Expected input from the caller

- A brief summary of **what's being analyzed/changed** (the specific change/fix, not the whole conversation).
- The **context already gathered** so far (e.g. whatever already came out of `pv-internal-tech-analysis`'s steps 1-2, or `plan.md`'s technical solution) — to avoid repeating exploration already done, and to be able to mark a category as resolved if the context already covers it.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root (if you haven't already this session). Don't validate here that the framework is initialized — the calling skill has already checked that before invoking this one.

## 1. The category checklist

For each category, assess two things: (a) whether it's **applicable** to this specific change (not every change touches every category — most changes only touch one or two) and (b) if applicable, whether the received context already makes clear how it's resolved, or whether it's **pending review**.

| Category | What to check |
|---|---|
| Authentication | Does it touch login, session, tokens, session cookies, password recovery, MFA? |
| Authorization | Does it touch access control, roles, resource ownership (IDOR risk), admin endpoints or functions? |
| Input validation / injection | Is there user input that reaches a query (SQL/NoSQL), a system command, a parser (XML/YAML), a template engine, a file path, a deserialization, or a URL requested by the server itself (SSRF)? |
| Secrets and configuration | Are credentials, API keys, tokens added or moved? Does how they're loaded, stored, or rotated change? |
| Communication and transport | Is a network call, internal or external, added or changed? Is it encrypted (TLS) with certificate verification? |
| Sensitive data | Does the change handle PII, credentials, payment or health data? Is it encrypted at rest, masked, or excluded from logs? |
| Dependencies | Is a new third-party library, package, or service added? |
| Infrastructure and deployment | Are permissions touched (IAM, service roles), exposed surface (ports, public endpoints), deployment or container configuration? |
| API | Is an endpoint added or modified? Does it need authentication, CORS control, schema validation, or is it left exposed without protection? |
| Logging and monitoring | Are logs added that could capture sensitive data (secrets, PII)? Does the change affect an event that should be logged for security reasons (failed login, permission change, admin access)? |
| Client hardening | Is HTML or user content rendered without the framework's usual escaping/sanitization? Is a state-changing operation added that needs CSRF protection? Are third-party scripts loaded? |

## 2. Check against the received context

For each category marked applicable in step 1:

- If the context already gathered (technical documentation, explored code, `plan.md`) makes clear how that category is addressed — e.g. it already goes through the project's parameterized ORM, already uses the existing auth middleware, already follows an established sanitization pattern — don't mark it as pending: flag it as **covered**, in one sentence, citing the specific pattern that resolves it.
- If the context doesn't make it clear, or the change introduces something new in that category with no existing pattern to follow, mark it as **pending review**, with a sentence on what needs confirming or deciding.
- Don't over-explore code just to resolve this: if more information is needed than what's already available to decide confidently, that's a sign the category stays pending — not a reason to launch additional exploration of the repo on your own.

## 3. Return the result to the caller

Don't draft any file nor show anything to the user directly. Return to the caller, in the same turn:

- **Applicable categories covered**: a list (can be empty) of `{category}: {why it's already resolved}`.
- **Categories pending review**: a list (empty if none) of `{category}: {what needs confirming or deciding}`.
- Categories not applicable to the change aren't even mentioned in the result.

The caller decides what to do with the pending items (resolve them with the user, note them in `plan.md`, use them as a reason not to qualify as trivial in `pv-fix`'s `fast` shortcut); this skill doesn't intervene on that again.
