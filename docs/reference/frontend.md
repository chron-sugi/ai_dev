---
type: reference
title: Frontend
scope: frontend
updated: 2026-07-18
---

# Frontend — Reference

Current-state registry of supported frontend tooling, libraries, and conventions. Mutable by design; kept current via PR review. Entries link to an ADR only when the addition was a contested decision. See `docs/adrs/adr-0002-reference-documentation.md` for the document-class rationale.

## Entry template

Copy for new entries:

```markdown
### <Name>

| Field | Value |
|---|---|
| **Configuration** | <what is configured / supported> |
| **What it does** | <mechanical effect in the repo> |
| **Rationale** | <why it was added, one or two sentences> |
| **ADR** | <link to docs/adrs/... or —> |
| **Rule** | `<atomic, projectable rule, or omit row>` |
```
