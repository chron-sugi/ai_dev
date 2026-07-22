---
id: ADR-0011
title: Framework-owned justfile with project recipes in justfile.local
status: accepted
date: 2026-07-22
domain: task-runner
scope: "justfile,justfile.local"
rule: "Add project-specific just recipes only to justfile.local, never to the framework-owned justfile."
projection: instructions
---

# Framework-owned justfile with project recipes in justfile.local

## Context

The framework is deployed into consuming projects, and each deploy must be able to update the pipeline recipes that ADR-0008 makes load-bearing. Projects also accumulate their own task recipes over time. If both kinds of recipes live in one file, a framework deploy either clobbers project recipes or must merge into a hand-edited file, and neither outcome is reliable. An agent's default instinct — append a new recipe to the justfile it can see — silently plants recipes that the next deploy destroys.

## Decision

Two justfiles: the root `justfile` contains framework-only recipes and is copied over verbatim (overwritten) on every framework deploy; `justfile.local` holds project-specific recipes and is never touched by the deploy. The framework justfile includes `justfile.local` via just's optional import (`import? 'justfile.local'`) so project recipes remain invocable through the single `just` entry point required by ADR-0008.

## Rejected Alternatives

- **Single justfile merged on deploy** — recipe-level merging of a hand-edited file is fragile; a bad merge corrupts the pipeline definition that CI and drift checks depend on.
- **Marked "project section" inside one justfile** — requires the deploy tooling to parse and preserve regions of a file it otherwise owns; one stray edit outside the markers is silently lost.
- **Project tasks in a separate runner (npm scripts, raw scripts)** — splits task orchestration across two runners, contradicting ADR-0008's single-entry-point rationale.

## Consequences

Framework deploys become a safe blind overwrite of the root justfile, and project recipes survive every upgrade untouched. The cost is a convention agents and developers must know: any recipe added to the root justfile will be lost on the next deploy, so review must police recipe placement, and the deploy tooling must never write `justfile.local` (creating an empty stub on first deploy is the one allowed exception, so the optional import always resolves cleanly).
