---
id: ADR-0010
title: .velocai as the single parent directory for velocai-owned artifacts
status: proposed
date: 2026-07-21
domain: velocai-artifacts
scope: ".velocai/**"
rule: "Write velocai-generated or velocai-provided files — ephemeral agent artifacts, app-supplied scripts, and velocai-specific context — only under the .velocai/ directory."
projection: instructions
---

# .velocai as the single parent directory for velocai-owned artifacts

## Context

Agent sessions continuously produce ephemeral artifacts — plans, code reviews, research notes — and the velocai app additionally ships its own material into consumer repositories: justfile scripts, context files, and other app-specific support files. Without a designated home, this output scatters into whatever location each session defaults to: this repo already holds a plan under `docs/plans/`, and the workspace template ships a `docs/.velocai/` workspace for the same artifact class. Every scattered location pollutes the human documentation tree, complicates retention and gitignore policy, and forces each new agent session to re-decide where output belongs.

## Decision

`.velocai/` at the repository root is the single parent directory for everything velocai owns: ephemeral agent artifact generation (plans, code reviews, and similar), justfile scripts provided by the velocai app, and any other velocai-specific context or scripts. The root justfile remains the single pipeline entry point per ADR-0008; velocai-provided recipes live under `.velocai/` and are wired in from the root justfile rather than invoked directly.

## Rejected Alternatives

- **`docs/.velocai/` workspace (current template convention)** — mixes app-owned, retention-governed output into the human documentation tree, and the dot-directory-inside-docs layout is invisible enough that sessions keep writing to `docs/plans/` anyway.
- **Per-type directories (`docs/plans/`, `docs/reviews/`, …)** — every artifact class re-litigates its own location, and durable human docs and ephemeral machine output end up interleaved under `docs/`.
- **`.github/` as the host namespace** — that namespace is owned by GitHub/Copilot surfaces, parts of which are generated and hand-edit-forbidden per ADR-0006; app artifacts there would be indistinguishable from projection output.
- **OS temp or untracked scratch directories** — artifacts vanish between sessions and are unreachable by cloud agents; ephemeral-but-shared output must live inside the repository tree.

## Consequences

Agents get one non-negotiable write target for generated artifacts, and retention, gitignore, and review policy can be expressed once against a single subtree instead of per location. The `docs/` tree returns to being exclusively durable, human-audience documentation. This obligates a migration: existing ephemeral artifacts (e.g. `docs/plans/adr-persistence.plan.md`) move under `.velocai/`, and the workspace template's `docs/.velocai/` convention must be updated to match. The internal layout of `.velocai/` (subdirectory names, retention tiers) is deliberately not fixed here and can evolve without superseding this record.
