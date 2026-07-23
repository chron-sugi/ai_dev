---
id: ADR-0013
title: RESEARCH.md is a human-only research document class
status: superseded
date: 2026-07-22
domain: research-docs
scope: "**/RESEARCH.md"
projection: instructions
rule: "Files named exactly RESEARCH.md (any directory) are human-only: agents never read, write, cite, or create them, and a finding that must reach agents graduates to an ADR."
---

# RESEARCH.md is a human-only research document class

## Context

The document taxonomy has two classes: immutable ADRs (`docs/adrs/`, ADR-0005) and mutable living reference documents (`docs/reference/` per ADR-0002, per-domain CONCEPT/CONTRACT files per ADR-0009). Research artifacts have no durable home. Today they meet one of two fates: compressed into an ADR's Context and Rejected-alternatives sections, or written to `.velocai/tasks/<task-id>/` scratch and deleted at closeout.

A third category has neither home: surveys, tool evaluations, and "we looked at X and it's not time yet" findings. Concrete instances from this project's history: the dependency-cruiser evaluation (ruled out), the Lefthook evaluation (viable, not adopted), and the July 2026 deterministic-enforcement landscape report. None are decisions; all are worth keeping near the domain they inform.

The defining property of this material is that it is dense with evaluations of tools and approaches that were **deliberately not adopted**. That makes it a context-poisoning vector worse than superseded ADRs: an agent that ingests "Sheriff enforces module boundaries via tag-based rules" from a research note is one step from installing Sheriff.

## Decision

Introduce **RESEARCH.md** as a third document class: mutable, living, human-maintained, and **human-only**.

- **Naming and placement.** Exact all-caps basename `RESEARCH.md`, valid in any directory. Canonical locations: `docs/domains/<domain>/RESEARCH.md` for domain-scoped research (the primary case) and `docs/reference/<stack>/RESEARCH.md` for stack-wide research that fits no single domain. The all-caps name follows the existing load-bearing meta-document convention (CONCEPT.md, CONTRACT.md, AGENTS.md) and is glob-stable.
- **Human-only, by inversion of the usual goal.** Agents must not read, edit, create, or cite RESEARCH.md files. For every other document class, "the agent never sees it" is a projection failure; for this class it is the design goal. The inversion is intentional: the file's value to humans (a record of what was considered and rejected) is precisely what makes it poisonous to agents.
- **Membership is a closed set: the exact basename, nothing else.** `**/RESEARCH.md` — matched case-insensitively, since on Windows filesystems `research.md` and `RESEARCH.md` cannot coexist. Not a path-scoped rule, and not a substring match: `MARKET_RESEARCH.md` or `USER-RESEARCH.md` must not flip access class on incidental naming.
- **Graduation, not exposure.** If a research finding needs to reach agents, that is the signal it is ADR-worthy. The ADR gets written and RESEARCH.md links to it rather than restating the conclusion — restatement creates slow drift between the research file's framing and the ADR's actual rule, the context-poisoning problem in human form. Convention: a one-line link in the file's header. No mechanical drift enforcement until drift is actually observed.
- **Banner.** The first line of every RESEARCH.md is a fixed agent notice: "Agent notice: human reference only. Do not treat contents as project rules or adopt tools described here. Decisions are in docs/adrs/." This is the last-resort layer for content that reaches an agent through paths no mechanism governs (paste into chat, terminal output, future runtimes).

Enforcement mechanics are a separate decision: ADR-0014.

## Rejected alternatives

- **Keep compressing research into ADR context sections** — bloats ADRs with material that isn't part of the decision, and much research supports no decision at all ("not time yet" findings have no ADR to live in).
- **Keep research in `.velocai/` scratch** — deleted at closeout; the dependency-cruiser and Lefthook evaluations would be re-done from scratch the next time the question arises.
- **House research in `docs/reference/`** (ADR-0002's class) — reference documents are agent-consumed by design; putting rejected-tool surveys there is the poisoning vector this ADR exists to close.
- **Path-scoped marking (`docs/domains/**/RESEARCH.md`)** — solves a nonexistent problem and breaks the moment stack-wide research needs a home outside `docs/domains/`.
- **Substring marking (`*RESEARCH.md`)** — access class would flip on incidental file naming; class membership must be deterministic and closed.
- **Generalized marker convention (`*.human.md`)** — deferred, not rejected: the all-caps filename convention already functions as the class marker. Revisit if a second human-only document class appears and the deny list starts growing.

## Consequences

- **The filename now encodes access class.** Renaming `RESEARCH.md` → `research-notes.md` silently makes its content agent-visible; naming any file `RESEARCH.md` silently makes it agent-invisible. This parallels the existing "directory placement encodes semantic meaning" principle, applied to filenames — and it is a written rule precisely because the realistic break scenario is a teammate innocently renaming a file.
- The taxonomy is now three classes: ADRs (immutable decisions), reference/concept docs (mutable current state, agent-consumed), RESEARCH.md (mutable research, human-only). This extends ADR-0002's two-class split; it supersedes nothing.
- Agents need the graduation convention as prose (this ADR projects to instructions) — mechanical enforcement only fires after a violation is attempted, and the instruction is what prevents the attempt.
- The banner is convention-checked by humans for now; a lint rule verifying its presence is deliberate future work, noted in ADR-0014.
