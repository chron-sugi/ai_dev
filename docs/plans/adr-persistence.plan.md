# Implementation Plan: ADR-Driven Decision Persistence for AI-Engineered Software

**Target environment:** VS Code + GitHub Copilot (Chat and Agent mode), Git/GitHub-native, no external service dependencies.

**Architecture in one sentence:** ADRs in `docs/adr/` are the single write path for durable adrs; instruction files, golden files, and lint config are generated or derived projections; probe prompts and CI gates verify compliance; a task-closeout distill step feeds new adrs back into the ADR store.

**Evidence anchors used throughout:**

| Finding | Source | Design consequence |
|---|---|---|
| Persistent context lifts decision *compliance* (~46%→95%) but not the code-quality ceiling | dcbench (arXiv 2605.08112); Sandelin pilot | ADRs target compliance and rework reduction; quality investment goes to tests/review |
| ~150–200 instructions before compliance degrades *uniformly* | HumanLayer / QRSPI analysis | Hard token budget on always-loaded context; overflow pushed to glob-scoped files |
| 3–5 relevant/recent records is the near-optimal context window | Gupta et al., EASE 2026 (arXiv 2604.03826) | Progressive disclosure: index always, rules contextually, full ADRs on demand |
| Rules raise adherence to ~70–95%, never 100%; access ≠ binding | arXiv 2606.13174; dcbench | Verification layer is mandatory, not optional |
| ~50% of ADR-adopting repos stall at ≤5 records | Buchgeher et al., IEEE Access 2023 | Lifecycle integration (closeout/distill) and ownership are first-class, not afterthoughts |
| Context files skew toward build/run trivia and rot silently | Agent READMEs study (arXiv 2511.12884) | Instruction files are generated, never hand-authored |

---

## Phase 0 — Baseline and inventory (½ day)

**Goal:** Know what exists before generating anything.

1. Inventory all current decision-bearing artifacts: `docs/adr/`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`, README sections, wiki pages, golden files, lint configs.
2. Classify each statement found as one of: **durable decision** (belongs in an ADR), **mechanizable rule** (belongs in lint/format config), **pattern** (belongs in a golden file), **build/run fact** (stays in instructions, non-decision), or **stale/duplicate** (delete).
3. Record the token count of the current always-loaded surface (`copilot-instructions.md` + any `applyTo: **` files). This is the baseline for the Phase 2 budget.
4. Capture 3–5 known contamination vectors from experience (e.g., Tailwind v3 patterns, rejected libraries resurfacing, string-concatenated class names). These seed the Phase 4 probe suite.

**Exit criteria:** A classification sheet; a measured baseline token cost; a seed list of contamination vectors.

---

## Phase 1 — Canonicalize the ADR store (1–2 days)

**Goal:** `docs/adr/` becomes the authoritative, machine-parseable write path.

1. **Finalize the frontmatter schema.** Required fields:
   - `id` (stable, e.g., `ADR-0007`)
   - `title`
   - `status` (`proposed | accepted | superseded | deprecated`)
   - `date`
   - `supersedes` / `superseded-by` (explicit links; supersession is a first-class operation)
   - `scope` (glob patterns the decision governs — this drives projection targeting)
   - `rule` (one atomic, imperative sentence — the projectable unit)
   - `projection` (which channels this rule compiles to: `instructions | golden-file | lint | none`)
2. **Body structure** (Structured-MADR-adjacent): Context, Decision, **Rejected Alternatives (mandatory, with one-line reasons)**, Consequences. Rejected Alternatives is non-negotiable — it is the direct countermeasure to an agent's statistical prior re-introducing the most common solution.
3. **Migrate existing adrs.** Every durable decision from the Phase 0 inventory gets an ADR. One decision per file. Anything that can't be expressed as a single atomic `rule` is probably two ADRs.
4. **Validation script** (`scripts/adr-lint`): checks frontmatter completeness, unique IDs, valid status transitions, resolvable supersedes links, non-empty rule field, and that `scope` globs parse. Wire into CI and pre-commit.

**Exit criteria:** All durable adrs live as schema-valid ADRs; `adr-lint` passes in CI; no decision reasoning remains hand-authored anywhere else.

---

## Phase 2 — Build the projection pipeline (2–3 days)

**Goal:** Instruction files become compiled output. Humans edit ADRs; a generator edits everything else.

1. **Generator script** (`scripts/project-adrs`, plain Node or Python, repo-native):
   - Reads all `status: accepted` ADRs.
   - Emits `docs/adr/INDEX`: one line per ADR (`id | title | status | rule`). This is the cheap always-loadable map.
   - Emits/updates a fenced, generated block in `.github/copilot-instructions.md` containing: the ADR index reference, the ≤5–7 truly universal rules (those with `scope: **`), and a standing instruction: *"Before modifying files matching an ADR's scope, read the full ADR in docs/adr/. Do not re-litigate adrs with status: accepted; rejected alternatives are listed in each record."*
   - Emits one `.github/instructions/<domain>.instructions.md` per scope cluster, with `applyTo` frontmatter derived from ADR `scope` globs and body content derived from `rule` fields plus a pointer to the source ADR ID.
   - Marks all generated regions with `<!-- generated from docs/adr — do not edit -->` sentinels.
2. **Budget enforcement in the generator:** fail the build if the always-loaded surface exceeds the budget (start at ~2,000 tokens / roughly 200 words of rules; the ~150–200-instruction ceiling is the hard justification). Overflow must be resolved by demoting rules to glob-scoped files or pushing them down the enforcement stack — never by raising the budget silently.
3. **Drift guard:** CI job re-runs the generator and fails on diff (same pattern as generated-code checks). Hand edits to generated files are structurally impossible to merge.
4. **AGENTS.md decision:** either (a) `copilot-instructions.md` delegates to a generated `AGENTS.md` shared across tools, or (b) Copilot-only. Pick one; duplicating rules across both is a documented drift vector. Default recommendation: generate `AGENTS.md` as the shared projection and keep `copilot-instructions.md` to Copilot-specific mechanics only.

**Exit criteria:** Editing an ADR and running the generator updates all projections; CI fails on hand-edited projections or budget overflow.

---

## Phase 3 — Push adrs down the enforcement stack (2–4 days, ongoing)

**Goal:** Every rule lives at the most mechanical layer that can express it. Prose is the last resort.

1. For each ADR, honor its `projection` field:
   - **Lint/format:** anything statically checkable (e.g., `eslint-plugin-better-tailwindcss`, `prettier-plugin-tailwindcss`, import restrictions, banned APIs via `no-restricted-imports`/`no-restricted-syntax`). The ADR remains the record; the lint rule is the enforcement; the instruction file may drop the rule entirely once mechanized (compliance benchmarks show compiled rules outperform prose).
   - **Golden files:** canonical exemplars (e.g., `Button.tsx` with `cva` + `cn()`), referenced by ID from the projected instruction file ("follow the pattern in src/components/Button.tsx, per ADR-0004").
   - **Instructions:** only the residue — the "why," negative rules ("do not reintroduce X"), and pointers.
2. **Protect the machinery:** exclude `scripts/**`, `.github/hooks/**`, `.github/instructions/**`, and `docs/adr/**` from agent auto-approval so an agent cannot self-modify its own constraints or the enforcement layer mid-task.
3. **Track the demotion ratio:** count of rules enforced mechanically vs. by prose. The ratio should rise over time; a stagnant ratio means new adrs are defaulting to the weakest layer.

**Exit criteria:** No rule lives in prose that could live in config; enforcement paths are write-protected from agents; demotion ratio is measured.

---

## Phase 4 — Verification layer (1–2 days to stand up, ongoing to run)

**Goal:** Because access ≠ binding, compliance is measured, not assumed.

1. **Probe suite:** for each contamination vector from Phase 0 (and each new ADR with a plausible failure mode), write a probe prompt that tempts the agent toward the rejected alternative in a scratch file. Run the suite after any change to ADRs, projections, or the enforcement stack. Record pass/fail per ADR ID.
2. **Pre-implementation consistency gate:** before an agent's plan is approved (in the Plan stage of Explore → Plan → Code → Commit), a check — manual or agent-assisted — that the plan does not contradict any `accepted` ADR whose `scope` intersects the touched paths. This is the Spec-Kit-`/analyze` role, implemented repo-natively.
3. **CI as the floor:** everything mechanized in Phase 3 runs in CI; probe results are advisory, lint failures are blocking.
4. **Compliance vs. quality dashboard (lightweight):** track (a) probe pass rate, (b) ADR-contradiction incidents caught in review, (c) defect/rework rate. Interpretation rule, per the evidence: if (a) and (b) are strong but (c) is flat, that is the expected model-bound quality ceiling — invest further effort in tests and review, not more context.

**Exit criteria:** Probe suite runs on demand and after projection changes; plans are gated against ADRs; the three metrics have baselines.

---

## Phase 5 — Lifecycle integration and rot prevention (1 day to wire, permanent to operate)

**Goal:** Beat the Buchgeher abandonment curve. The system must feed itself.

1. **Distill at closeout:** the `/task-closeout` stage (between review and merge) has the agent scan `.agent/<task-id>/` scratch content and propose ADR candidates before the closeout commit deletes it. Human accepts, edits, or rejects each candidate. Location-as-semantics holds: scratch is ephemeral by structure; only distilled adrs cross into `docs/adr/`.
2. **Supersession workflow:** changing a decision means writing a superseding ADR (new ID, `supersedes` link), flipping the old record's status, and re-running the generator — never editing projections. The generator excludes superseded rules automatically, so decision changes propagate mechanically.
3. **Staleness review cadence:** quarterly (or per-milestone) pass over `accepted` ADRs whose `scope` globs no longer match any files, or whose golden files have drifted. A wrong ADR is worse than none — agents follow it faithfully.
4. **Ownership:** the ADR store has a named owner (or CODEOWNERS entry on `docs/adr/**`); ADR changes go through PR review like code.
5. **Push-path protection (already designed, verify in place):** `PreToolUse` hook denying `git push` while `.agent/` is tracked, `SessionEnd` reminder, plain git `pre-push` hook for manual pushes.

**Exit criteria:** Closeout produces ADR candidates on real tasks; a supersession has been exercised end-to-end at least once; review cadence is scheduled.

---

## Rollout sequence and effort

| Phase | Duration | Depends on |
|---|---|---|
| 0 Baseline | ½ day | — |
| 1 ADR store | 1–2 days | 0 |
| 2 Projection | 2–3 days | 1 |
| 3 Enforcement push-down | 2–4 days | 2 (parallelizable per-ADR) |
| 4 Verification | 1–2 days + ongoing | 2 |
| 5 Lifecycle | 1 day + permanent | 2 |

Pilot on one repo (the Tailwind v4 kit repo is the natural candidate — its ADRs, golden files, and lint config already exist and only need wiring into the generator). Expand after one full task cycle including closeout and one exercised supersession.

## Risks and mitigations

- **Generator becomes a bottleneck or is bypassed.** Mitigation: keep it dependency-light, fast, and CI-enforced (drift guard); bypassing is a red CI, not a policy violation.
- **ADR overhead deters capture.** Mitigation: the distill step drafts candidates from scratch content the agent already wrote; human effort is accept/edit/reject, not authoring from scratch. Reserve ADRs for adrs that are expensive to reverse, likely to be second-guessed, or counterintuitive.
- **Token budget pressure as ADR count grows.** Mitigation: budget is on the *always-loaded* surface only; ADR count scales in the on-demand tier. The index line cost (~10–15 tokens/ADR) is the only per-ADR always-on cost, and even that can move behind a pointer if it grows large.
- **False confidence from passing probes.** Mitigation: probes are advisory signals for the context layer; correctness assurance remains with tests, lint, and review, consistent with the quality-ceiling evidence.
- **Evidence base is thin.** The compliance and efficiency benefits are the defensible claims; improved delivered-software quality is not yet demonstrated in controlled studies. Track the Phase 4 metrics to generate local evidence either way.

## Success criteria (90 days)

1. Zero hand-authored decision prose outside `docs/adr/` (drift guard green for 90 days).
2. Always-loaded context within budget; instruction-following complaints not attributable to context overload.
3. Probe pass rate ≥90% across the suite; every failure traced to a layer fix (demotion to lint/golden file) rather than more prose.
4. At least 3 ADRs created via closeout distill and 1 supersession exercised — evidence the log is alive, against the ≤5-record stall pattern.
5. Measured reduction in decision-churn rework (agent-undone adrs caught in review), acknowledging defect rates may be unchanged.
