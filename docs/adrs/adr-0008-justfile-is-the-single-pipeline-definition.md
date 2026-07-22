---
id: ADR-0008
title: justfile as the single definition of the ADR pipeline
status: approved
date: 2026-07-21
domain: adr-pipeline
projection: instructions
scope: justfile,.github/workflows/**,scripts/**
rule: "Run ADR pipeline operations only through justfile recipes; never invoke the pipeline scripts directly from CI or ad-hoc commands."
---

# justfile as the single definition of the ADR pipeline

## Context

The pipeline has multiple entry points (lint, projection, drift check, status transitions) and two interchangeable implementations (Node and PowerShell). If CI workflows assemble their own script invocations, local runs and CI inevitably diverge — different flags, different shells, different profile state — and the byte-determinism contract is checked against two subtly different pipelines. Divergence of this kind is silent until a drift-guard failure that cannot be reproduced locally.

## Decision

The justfile is the single definition of every pipeline operation; CI invokes the same recipes (`just project-check` and peers) that developers and agents run locally. PowerShell recipes invoke `powershell.exe -NoProfile -ExecutionPolicy Bypass -File` so user profile state can never alter pipeline behavior.

## Rejected Alternatives

- **CI workflows calling scripts directly with their own flags** — local and CI drift apart; a check that passes locally and fails in CI (or vice versa) becomes undebuggable because the two are not running the same command.
- **npm scripts / package.json as the task runner** — ties orchestration to the Node implementation; the PowerShell implementation is a first-class peer and both must run through one runner.
- **Documented commands in a README** — prose invocation instructions rot and get retyped with variations; a recipe is executable documentation.

## Consequences

Any pipeline behavior change is made once, in the justfile, and applies identically everywhere; debugging a CI failure starts with running the identical recipe locally. The cost is that the justfile becomes load-bearing infrastructure: new pipeline operations must land as recipes, `just` becomes a required tool in CI and on dev machines, and the justfile itself belongs with `scripts/**` in the set of paths excluded from agent auto-approval.
