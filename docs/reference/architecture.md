---
type: reference
title: Architecture
scope: architecture
updated: 2026-07-21
---

# Architecture — Reference

Current-state registry of architectural configuration: structural adrs, layering rules, and cross-cutting conventions in effect now. Mutable by design; kept current via PR review. Entries link to an ADR only when the addition was a contested decision. See `docs/adrs/adr-0002-reference-documentation.md` for the document-class rationale.

## Naming

### Application name — velocai

| Field | Value |
|---|---|
| **Configuration** | The application is named `velocai`. |
| **What it does** | Canonical name for package/module identifiers (Python packages, npm packages, top-level namespaces), product branding in docs and UI strings, and repo/infra identifiers (config keys, service names, URLs, environment prefixes). |
| **Rationale** | Registered so scaffolding and generation use the real name; without a canonical entry, agents invent placeholders (`myapp`, `app`) that propagate into package names and configs and are expensive to rename later. |
| **ADR** | — |
| **Rule** | `Use velocai as the application name in all package, branding, and infrastructure identifiers; never scaffold with a placeholder name.` |

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
