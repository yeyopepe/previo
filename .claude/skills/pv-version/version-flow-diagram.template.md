# How `/pv-version` works

General diagram of the release-preparation process, with no script or parameter-name detail — meant to be shown as-is if the user asks "how does `/pv-version` work?" during invocation, or as a reference in the project's documentation.

```mermaid
flowchart LR
    Guard{"implemented/\nempty?"}
    Resolve["Resolve each entry\n(user confirms → closed)"]
    Folder["Create versions/XXXX\n(files/, docs/)"]
    Compile["Generate the deliverable\n(how-to-compile-version.md)"]
    Docs["Zip and copy current technical\nand functional documentation to docs/"]
    Changelog["pv-internal-changelog\ndrafts changelog.md from closed/"]
    Confirm["Confirm the release\nto the user"]

    Guard -- No --> Resolve --> Guard
    Guard -- Yes --> Folder --> Compile --> Docs --> Changelog --> Confirm

    classDef guardrail fill:#e03131,color:#fff
    classDef core fill:#2b6cb0,color:#fff
    classDef internal fill:#805ad5,color:#fff
    classDef done fill:#2f9e44,color:#fff
    class Guard,Resolve guardrail
    class Folder,Compile,Docs core
    class Changelog internal
    class Confirm done
```

Legend: red = `implemented/` guardrail (blocks until resolved); blue = `pv-version`'s mechanical steps; purple = delegated to `pv-internal-changelog`; green = end of the process.
