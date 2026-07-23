---
id: ADR-0004
title: No CONSTITUTION.md — durable rules enter the repo only as ADRs
status: accepted
date: 2026-07-21
domain: adr-pipeline
projection: instructions
scope: repo
rule: "Never create a CONSTITUTION.md or any monolithic hand-edited rules file; record each durable rule as its own ADR in docs/adrs/."
---

# No CONSTITUTION.md — durable rules enter the repo only as ADRs

## Context

Agentic development toolchains (spec-kit and similar scaffolds) popularize a single hand-maintained constitution file as the repository's governing rule set, and agents statistically default to creating one. This repo already routes durable decisions through per-decision ADRs, from which agent-facing surfaces (instruction files, the copilot block) are generated and status-filtered. A monolithic prose file carries no per-rule provenance, status, or supersession semantics, and LLMs weight content far more heavily than metadata — a stale imperative in a hand-edited rules file reads with full authority in agent context regardless of any header marking it outdated.

## Decision

The repository does not use a CONSTITUTION.md or any equivalent monolithic, hand-edited rules file. Individual ADRs in `docs/adrs/` are the sole write path for durable rules; the aggregated agent-facing rule surface exists only as a generated projection of `accepted` ADRs, never as a directly edited document.

## Rejected Alternatives

- **Hand-maintained CONSTITUTION.md as the canonical rule set** — creates a second write path competing with ADRs; individual rules have no status or supersession lifecycle, so retired rules linger as stale imperatives that poison agent context.
- **Constitution as an additional generated projection (compiled from accepted ADRs)** — the projection layer already produces exactly this artifact as instruction files and the copilot block; a second compiled surface with a different name adds a sync obligation and no new capability.
- **Hybrid: constitution for principles, ADRs for decisions** — splits authority across two documents with no mechanical rule for which governs on conflict; principles drift without the supersede-don't-edit discipline that keeps ADRs trustworthy.

## Consequences

Every durable rule gains provenance, rejected alternatives, and a supersession path by construction, and the projection pipeline remains the single source for agent-facing rules. The cost is granularity: there is no single human-readable "read this first" rules document, and anyone wanting that overview must read the generated projections or the ADR index. Scaffolding tools that emit a constitution file must have that output disabled or deleted, and reviewers should reject PRs introducing one.
