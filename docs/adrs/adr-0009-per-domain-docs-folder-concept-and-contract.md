---
id: ADR-0009
title: Per-domain documentation folder with exactly CONCEPT.md and CONTRACT.md
status: superseded
date: 2026-07-21
domain: concept-docs
scope: "docs/domains/**"
rule: "Document each domain only in docs/domains/<domain>/, which contains exactly CONCEPT.md (durable domain knowledge) and CONTRACT.md (the domain's current contract)."
projection: instructions
---

# Per-domain documentation folder with exactly CONCEPT.md and CONTRACT.md

## Context

Domain packages are scaffolded from ADRs whose binding declarations (exported surface, endpoints, granted cross-package edges) constitute a domain contract, but no artifact holds that contract's *current* state — it accretes across the granting ADR, later amending ADRs, and import-linter config. Agents working a domain-scoped task therefore have no single location to load, and agents writing documentation have no fixed layout to target — the statistically common default is a free-form per-domain README or a growing flat concepts directory.

## Decision

Each domain gets one folder, `docs/domains/<domain>/`, containing exactly two files: `CONCEPT.md`, holding the domain's durable knowledge under the content bars of the `/concept-create` prompt (mental model, invariants, gotchas; pull-loaded, line-capped), and `CONTRACT.md`, a current-state registry of the domain's contract — declared surface, endpoints, granted dependency edges — where each entry links to the ADR that granted it. Per the ADR-0002 split, `CONTRACT.md` holds state while the linked ADRs hold reasoning; the contract file is never a write path for new grants.

## Rejected Alternatives

- **Flat `docs/concepts/` files for domain knowledge (current convention)** — separates a domain's knowledge from its contract, gives the contract no home at all, and scatters what a domain-scoped task loads together; co-location by domain is the same delivery-granularity argument as ADR-0007.
- **Contract lives only in the granting ADRs** — ADRs are point-in-time and supersede-don't-edit; reconstructing the current contract requires walking the ADR trail, the exact temporal-reasoning burden ADR-0002 rejected for configuration.
- **Single combined `DOMAIN.md` per domain** — merges a pull-loaded explanatory document with a checkable state registry that have different consumers and update cadences; one file forces every contract amendment through the concept doc's line cap and content bars.
- **Free-form per-domain folder** — without a fixed two-file layout, agents scaffold ad-hoc files (`notes.md`, `api.md`, `README.md`) and the loading convention stops being predictable.

## Consequences

Domain-scoped tasks get one folder to load, and scaffolder prompts get a canonical location to read a domain's contract from instead of re-deriving it from ADRs. The `/concept-create` prompt and the `concept-docs` concept document must be updated to route domain-scoped knowledge to `docs/domains/<domain>/CONCEPT.md`, leaving `docs/concepts/` for cross-cutting concepts only — a migration obligation on existing concept files. `CONTRACT.md` is duplication by design (state copied from ADR declarations), which stays safe only while every entry cites its granting ADR; a contract entry with no ADR link is a defect, not a low-stakes addition.
