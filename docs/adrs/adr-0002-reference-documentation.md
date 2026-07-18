---
id: ADR-0002
title: Introduce living reference documents for current-state configuration
status: accepted
date: 2026-07-18
projection: instructions
scope: docs/**
rule: "Record piecemeal, current-state configuration in docs/reference/ registry documents; reserve docs/adr/ for contested, point-in-time decisions. Reference entries link to an ADR when one exists; never accumulate configuration lists inside an ADR."
---

# Introduce living reference documents for current-state configuration

## Context

Environment and tooling configuration accretes piecemeal across working sessions rather than arriving as discrete, contested decisions. Each addition still needs three things captured: the configuration itself, what it does, and the rationale for adding it.

ADRs are the current canonical write path for durable decisions, but they are point-in-time, immutable-once-accepted records. Using an ADR as an accumulating configuration list would require continuous appending, which violates the ADR model (supersede, don't edit). Creating a full ADR per minor configuration addition produces noise and dilutes the signal of genuinely contested decisions.

A document class for *current state* is missing.

## Decision

Introduce **living reference documents** under `docs/reference/` as a second document class alongside ADRs:

- Reference documents are registries of what is in effect *now* — inventory-style, structured entries, no narrative or temporal framing.
- Each entry records: the configuration, what it does, and a short rationale.
- Reference documents are mutable by design; they are kept current through normal PR review. No immutability or supersession semantics apply.
- Entries may carry a per-entry `rule` field to participate in the same frontmatter-driven projection pipeline as ADRs.

## Relationship to ADRs

- ADRs remain the sole write path for contested decisions with rejected alternatives.
- When a reference entry embodies such a decision, the decision gets an ADR and the entry links to it. The registry holds state; the ADR holds reasoning history.
- ADRs are never used to accumulate configuration lists; reference documents are never used to record decision history.

## Consequences

- Agents consume current-state configuration directly from reference documents without the temporal-reasoning burden of walking an ADR trail.
- The ADR corpus stays high-signal: every ADR represents a genuine decision point.
- A registry entry without a linked ADR signals a low-stakes, uncontested addition; presence of a link signals settled, do-not-relitigate territory.
- The ADR template may need a lightweight update to reference this split (e.g., a "See also: reference entry" field), tracked separately.

## Rejected alternatives

- **Appendable ADRs**: violates the immutability principle; turns decision records into state documents and breaks supersession semantics.
- **One ADR per configuration addition**: correct semantics but disproportionate ceremony; buries contested decisions in noise.
- **Prose-only conventions doc without structure**: loses per-entry rationale and cannot feed the projection pipeline; drifts toward unmaintained narrative.
