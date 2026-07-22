---
# PROPOSALS.md — distiller output for the sibling research file.
# Records dispositions, not rules. ADRs remain the single write path for decisions.
research: ./RESEARCH.md        # sibling research file this distills
task: <task-id>                # task that dispatched the distiller
date: YYYY-MM-DD               # distillation date
status: pending                # pending | triaged (triaged = every proposal has a verdict)
---

# Proposals

<!--
One `##` block per proposal. All fields required except `adr`, which is added
as a back-link once the approved proposal has an authored ADR.

verdict values: pending | approved | approved-with-modification | rejected
Mechanical triage triggers:
  - file status is `pending` while any proposal has `verdict: pending`
  - `verdict: approved*` with no `adr:` field = pending ADR authoring
-->

## P-001: <short imperative title>

- **decision**: <the proposed durable decision, one or two sentences>
- **rule**: `<draft atomic rule line, written as it would project>`
- **class**: architecture | convention
- **rejected-alternatives**:
  - <alternative> — <one-line reason it loses>
  - <alternative> — <one-line reason it loses>
- **rationale**: <why this is ADR-worthy: what an agent or future developer could plausibly re-litigate>
- **source**: <section heading or anchor in the sibling research file>
- **verdict**: pending
- **verdict-note**: <human note; required for rejected or approved-with-modification>
- **adr**: <ADR id, e.g. ADR-0007 — added after authoring; approved proposals without this are pending dispatch>

## P-002: <short imperative title>

- **decision**:
- **rule**: ``
- **class**:
- **rejected-alternatives**:
  -
- **rationale**:
- **source**:
- **verdict**: pending
- **verdict-note**:
- **adr**:

# Not proposed

<!--
Mandatory, even if empty (write "None."). Findings the distiller judged NOT
ADR-worthy, one line each with the reason. Reviewing what the distiller chose
to omit is where distillation errors hide.
-->

- <finding> — <one-line reason it is not ADR-worthy>
- <finding> — <one-line reason it is not ADR-worthy>