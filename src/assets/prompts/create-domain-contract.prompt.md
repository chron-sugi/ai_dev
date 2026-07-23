---
name: create-domain-contract
agent: architect
description: Establish a domain's CONTRACT.yaml from a proposed ADR — drafted in the task workspace, graduated to docs/domains/<domain>/ on approval.
---

# Create a Domain Contract YAML

Create the domain contract described by one ADR. This is the pipeline step
that runs **after an ADR is proposed** (via `/write-adr`, typically following
an `/explore` escalation): it turns the ADR's declarations into the validated
YAML contract that a separate scaffolder may later implement.

## Where this fits

```
/explore → /write-adr (ADR proposed) → /create-domain-contract → approval → scaffold
```

A **proposed** ADR is a sufficient authoring source — per ADR-0017, the
contract's own validation and approval state gate scaffolding, not ADR
acceptance. Per ADR-0018, the contract is drafted in the task workspace and
moves to its durable home only once approved.

## Required input

- `TASK_ID` — the active task's workspace id (descriptive kebab-case,
  ADR-0018); the draft is written to `.velocai/tasks/<TASK_ID>/`
- `ADR_PATH` — one ADR under `docs/adrs/`
- `CONTRACT_TEMPLATE` — normally `.velocai/templates/CONTRACT.yaml`

Optional input:

- `APPROVAL_ACTOR` — `human` or `agent`
- `APPROVAL_NAME` — the approving author's name or stable agent identifier
- `APPROVED_AT` — an ISO 8601 timestamp with timezone

The three approval values are one unit: accept all three or none of them.

## Permitted output

The lifecycle state decides the single destination:

```text
draft     → .velocai/tasks/<TASK_ID>/CONTRACT.yaml
approved  → docs/domains/<domain>/CONTRACT.yaml   (graduation, ADR-0018)
```

- **Without complete approval input** (the normal case for this step): write
  only the workspace draft. Do not create anything under `docs/domains/`.
- **With complete approval input and zero unresolved gaps**: write the
  contract to `docs/domains/<domain>/CONTRACT.yaml`, creating the domain
  directory if needed, and delete the workspace draft — an approved contract
  still sitting under `.velocai/` is a defect (ADR-0018).

Derive `<domain>` from the ADR's `domain` frontmatter exactly. It must be
kebab-case and must not be renamed, pluralized, or normalized to a near match.
If the destination contract already exists (workspace draft or durable file),
stop without changing it unless the invocation explicitly says to replace it.

Do not create or modify source code, tests, `CONCEPT.md`, ADRs, indexes, schemas,
templates, generated clients, reports, lockfiles, or any other file. Do not run
the scaffolder. Do not implement any declaration in the contract.

## Authoring procedure

1. Read the complete `ADR_PATH`, `CONTRACT_TEMPLATE`, and the normative
   schema `.velocai/schemas/CONTRACT.schema.json`. The schema defines
   validity (required blocks, enums, entry shapes); the template only
   demonstrates one valid instance.
2. Confirm the ADR frontmatter contains a valid `domain`. Stop without writing
   if it is absent or invalid.
3. Use the schema's key names, nesting, value vocabulary, and current
   `schema_version`. The template only demonstrates one valid instance; its
   example values are never evidence for this domain.
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
   values and comments except the first-line schema directive, and re-point
   that directive's relative path to the destination: a workspace draft uses
   `../../schemas/CONTRACT.schema.json`; a graduated contract uses
   `../../../.velocai/schemas/CONTRACT.schema.json`.
8. Record each fact required for a complete contract but not decided by the ADR
   as a specific `unresolved_gaps` entry. Do not hide missing information in a
   description or choose a default on the author's behalf.

## Lifecycle rules

- A proposed ADR establishes the contract's content; an accepted ADR is still
  only provenance, not contract approval.
- Without the complete approval input, emit `status: draft` in the task
  workspace, omit `approval`, and retain every unresolved gap.
- With complete approval input, emit `status: approved` at the durable
  location only if validation finds no unresolved gaps and every activated
  component is completely declared.
- If approval input is supplied but the contract is incomplete, emit a
  workspace draft without approval metadata. Never fabricate approval or its
  timestamp.
- Write `approved_at` quoted (`approved_at: "2026-01-01T00:00:00-05:00"`) —
  unquoted, YAML parses the timestamp as a datetime object instead of the
  string the schema requires.

## Validation and write boundary

Write the candidate only to the single destination its lifecycle state
permits, then check that same file parses as YAML and conforms to
`.velocai/schemas/CONTRACT.schema.json` — there is no runtime validator yet,
so schema conformance by inspection is the review bar. Also check the one
rule the schema cannot express: every endpoint id referenced from
`http.backend.endpoint_ids` or `frontend.segments.api` must resolve to a
declared `http.endpoints` entry. Fix conformance
errors only by editing that destination YAML and only when the ADR or
invocation provides the required fact. If a required fact is undecided,
represent it as an unresolved gap and keep the contract a workspace draft;
if the schema cannot represent that gap without an otherwise required
declaration, stop and report the missing decision without writing a
malformed contract.

Before finishing, inspect the working-tree diff and verify that this run
changed only the permitted destination (plus, on graduation, the removal of
the workspace draft). Preserve all pre-existing changes. Return one concise
line containing the contract path, lifecycle status, and validation result.
The response is a handoff, not a second artifact.

## Hand-off

- Draft written: tell the human to resolve `unresolved_gaps`, then re-invoke
  with the approval inputs to graduate the contract.
- Contract graduated: the domain is scaffoldable — next step is the
  scaffolder against `docs/domains/<domain>/CONTRACT.yaml`.
