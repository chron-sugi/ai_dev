---
name: create-domain-contract
agent: architect
description: Create one domain CONTRACT.yaml from an ADR and the canonical domain contract template; write no other artifacts.
---

# Create a Domain Contract YAML

Create the domain contract described by one ADR. This prompt is an authoring
step only: it produces the validated YAML contract that a separate scaffolder
may later implement.

## Required input

- `ADR_PATH` — one ADR under `docs/adrs/`
- `CONTRACT_TEMPLATE` — normally `docs/domains/_contract_template.yaml`

Optional input:

- `APPROVAL_ACTOR` — `human` or `agent`
- `APPROVAL_NAME` — the approving author's name or stable agent identifier
- `APPROVED_AT` — an ISO 8601 timestamp with timezone

The three approval values are one unit: accept all three or none of them.

## Sole permitted output

Write exactly one repository artifact:

```text
docs/domains/<domain>/CONTRACT.yaml
```

Derive `<domain>` from the ADR's `domain` frontmatter exactly. It must be
kebab-case and must not be renamed, pluralized, or normalized to a near match.
Create the domain directory when it does not exist. If the destination contract
already exists, stop without changing it unless the invocation explicitly says
to replace it.

Do not create or modify source code, tests, `CONCEPT.md`, ADRs, indexes, schemas,
templates, generated clients, reports, lockfiles, or any other file. Do not run
the scaffolder. Do not implement any declaration in the contract.

## Authoring procedure

1. Read the complete `ADR_PATH`, `CONTRACT_TEMPLATE`, and the JSON Schema named
   by the template's `yaml-language-server` directive.
2. Confirm the ADR frontmatter contains a valid `domain`. Stop without writing
   if it is absent or invalid.
3. Use the template's current `schema_version`, key names, nesting, and value
   vocabulary. The template demonstrates shape; its example values are never
   evidence for this domain.
4. Translate only facts decided by the ADR or supplied explicitly in the
   invocation. Preserve exact names, signatures, paths, dependency edges,
   endpoint IDs, types, invariants, and alternatives when the ADR declares
   them. Do not invent declarations, rejected alternatives, or architectural
   choices to make the contract look complete.
5. Add the source ADR to `adr_provenance` using its declared ADR ID and
   repository-relative path. A rule may cite that ID only when the ADR directly
   establishes the rule.
6. Include `backend`, `frontend`, and `http` only when the ADR explicitly
   activates and completely declares that concern. Absence means omit; never
   infer a component, module, segment, endpoint, persistence surface, or
   dependency edge.
7. Remove every unused optional example block. Remove all template placeholder
   values and comments except the first-line schema directive.
8. Record each fact required for a complete contract but not decided by the ADR
   as a specific `unresolved_gaps` entry. Do not hide missing information in a
   description or choose a default on the author's behalf.

## Lifecycle rules

- An accepted ADR is provenance, not contract approval.
- Without the complete approval input, emit `status: draft`, omit `approval`,
  and retain every unresolved gap.
- With complete approval input, emit `status: approved` only if validation finds
  no unresolved gaps and every activated component is completely declared.
- If approval input is supplied but the contract is incomplete, emit a draft
  without approval metadata. Never fabricate approval or its timestamp.

## Validation and write boundary

Write the candidate only to the sole permitted destination, then validate that
same file through `app.config.validate_domain_contract`. Fix validation errors
only by editing that destination YAML and only when the ADR or invocation
provides the required fact. If validation requires an undecided fact, represent
it as an unresolved gap and keep the contract draft; if the schema cannot
represent that gap without an otherwise required declaration, stop and report
the missing decision without writing an invalid contract.

Before finishing, inspect the working-tree diff and verify that this run changed
only `docs/domains/<domain>/CONTRACT.yaml`. Preserve all pre-existing changes.
Return one concise line containing the contract path, lifecycle status, and
validation result. The response is a handoff, not a second artifact.
