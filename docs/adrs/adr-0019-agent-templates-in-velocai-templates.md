---
id: ADR-0019
title: Flat .velocai/templates directory for agent-facing document templates
status: accepted
date: 2026-07-22
domain: velocai-artifacts
scope: ".velocai/templates/**"
rule: "Read and store agent-facing document templates only in the flat .velocai/templates/ directory, never under docs/."
projection: instructions
---

# Flat .velocai/templates directory for agent-facing document templates

## Context

Agent workflows consume authoring templates — the shapes for `CONTRACT.yaml`, `CONCEPT.md`, and similar documents — but those templates currently live inside the human documentation tree as underscore-prefixed siblings of the documents they produce (`docs/domains/_contract_template.yaml`, `docs/domains/_concept_template.md`). That placement mixes app-supplied, deploy-updated assets into `docs/`, which ADR-0010 reclaimed for durable human-audience content, and leaves each new template to re-litigate its own location and naming convention. ADR-0010 fixed `.velocai/` as the parent for everything velocai-owned but deferred its internal layout; ADR-0018 has since pinned `.velocai/tasks/` for task workspaces, leaving templates as the remaining unplaced artifact class.

## Decision

Agent-facing document templates live in `.velocai/templates/`, a flat directory with no subdirectories, alongside `.velocai/tasks/`. Each template file is named for the document it produces (e.g. `CONTRACT.yaml`, `CONCEPT.md`), so the filename alone identifies the target document type. The templates currently under `docs/` move to this directory; like all `.velocai/` app-supplied content, templates are owned by the velocai app and refreshed on framework deploy — template changes are made in the framework source (`src/templates/`, `src/assets/`), not by hand-editing the deployed copies.

## Rejected Alternatives

- **Templates beside their destination documents (current convention, `docs/domains/_*_template.*`)** — mixes app-owned deploy artifacts into the human documentation tree ADR-0010 reclaimed, and the underscore-prefix naming is an unenforced convention each author must rediscover.
- **Per-type subdirectories (`.velocai/templates/contract/`, `.velocai/templates/concept/`)** — hierarchy adds lookup indirection for a small, flat file set whose filenames already identify the document type.
- **Reading templates directly from `src/templates/` or `src/assets/`** — couples agent behavior to framework source internals, and consumer repositories receive only deployed assets, not the framework's `src/` tree.
- **`.github/` as the host namespace** — owned by GitHub/Copilot surfaces, partly generated and hand-edit-forbidden per ADR-0006; rejected for the same reason in ADR-0010.

## Consequences

Agents get one fixed, flat location to read any document template from, and the `docs/` tree sheds its last app-supplied files. This obligates a migration: `docs/domains/_contract_template.yaml` and `docs/domains/_concept_template.md` move to `.velocai/templates/`, and every surface referencing the old paths — the AGENTS.md pointers, `create-domain-contract` (`CONTRACT_TEMPLATE` default), `concept-create`, and the curator agent — must be updated. The `yaml-language-server` schema directive inside the contract template must be re-pointed, since the relative path to the JSON Schema changes with the move.
