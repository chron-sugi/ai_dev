---
id: ADR-0023
title: Standards registry as the low-ceremony write path for standing rules
status: accepted
date: 2026-07-23
domain: adr-pipeline
supersedes: ADR-0004
scope: repo
rule: "Record a durable rule as its own ADR in docs/adrs/ when it is structural or contested, or as a single rule line in docs/standards/<domain>.md when it is an uncontested standing rule; never in a monolithic hand-edited rules file."
projection: instructions
---

# Standards registry as the low-ceremony write path for standing rules

## Context

ADR ceremony — qualification gate, rejected alternatives, immutability with supersession — is right for structural choices an agent could re-litigate, and wrong for low-stakes standing rules like naming schemes, styling idioms, and usage conventions within settled stack selections. ADR-0004 made ADRs the sole write path for durable rules, so these small rules either pay full ceremony or go unrecorded and never reach the projected instruction surfaces. A rule class was needed that is durable and projectable but cheap to author and cheap to edit as the codebase evolves, without reopening the door to the monolithic constitution file ADR-0004 rejected.

## Decision

Durable rules have two write paths, both compiled into the same domain-clustered projection surfaces (ADR-0007). ADRs remain the home for structural or contested decisions. Uncontested standing rules live in the standards registry: one file per projection domain at `docs/standards/<domain>.md`, with frontmatter of exactly `domain` (from the projector's domain vocabulary) and `scope` (one quoted glob string). Only single-bullet lines under a `## Rules` section are projected — each one imperative, self-contained sentence, held to the same discipline as the ADR `rule` field; `## Enforced by lint` lines (which must name their enforcing tool) and `## Notes` are never projected. Standards are edited in place under normal PR review; git history is the record.

Precedence is non-negotiable: on conflict with an accepted ADR rule, the ADR wins and the standard line is deleted or rewritten; the projector fails on exact-duplicate rule text across the two sources. Routing works down a ladder, stopping at the first match: mechanizable → lint config; structural, contested, or fighting the model's training-data defaults → ADR; descriptive domain shape → `docs/domains/<domain>/CONCEPT.md`; standing "do it this way" rule with an obvious right answer → standards registry. The moment a standard is contested, it is promoted to an ADR and its registry line deleted in the same PR.

Projection merges accepted ADR rules first, then standard rules, each block sorted by source id/filename for deterministic output; every line cites its source (`ADR-NNNN` or `standards/<domain>`); `applyTo`/`paths` is the union of member ADR scopes and the standards file's `scope`; the combined per-domain file is what the token budget gate measures, and a generated footer line links the full standards doc. Registry tooling (parser, `standards-lint`, generator extension) is stdlib-only Python 3 per ADR-0012 and runs only through `just` recipes per ADR-0008.

This ADR supersedes ADR-0004 only to widen the write path; its core prohibition stands and is carried in this ADR's rule: no `CONSTITUTION.md` or any monolithic hand-edited rules file, and generated surfaces are still never hand-edited (ADR-0006).

## Rejected Alternatives

- **Status quo — every durable rule is an ADR (ADR-0004)** — full ceremony on "boolean props are named `is*`" either deters recording or floods `docs/adrs/` with trivial immutable records that need supersession for a naming tweak.
- **Hand-authoring instruction files directly with a sync script** — ADR rules and standards for one domain must coexist in one projected file, so a merge step exists regardless; hand-authored targets silently escape the budget gate, drift check, and duplicate-vs-ADR check, and the Copilot/Claude frontmatter dialects make the "small sync script" grow into a worse projector.
- **Defining standards negatively as "everything that isn't an ADR"** — invites dumping; concept docs, contracts, and reference docs are also non-ADR homes, so a standard is defined positively as a projectable standing rule with an obvious right answer.
- **Alternative names (rules, conventions, guidelines, policies, practices, idioms)** — "rules" is already overloaded three ways (ADR `rule` field, `.claude/rules/` target, projected line); "conventions/guidelines" read as optional to an agent; "policies" pulls toward policy-as-code governance; "practices" and "idioms" are respectively mushy and too narrow.

## Consequences

Small durable rules become cheap to record and edit, and the budget gate now measures the combined ADR-plus-standards domain file — ceiling pressure correctly pushes standards down the enforcement ladder into lint or golden files first. What must now be maintained: a standards parser and `standards-lint` (stdlib-only Python, wired into the `just` menu and hooks), a generator that takes two input sets with an exact-duplicate failure mode, and test scenarios covering propagation, deletion, duplicate-of-ADR, unknown domain, and budget bust. Reviewers gain a duty the tooling cannot fully automate: catching semantic (non-verbatim) conflicts between standards and ADR rules, and spotting contested standards that need promotion.
