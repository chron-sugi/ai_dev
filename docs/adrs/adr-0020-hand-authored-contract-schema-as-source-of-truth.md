---
id: ADR-0020
title: Hand-authored JSON Schema as the source of truth for contract validity
status: accepted
date: 2026-07-22
domain: concept-docs
scope: ".velocai/schemas/CONTRACT.schema.json,.velocai/templates/CONTRACT.yaml,docs/domains/**/CONTRACT.yaml"
rule: "Treat .velocai/schemas/CONTRACT.schema.json as the sole authority on domain-contract validity; validators and templates conform to it, never define it."
projection: instructions
---

# Hand-authored JSON Schema as the source of truth for contract validity

## Context

Domain contracts (ADR-0017) need a definition of validity — required blocks, enums, entry shapes — that humans can approve and machines can check. The first implementation made pydantic models the source of truth and generated the JSON Schema from them, so approving a format change meant reading Python, and the format was coupled to an implementation that was ultimately rejected and removed. In the interim the authoring template served as the only shape authority, which left every empty list, enum vocabulary, and required-versus-optional question undefined. The statistically common default — models as source, schema as build artifact — is exactly the arrangement that failed here, so the direction of authority must be recorded or it will be rebuilt that way.

## Decision

The contract format is defined by exactly one artifact: the hand-authored JSON Schema at `.velocai/schemas/CONTRACT.schema.json`. Facts split three ways — semantics (lifecycle, presence-means-create) live in ADRs and are echoed in the schema's `description` fields; validity lives only in the schema; authoring ergonomics live in the template at `.velocai/templates/CONTRACT.yaml`, which demonstrates one valid instance, must always validate against the schema, and never states a constraint of its own. Any future runtime validator consumes or is checked against this schema file; code conforms to schema, never the reverse. This displaces the maintenance mechanism ADR-0017's consequences anticipated (pydantic models with a generated schema and drift check) while leaving ADR-0017's rule — contract location and primacy — untouched.

## Rejected Alternatives

- **Pydantic models as source with generated JSON Schema (the removed implementation)** — format approval requires reading code, couples a still-evolving format to application internals, and was already rejected in practice.
- **Template as sole shape authority (the interim state)** — a template can only teach by example; empty lists, enum vocabularies, and required-versus-optional splits stay undefined, so identical inputs produce differently-shaped contracts.
- **Defer any schema until a runtime validator is chosen** — couples settling the format to a tooling decision (a `jsonschema` dependency is ask-first under ADR-0012), while editor-level validation via the `yaml-language-server` directive is available for free today.
- **Restating shape rules in prompts and agent instructions** — N prose copies of the format drift independently; prompts should point at the schema, not paraphrase it.

## Consequences

Format changes become data diffs a human can review and approve without reading code, and every `CONTRACT.yaml` gets editor-time validation through its schema directive. The template gains a standing obligation: it must validate against the schema on every change — currently checked by hand, and the natural first test if a runtime validator is ever added. Constraints not expressible in JSON Schema (endpoint-id referential integrity) remain prose in the schema's descriptions and must be checked by reviewers. `schema_version` inside contracts now tracks this file: a shape-changing schema edit bumps it.
