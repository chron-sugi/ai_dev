---
id: ADR-0007
title: Domain-clustered projection via declared frontmatter, not one file per ADR
status: proposed
date: 2026-07-21
domain: adr-pipeline
projection: lint
scope: docs/adrs/**
rule: "Declare an explicit kebab-case domain in frontmatter for every scoped projected rule; never emit or expect one instruction file per ADR."
---

# Domain-clustered projection via declared frontmatter, not one file per ADR

## Context

An ADR is the unit of decision, but agents consume rules by task context: the files that co-occur in a task define the useful delivery granularity. A 1:1 mapping from ADRs to instruction files is the default an agent (or generator author) would reach for, yet it fragments activation — dozens of small files with overlapping globs, file churn on every supersession, and no natural place for related rules to travel together. The compiler must also be deterministic, which rules out any clustering the generator has to infer.

## Decision

Many ADRs project into one instruction file per **domain** — a kebab-case value declared in each ADR's `domain:` frontmatter field, required for every non-universal projected rule and validated by `scripts/adr-lint`. The generated `<domain>.instructions.md` file's `applyTo` is the union of member ADR scopes, and traceability is per projected line via ADR-ID citation, not per file.

## Rejected Alternatives

- **One instruction file per ADR (1:1 projection)** — fragments delivery into per-decision files, churns files on supersession instead of producing a clean content diff, and multiplies activation contexts; singleton domains already cover the degenerate case where 1:1 is genuinely right.
- **Inferred clustering (generator groups ADRs by glob similarity)** — declared beats clever; the compiler must be deterministic, and inference makes projection output depend on a heuristic that can silently reshuffle files.
- **Per-file source mapping for traceability** — ADR-ID citation on each projected line is finer-grained and survives clustering; a file-level map adds a second artifact to keep in sync.

## Consequences

Supersession becomes a clean diff inside one domain file, and rules that co-occur in tasks arrive in one activation context. The cost is a curation duty: a domain whose glob union spans trees that never appear in the same task should be split, and a domain approaching 15–20 rules signals splitting or, more often, demotion of rules down to lint. The `domain:` field becomes required schema surface that `adr-lint` must enforce and the drafting prompt must request.
