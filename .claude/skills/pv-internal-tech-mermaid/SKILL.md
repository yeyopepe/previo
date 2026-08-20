---
name: pv-internal-tech-mermaid
description: Shared, project-agnostic procedure to generate Mermaid diagrams (functional or technical — flow, sequence) representing a use case, user story, workflow, or communication between components. Receives the list of diagrams to generate (type, what each should represent) and returns each one's Mermaid code, without deciding on its own which diagrams are needed or where they're inserted. Internal use by the pv-internal-workflow, pv-new, pv-fix and pv-how skills, invoked by the name configured in `.claude/pv-context.json`'s `framework.skills.diagrams` (by default, this same skill).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.5b10
  uses: []
---

# pv-internal-tech-mermaid

A single, shared procedure to generate Mermaid diagrams representing a change/fix's behavior — never its visual look (that's `design_*.html`, another skill) nor navigation between UI screens (that's `design_navigation_*.md`, which `pv-new` writes directly). Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**Language.** This skill doesn't talk to the user. The diagram code itself (node/actor labels, message text) follows the target language the caller passes it as input (see "Expected input" below) — this skill doesn't read `.claude/pv-context.json` itself, since it doesn't know which final document each diagram will be inserted into; each caller (`pv-internal-workflow`, `pv-new`, `pv-fix`, `pv-how`) must resolve the right `language` (`changes.language` or `docs.tech.language`, depending on the destination document) before invoking this skill.

**This skill doesn't decide which diagrams are needed, nor whether a diagram is the right tool versus prose, nor where the result is inserted.** That's always decided by the caller: this skill is only invoked once it's already known that at least one Mermaid diagram needs generating, never "just in case". Presenting the result to the user for confirmation is also the caller's responsibility.

If a project configures another skill in `framework.skills.diagrams` to generate diagrams a different way (another notation, an external tool), that alternative skill must fulfill the same input/output contract described here so it can replace this one without `pv-internal-workflow`/`pv-new`/`pv-fix`/`pv-how` needing to change anything.

## Expected input from the caller

A list of diagrams to generate. For each one:

- **Type**: one of the three defined in "General rules" below — `functional`, `technical-flow` or `technical-sequence`.
- **What it should represent**: the specific use case/user story (if `functional`) or the specific flow/communication (if technical) — steps, decisions, edge cases, or the actors/components involved and what they exchange, as applicable.
- **Supporting context** the caller already has (e.g. real component/module names if `technical-sequence`, or the project's domain vocabulary) so the diagram uses precise terminology instead of generic.

## General rules (Mermaid-agnostic)

These rules govern **what** to represent and **how to split** the diagrams, regardless of the syntax used to draw them.

### Functional diagrams

- Represent the user's direct experience: what they do, what they decide, what they see as a result — never how the system solves it internally (no component names, functions, data structures, network calls, etc.).
- **One diagram per use case or user story, never fewer.** Don't mix two different cases or stories in the same diagram, even if they share steps — if they share steps, each diagram repeats them from its own entry point. If the caller asks to represent several cases/stories, generate an independent diagram for each.
- If a use case has no branches or decisions (it's a single-path linear sequence, no alternatives), it still deserves a diagram: don't discard it for being "too simple" — that decision (whether the diagram adds value over a sentence) belongs to the caller, not this skill.

### Technical diagrams

- **Flow diagram** (workflow): to represent an internal process with steps and decisions — the order something happens in, conditions that branch the path, chained edge cases. A single actor/execution thread moving through steps.
- **Sequence diagram**: to represent communication between components — what messages/calls are exchanged, in what order, between which actors or parts (user↔system, client↔server, module↔module). Use it as soon as there are two or more parts exchanging information, not just one component's internal flow.
- If what needs representing has both dimensions (a flow with steps/decisions that also involves communication between components at some point), generate the two diagrams separately instead of forcing one to cover both — each reads better focused on its own dimension.
- Unlike functional ones, a single technical diagram covering several related steps of the same change can make sense, if the caller explicitly asks for it as a single unit — this skill doesn't impose that, but doesn't split it on its own either if asked to keep it together.

## Mermaid-specific rules

These are the Mermaid syntax/notation rules themselves, kept separate from the general rules above so a project can swap this skill for another notation without losing the general rules (which live in `pv-internal-workflow`/`pv-new`/`pv-fix`/`pv-how`, not here).

### Choosing the Mermaid diagram type

- **Functional** → `flowchart` (`TD` top-to-bottom unless `LR` is more readable given the number of steps). Functional diagrams represent a user moving through steps and decisions, which is exactly what a flowchart expresses. Don't use `sequenceDiagram` for a functional diagram: it implies technical actors/components exchanging messages, which is exactly what a functional diagram must not show.
- **Technical flow** → `flowchart` (`TD` or `LR` depending on readability).
- **Technical sequence** → `sequenceDiagram`.
- If what needs representing is explicitly a state machine (a component/entity with named states and transitions between them, rather than a sequence of steps), `stateDiagram-v2` is a valid alternative to `flowchart` for both functional and technical — only use it when the "named state" concept is real in the domain, not as a synonym for flowchart.

### `flowchart` syntax

```
flowchart TD
    A[Step or action] --> B{Decision?}
    B -->|Yes| C[Result A]
    B -->|No| D[Result B]
    C --> E[End]
    D --> E
```

- Nodes: `[Text]` rectangle (step/action), `{Text}` diamond (decision), `(Text)` oval (start/end), `((Text))` circle (one-off event) — use whichever best semantically describes the node, not just the default rectangle.
- Arrows: `-->` for the normal transition; `-->|text|` to label a decision's condition or outcome. Every output from a `{Decision}` node must carry a label reflecting which one it is (`Yes`/`No`, or the specific case) — a decision without its branches' labels isn't understandable.
- Group related steps with `subgraph Name ... end` only if the diagram has clearly distinct phases and grouping helps readability — don't use it by default in short flows.
- Node labels in the domain/user vocabulary (functional) or the system's (technical) given by the caller — never generic ones like "Step 1", "Step 2".
- If a label needs quotes, parentheses, or other characters Mermaid might interpret as syntax, wrap it in double quotes: `A["Text with (parentheses)"]`.

### `sequenceDiagram` syntax

```
sequenceDiagram
    actor User
    participant Frontend
    participant Backend

    User->>Frontend: Specific action
    Frontend->>Backend: Specific request
    Backend-->>Frontend: Response
    Frontend-->>User: Visible result

    alt Condition
        Frontend->>Backend: Alternative path
    else Other condition
        Frontend->>User: Notice
    end
```

- `actor Name` for human people/roles, `participant Name` for components/systems — declare only the ones actually involved, in the order convenient to read them (usually from "most external/user" to "most internal").
- Arrows: `->>` synchronous message/call, `-->>` response or return, `-)` asynchronous message (fire-and-forget, no response expected). Always use the one that correctly describes whether the sender expects a response or not.
- `alt/else/end` for conditional branches within the sequence, `loop ... end` for repetition, `Note over A,B: text` for a one-off clarification that isn't a message itself.
- Every arrow carries a brief, specific label (what's requested or what's returned) — never an unlabeled arrow.

### `stateDiagram-v2` syntax (only when applicable, see above)

```
stateDiagram-v2
    [*] --> State1
    State1 --> State2 : event/condition
    State2 --> [*]
```

- `[*]` represents the entry/exit point (not a real state). Every transition carries `: text` with the event or condition that triggers it.

### Hygiene rules common to all three types

- The diagram always goes in a code block with `mermaid` language (` ```mermaid ` ... ` ``` `), never as loose text.
- Don't mix two diagram types (e.g. `flowchart` nodes inside a `sequenceDiagram`) in the same block.
- Short, specific labels — if an idea needs a long sentence to be clear, that's a sign that nuance belongs in a prose note next to the diagram, not inside a label.
- No need to force the same diagram to explain absolutely everything: whatever isn't clear from the diagram itself, the caller can add as a brief prose note next to it — this skill doesn't write those notes, only the diagram.

## Steps

1. For each diagram in the received list, choose the Mermaid diagram type per "Choosing the Mermaid diagram type" and draft it following the general and syntax rules above.
2. Return to the caller, in the same turn, one ```mermaid``` block per requested diagram (in the same order they were requested). Don't present anything to the user or ask for confirmation, nor write the result to any file — that's the caller's job.
