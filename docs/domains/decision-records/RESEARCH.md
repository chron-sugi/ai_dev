The failure mode to design against is your own principle: agents have unreliable conditional judgment. "Is this re-litigatable?" is a vibes question — an agent will answer it inconsistently. The fix is to replace every judgment call with an **evidence-production test**: the agent doesn't *assess* a property, it must *produce a concrete artifact* proving the property, and failure to produce = criterion not met. That makes classification mostly mechanical and self-documenting, because the produced evidence becomes ADR/standard content.

Here's the gauntlet — strictly ordered, stop at first match:

**Q1 — Durable?** Would this still bind after the current task is merged and forgotten? No → task notes in `.agent/<task-id>/`, stop. (Filters out "for this PR, put the fix in module X.")

**Q2 — Prescriptive?** Rewrite it as one imperative sentence commanding future behavior. Can't → it's descriptive knowledge → `CONCEPT.md` / `CONTRACT.md` / reference doc, stop. (Filters out "the `severity` field is populated only after triage.")

**Q3 — Mechanizable?** Evidence test: **name the tool and the specific rule/config** from the approved toolset (ruff `TID251`, import-linter contract, Steiger, ESLint rule, ast-grep pattern, commitlint) that enforces it deterministically. Named → lint config + `## Enforced by lint` ledger line, stop. Can't name a real tool+rule → not mechanizable today, continue. The naming requirement matters: "this could probably be linted somehow" doesn't pass.

**Q4 — ADR triggers.** Any *one* of these, with its evidence, routes to ADR:

| Trigger | Evidence the agent must produce |
|---|---|
| Selection between alternatives | Name at least one **real, viable** rejected alternative that a competent developer or default-configured agent would actually choose. Can't name one honestly → trigger not met. (Doubles as the anti-invented-alternatives safeguard — the evidence *is* the Rejected Alternatives section.) |
| Model contamination | Name the specific wrong output training defaults produce (`class Config`, `@validator`, `tailwind.config.js`, v3 directives). This is checkable: would an unprompted agent plausibly emit the violation? |
| Expensive to reverse | Name what a reversal touches — migration, N files, a public interface. |
| Cross-domain reach | Name two+ projection domains the rule constrains. |
| Already contested | Cite where someone (human or agent) argued the other way. |

**Q5 — Standard gate.** No Q4 trigger fired, *and* it passes the atomicity contract: one imperative sentence, self-contained, single projection domain, obvious right answer. → `docs/standards/<domain>.md` via PR.

**Q6 — Default on ambiguity: escalate up, never down.** This is the load-bearing asymmetry. If the agent is unsure between ADR and standard, it proposes an **ADR candidate** — because an over-proposed ADR costs one human verdict at the gate (cheap, and "REJECT → demote to standard" is a valid verdict), while an under-classified structural decision entering as a standard slips through ordinary PR review and evades the gate entirely. Misclassification cost is asymmetric, so the tie-break is too. Same direction everywhere: unsure if mechanizable → treat as not (a prose rule that later moves to lint is fine; a hallucinated lint rule is not); unsure if durable → treat as durable.

Calibration examples worth baking in as few-shots: "use Pydantic v2" → ADR (selection + contamination); "validators sit below the fields they validate" → standard; "ban `.dict()`" → lint (`TID251`); "extend the core vulnerability model rather than compose" → ADR (selection + reversal cost); "the optional `cvss_vector` field is set only for imported findings" → Q2 fail → concept doc; "how to run migrations locally" → Q2 fail → reference.

Two wiring notes. First, this triage procedure is itself agent-facing content, so it needs a projection home — it belongs at the front of `new-adr.prompt.md` (replacing the current qualification gate) or as a small shared `rule-triage` block both the ADR prompt and a future standards prompt include; a decision procedure that lives only in `docs/reference/` is the concept-doc trap again. Second, the output contract should force the evidence into the artifact: an ADR candidate must carry its Q4 trigger + evidence verbatim, and a standards PR should state "Q4 checked: no triggers" in its description — which gives your review prompt (open thread 5) something mechanical to verify rather than re-deriving the classification.

Want me to fold this into the registry doc as a section, or draft it as the standalone triage prompt block?