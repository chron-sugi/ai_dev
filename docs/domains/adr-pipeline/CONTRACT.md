# Contract — adr-pipeline

Current-state registry of this domain's contract. Each entry cites the ADR
that granted it; this file is never the write path for a new grant.

## Rule surface

- Durable rules enter the repo only as individual ADRs in `docs/adrs/`; no
  CONSTITUTION.md or equivalent monolithic rules file exists —
  [ADR-0004](../../adrs/adr-0004-no-constitution-file.md)
- ADRs remain the permanent source of truth after projection; compiled
  output never justifies deleting or condensing a source record —
  [ADR-0005](../../adrs/adr-0005-adrs-are-the-source-of-truth-after-projection.md)

## Projection outputs

- Agent-facing rule surfaces (`.github/copilot-instructions.md`,
  `.github/instructions/**`, `.claude/rules/**`) are compiled by
  `scripts/project-adrs`; generated regions are sentinel-marked and never
  hand-edited; only files bearing the generated notice may be auto-deleted —
  [ADR-0006](../../adrs/adr-0006-generated-surfaces-are-never-hand-edited.md)
- Rules cluster into one `<domain>.instructions.md` per declared frontmatter
  `domain`; the file's `applyTo` is the union of member ADR scopes;
  traceability is per projected line via ADR-ID citation —
  [ADR-0007](../../adrs/adr-0007-domain-clustered-projection.md)

## Entry points

- Every pipeline operation (lint, projection, drift check, status
  transitions) runs only through justfile recipes; CI invokes the same
  recipes (`just project-check` and peers) that local runs use —
  [ADR-0008](../../adrs/adr-0008-justfile-is-the-single-pipeline-definition.md)
- PowerShell recipes invoke
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File` so user profile
  state cannot alter pipeline behavior —
  [ADR-0008](../../adrs/adr-0008-justfile-is-the-single-pipeline-definition.md)
