---
id: ADR-0018
title: Per-task workspace at .velocai/tasks/<task-id> with graduation at approval
status: accepted
date: 2026-07-22
domain: velocai-artifacts
scope: ".velocai/**"
rule: "Write every agent artifact for a development task under .velocai/tasks/<task-id>/, where the task id is a short descriptive kebab-case name."
projection: instructions
---

# Per-task workspace at .velocai/tasks/<task-id> with graduation at approval

## Context

ADR-0010 fixed `.velocai/` as the single parent for velocai-owned artifacts but deliberately left its internal layout open, so every session still re-decides how to organize output inside it. A development task produces a cluster of related artifacts — plans, research scratch, code reviews, and draft domain contracts — that are created together, reviewed together, and retired together at task closeout, yet nothing binds them to one location. ADR-0013 already describes `.velocai/tasks/<task-id>/` scratch descriptively, without making it normative, and draft contracts in particular have no home distinct from the durable `docs/domains/<domain>/CONTRACT.yaml` that ADR-0017 reserves for the approved current state.

## Decision

Each development task gets exactly one workspace directory, `.velocai/tasks/<task-id>/`, holding all agent artifacts produced for that task; the task id is a short descriptive kebab-case name (e.g. `adr-persistence`, `contract-schema-migration`), never an opaque ticket number, UUID, or timestamp. Artifacts in the workspace are drafts: a domain contract is authored there as `CONTRACT.yaml` and, once approved and implemented, moves to its durable home `docs/domains/<domain>/CONTRACT.yaml` per ADR-0017, after which the workspace copy is deleted. The workspace itself is ephemeral and is removed at task closeout, with anything durable graduating to its governed location (ADRs to `docs/adrs/`, contracts to `docs/domains/<domain>/`).

## Rejected Alternatives

- **Type-clustered subdirectories (`.velocai/plans/`, `.velocai/reviews/`, …)** — scatters one task's artifacts across type buckets, so closeout and retention require a sweep of every bucket instead of deleting one directory; same delivery-granularity argument as ADR-0007.
- **Opaque task ids (ticket numbers, UUIDs, timestamps)** — unreadable when browsing the tree, and agents resuming work cannot match a directory to a task without an external index.
- **Authoring draft contracts directly in `docs/domains/<domain>/`** — places unapproved state in the durable tree, where consumers cannot distinguish a draft from the approved contract that ADR-0017 makes the gate for scaffolding.
- **Fixing the full internal taxonomy of a task workspace (file names, retention tiers)** — over-constrains; only the per-task boundary needs pinning now, and finer structure can evolve without superseding this record.

## Consequences

Agents get one predictable workspace per task, and closeout, retention, and gitignore policy collapse to a single directory delete per task. The `.velocai/tasks/<task-id>/` convention ADR-0013 mentioned descriptively becomes normative, and existing loose artifacts under `.velocai/` must migrate into task directories. Graduation becomes an explicit obligation: an approved contract still sitting under `.velocai/` is a defect, since `docs/domains/<domain>/CONTRACT.yaml` is the only authoritative contract location per ADR-0017. Scaffolding and closeout prompts must be updated to read drafts from, and clean up, the task workspace.
