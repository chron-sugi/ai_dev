---
# PLACEMENT (ADR-0009):
#   Domain-scoped knowledge → docs/domains/<domain>/CONCEPT.md
#     (fixed filename; the folder is the identifier).
#   Cross-cutting knowledge only → docs/concepts/<name>.md
#     (filename is the identifier).
# One sentence answering "should I load this?" — drives INDEX.md generation.
summary: >
  <What this concept is and when an agent needs it.>
# Glob(s) for the code territory this concept covers — enables path-scoped
# loading. For a domain CONCEPT.md, this is the domain package's territory.
scope: "<src/area/**>"
---

# <Concept Name>

<!--
MENTAL MODEL — required. 3–10 sentences.
How this actually works: the system shape a new agent would otherwise
reconstruct by reading code for twenty minutes. Analogies and structure,
not implementation detail. No file paths, no line numbers, no snippets.
End with a one-line ownership boundary. For a domain CONCEPT.md, contract
state (declared surface, endpoints, granted edges) is always on the far
side of that boundary — it belongs to the sibling CONTRACT.md (ADR-0009).
-->

<Mental model prose.>

<Owns X and Y; Z belongs to concept-<other>.>

## Invariants

<!--
CONDITIONAL — delete this section if no entry passes all three bars:
  (a) must-hold property
  (b) NOT mechanically checkable (lintable rules go to lint/hooks instead)
  (c) more than a bare ADR citation — the entry adds context the ADR lacks
One bullet per invariant. Cite ADRs inline where they exist.
-->

- <Property that must hold, with the context that makes it non-obvious
  (see adr-XXXX).>

## Gotchas

<!--
CONDITIONAL — delete this section if no entry passes the bar:
  admitted only if it caused a real debug loop (recurring: true evidence).
Pruned at every distill: entries contradicted by new evidence are removed.
Misleading entry points belong here, named by stable identifier only.
-->

- <Non-obvious behavior that has actually burned a session, and why.>

<!--
NEVER include: decision rationale (→ ADR), procedures (→ instructions),
contract state — surface, endpoints, dependency edges (→ sibling
CONTRACT.md, per ADR-0009), paths/lines/snippets, history, roadmap, or
anything derivable from the code in under a minute.
HARD CAP: 250 lines. Over budget = split or demote, never raise the cap.
ONE CONCEPT = one mental model, one noun phrase (no "and"), one contiguous
scope, changes together. Seam visible = split; interdependent = keep whole.
-->
