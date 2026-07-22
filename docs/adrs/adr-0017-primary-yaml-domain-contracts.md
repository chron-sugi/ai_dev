---
id: ADR-0017
title: Primary YAML contracts for documented domains
status: accepted
date: 2026-07-22
domain: concept-docs
supersedes: ADR-0009
scope: "docs/domains/**,src/assets/agents/scaffolder.velocais.md,src/assets/prompts/scaffold-*.md"
rule: "Define each documented domain's current executable contract in docs/domains/<domain>/CONTRACT.yaml."
projection: instructions
---

## Context

Domain scaffolding needs exact, machine-valid declarations for optional Python packages, frontend slices, and their HTTP seam. The Markdown registry established by ADR-0009 records current prose but cannot distinguish an intentionally omitted component from a missing decision or validate cross-component references. Requiring scaffolders to recover executable details from ADR prose also prevents deterministic gap detection and excludes work whose governing ADR is not accepted.

## Decision

Each documented domain uses `CONCEPT.md` for durable explanatory knowledge and `CONTRACT.yaml` as its primary executable specification. Contracts may cite ADRs as optional provenance, but their own validation and approval state determine whether scaffolding may proceed.

## Rejected Alternatives

- **Keep CONTRACT.md and add YAML beside it** — two current-state representations create an immediate drift obligation and leave authority ambiguous.
- **Generate YAML only from accepted ADRs** — prose ADRs do not contain every scaffold declaration reliably, and accepted-ADR status is not the contract approval boundary.
- **Let scaffold prompts infer missing declarations** — model judgment makes identical inputs produce different structures and hides specification gaps until implementation.

## Consequences

Domain contracts become strict, testable inputs that humans or agents can approve after resolving every gap. Existing Markdown contracts must migrate without losing their effective rules, and scaffold prompts must consume validated YAML rather than requiring an accepted ADR. The application must maintain Pydantic models, safe YAML loading, and a generated JSON Schema as the contract format evolves.
