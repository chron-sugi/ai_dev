---
id: ADR-0006
title: Generated agent-facing surfaces are never hand-edited
status: accepted
date: 2026-07-21
domain: adr-pipeline
projection: lint
scope: .github/copilot-instructions.md,.github/instructions/**,.claude/rules/**
rule: "Never hand-edit a generated instruction file or sentinel-marked region; change the source ADR and re-run projection."
---

# Generated agent-facing surfaces are never hand-edited

## Context

Instruction files are the delivery channel agents actually read, so they are the natural place to "quickly fix" a rule — a one-line edit that silently forks the compiled output from its source ADR. Research on hand-maintained agent context files shows they rot silently (arXiv 2511.12884), and a forked surface is worse than a stale one: it carries authority while no longer tracing to any decision record. The projection pipeline can only guarantee that agents see exactly the accepted rule set if the compiled output is mechanically derived and nothing else.

## Decision

All agent-facing rule surfaces are compiled output of `scripts/project-adrs`. Generated regions are marked with sentinels; hand-authored content outside sentinels survives regeneration; edits inside generated files or regions are forbidden. Enforcement is mechanical: CI runs the drift guard (`just project-check`, which invokes `project-adrs --check`) and fails on any divergence between committed output and a fresh projection. Only files bearing the generated notice may ever be auto-deleted by the pipeline.

## Rejected Alternatives

- **Hand-maintained instruction files with ADRs as background reading** — the two drift apart within sessions; compiled rules measurably outperform prose precisely because they cannot diverge from source.
- **Convention only ("please regenerate after editing ADRs") without a CI guard** — prose instructions do not survive agent sessions that never loaded them; drift becomes unmergeable only if CI makes it so.
- **Fully generated files without sentinel regions** — forfeits legitimate hand-authored content (project-specific prose around the rule block); sentinels let generated and human content coexist in one file.

## Consequences

Local and CI can never disagree about what agents are told: the drift guard makes a hand edit unmergeable rather than merely discouraged. The cost is a mandatory regeneration step in every rule-changing workflow, and the sentinel markers plus generated notice become load-bearing strings the scripts must preserve exactly. Any new projection target (e.g. `.claude/rules/`) must be added to the same desired-outputs map so the one drift guard covers it.
