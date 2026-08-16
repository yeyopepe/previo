# `/pv-new todo <code>` mode

Full procedure when the `pv-new` skill is invoked as `/pv-new todo <code>` (or the user explicitly asks to "turn idea `<code>` from todo into a change"). This entry doesn't originate from a new request from the user in chat, but from content already noted by `pv-todo`.

1. Check that `{changesDir}/todo/{code}/description.md` exists **exactly**. If it doesn't exist, tell the user there's no idea with that code in `todo/` and stop there (don't invent or assume a similar code).
2. Read that `description.md` in full (`## Idea`, `## Code` and `## Notes` sections) and, if any, its `design_*.html` files in that same folder. This is the content to analyze and document — use it as if it were the user's request for the rest of the process, instead of waiting for a new description in chat. If the user also added extra context when invoking the skill, add it to the analysis.
3. Ask the user if they want to develop the idea with you before continuing.

```
Do you want us to refine this idea ("<idea name>") before writing it, or should I document the change with the information as it is now?
```

If they confirm, propose ideas and chat with them until the idea is a bit more refined before continuing with point 4. If they don't want to, go to point 4.
4. Continue with the usual process from step 1 of `SKILL.md`'s "Steps" (anticipate doubts, document with `pv-internal-workflow`, visual proposal), using that content as the base. When invoking `pv-internal-workflow` in step 2 of "Steps", use the idea's `## Notes` content as `promptOriginal` (plus any extra context the user added when invoking the skill or during the refinement in point 3 here), so it's kept as history in `history.md`. If there were `design_*.html` in the `todo/` idea, take them into account when building the visual proposal in step 3 (don't just copy them as-is: they're only a starting sketch, not an already-validated mockup).
5. **Only if step 2 of "Steps" finishes successfully** (the entry already exists at `{changesDir}/inProgress/{xxxx}/`), automatically delete the entire `{changesDir}/todo/{code}/` (`description.md` and any `design_*.html` it had), without asking the user for confirmation — deletion is automatic cleanup of an already-migrated source, not a destructive action requiring approval. If step 2 doesn't complete, leave the idea as-is in `todo/`.
6. In step 4 of "Steps" (stating the next step), also mention that `todo/`'s idea `{code}` has been turned into change `{xxxx}` and deleted from `todo/`.
