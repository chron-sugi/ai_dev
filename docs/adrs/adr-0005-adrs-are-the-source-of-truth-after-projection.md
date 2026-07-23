---
id: ADR-0005
title: ADRs remain the source of truth after projection
status: accepted
date: 2026-07-21
domain: adr-pipeline
projection: instructions
scope: docs/adrs/**
rule: "Treat the ADR as the permanent source of truth for its rule; never delete or condense an ADR because its rule already appears in a generated file."
---

# ADRs remain the source of truth after projection

## Context

Once a projection pipeline compiles each ADR's atomic `rule` into agent-facing instruction files, the full ADR record can look redundant — the rule is already delivered where agents read it. An agent optimizing for context economy will plausibly propose deleting or trimming projected ADRs. But the rule is the only atomic part of the record: the context, consequences, supersession history, and rejected alternatives are the payload that stops future sessions from re-litigating the decision, and none of that survives in the compiled output. ADR-0004 establishes ADRs as the sole write path for durable rules; this record settles what happens to them after compilation.

## Decision

ADRs in `docs/adrs/` are the permanent source of truth for every projected rule. Projection is a read-only derivation: compiled instruction files carry rules, ADRs carry reasoning, and the existence of the compiled output never justifies removing, truncating, or summarizing the source record.

## Rejected Alternatives

- **Delete or archive ADRs once their rule is projected** — inverts the architecture; the compiled rule loses its provenance and the rejected-alternatives payload that prevents re-litigation is destroyed.
- **Make instruction files canonical and demote ADRs to commentary** — hand-maintained context files rot silently (arXiv 2511.12884); the write path must stay with the schema-validated, lifecycle-governed record.
- **Merge rule and full reasoning into one always-loaded document** — blows the always-on token budget and defeats progressive disclosure; the index-plus-on-demand tiering depends on ADRs staying separate from delivery surfaces.

## Consequences

Every projected rule stays traceable to its full decision record, and supersession history accumulates in one governed place. The cost is duplication by design: each rule exists in the ADR and in generated output, which is safe only because the generator plus CI drift guard keep the copy mechanically derived (see ADR-0006). The ADR corpus grows monotonically; superseded records are retired by status transition, never by deletion.
