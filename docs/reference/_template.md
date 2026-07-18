---
type: reference
title: AI Dev Environment
scope: framework
updated: 2026-07-18
---

# AI Dev Environment — Reference

Current-state registry of supported tooling and environment configuration. Mutable by design; kept current via PR review. Entries link to an ADR only when the addition was a contested decision. See `docs/adr/adr-00XX-reference-documentation.md` for the document-class rationale.

## Supported editors

### VS Code

| Field | Value |
|---|---|
| **Configuration** | VS Code is the supported editor for this repository. |
| **What it does** | Primary IDE; carries workspace settings, recommended extensions, and Copilot instruction-file integration (`.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`). |
| **Rationale** | Native GitHub Copilot Agent mode support and instruction-file conventions align with the repository's context-injection strategy. |
| **ADR** | — |
| **Rule** | `Assume VS Code as the editor; do not generate editor configuration for other IDEs.` |

## Entry template

Copy for new entries:

```markdown
### <Name>

| Field | Value |
|---|---|
| **Configuration** | <what is configured / supported> |
| **What it does** | <mechanical effect in the repo> |
| **Rationale** | <why it was added, one or two sentences> |
| **ADR** | <link to docs/adr/... or —> |
| **Rule** | `<atomic, projectable rule, or omit row>` |
```