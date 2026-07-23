---
id: ADR-0024
title: RESEARCH.md human-only boundary is delivered outside projection
status: proposed
date: 2026-07-23
domain: research-docs
supersedes: ADR-0013
scope: "**/RESEARCH.md"
rule: "Files named exactly RESEARCH.md (any directory) are human-only: agents never read, write, cite, or create them, and a finding that must reach agents graduates to an ADR."
projection: none
---

# RESEARCH.md human-only boundary is delivered outside projection

## Context

ADR-0013 established the RESEARCH.md human-only boundary but declared
`projection: instructions` with scope `**/RESEARCH.md`, while ADR-0014's rule
forbids RESEARCH.md from appearing in any projection output or instruction
glob. The two accepted records therefore contradict at the frontmatter level:
honoring ADR-0013's declared delivery would emit exactly the glob ADR-0014
bans. The projection generator currently resolves this by hardcoding an
exclusion for RESEARCH.md-scoped records, which leaves the contradiction
standing in the source corpus and a permanent special case in the compiler.
Accepted ADRs are immutable, so the metadata cannot be corrected in place.

## Decision

The boundary itself is unchanged and restated here verbatim; only its delivery
changes. This record supersedes ADR-0013 with `projection: none`: the rule
reaches agents through hand-authored surfaces (AGENTS.md) and the mechanical
enforcement layers ADR-0014 defines (Claude Code permission deny rules plus
the shared PreToolUse guard), never through projected instruction files or
their activation globs.

## Rejected Alternatives

- **Keep `projection: instructions` on the successor record** — re-creates the
  contradiction with ADR-0014 and forces the generator to special-case the
  exclusion forever; a path-scoped instruction file is also useless for a file
  class agents are mechanically denied from touching.
- **Edit ADR-0013's frontmatter in place** — accepted ADRs are immutable;
  supersession is the only change path.
- **Project the rule as a universal (glob-less) instruction** — still places
  the RESEARCH.md name into generated projection output, which ADR-0014's rule
  forbids; the always-on delivery already exists in hand-authored AGENTS.md.

## Consequences

The corpus becomes self-consistent: no projectable record requests a
RESEARCH.md glob, so the generator's ADR-0014 exclusion guard becomes a
defensive backstop rather than the active resolution of a live contradiction.
ADR-0013 transitions to `status: superseded` and drops out of projection by
status. Delivery of the boundary now depends entirely on AGENTS.md staying
hand-curated and the ADR-0014 enforcement layers staying wired; any future
wish to project this rule requires a new ADR superseding both this record and
ADR-0014 together.
