# AGENTS.md

velocai — a framework for ADR-driven agentic development. Architecture decisions
live in `docs/adrs/` as ADRs with machine-consumed frontmatter (`id`, `status`,
`rule`) and are projected into tool-facing surfaces (instruction files, lint
config, hooks); per-domain contracts in `docs/domains/<domain>/CONTRACT.yaml`
drive scaffolding. Python 3.11+ (pydantic, PyYAML), `just` as the command
surface. Application code is in `src/app/`; agent-facing assets (prompts,
instructions, templates) are in `src/assets/` and `src/templates/`.

## Commands

Invoke Python explicitly as `py -3` on Windows, `python3` on POSIX — never an
unqualified `python` (ADR-0012 pins the invocation form).

- Test: `py -3 -m pytest -q`
- Single test file: `py -3 -m pytest tests/config/test_domain_contract.py -q`
- Lint: `py -3 -m ruff check .`
- Schema drift check (set `PYTHONPATH=src` first; module form only — direct
  script invocation fails on relative imports):
  `py -3 -m app.config.generate_schema --check` (drop `--check` to regenerate)
- Pipeline operations: discover via `just --list`; run pipeline steps only
  through just recipes, never by invoking pipeline scripts directly (ADR-0008)

## Boundaries

🚫 NEVER:

- Read, write, cite, or create any file named `RESEARCH.md` — human-only
  document class (ADR-0013). A finding that must reach agents graduates to an ADR.
- Modify an ADR with `status: accepted`. Accepted ADRs are immutable; to change
  a decision, create a new ADR that supersedes it.
- Hand-edit a generated instruction file or sentinel-marked region; change the
  source ADR and re-run projection (ADR-0006).
- Add Node/`.mjs` scripts or a PowerShell peer; all framework scripting is
  stdlib-only Python 3, because hooks must run from a bare interpreter with no
  install step (ADR-0012).
- Add recipes to the framework-owned `justfile` — it is overwritten on every
  framework deploy; project recipes go in `justfile.local` (ADR-0011).
- Create a `CONSTITUTION.md` or any monolithic hand-edited rules file; each
  durable rule is its own ADR in `docs/adrs/` (ADR-0004).
- Commit secrets.

⚠️ ASK first: adding dependencies; deleting or renumbering ADRs; changing the
domain-contract schema or projection frontmatter schema.

✅ ALWAYS: run the test suite and `ruff check` before declaring work done.

## Repo-specific knowledge

- Ephemeral agent artifacts and app-supplied files go only under `.velocai/`
  (ADR-0010).
- Domain docs live only in `docs/domains/<domain>/` — `CONCEPT.md` (durable
  knowledge) plus `CONTRACT.yaml` (the current executable contract,
  ADR-0009/ADR-0017). The committed JSON Schema must match the pydantic
  models — the drift check above proves it.
- ADR frontmatter `rule:` fields are projection sources consumed by machines;
  write them as single atomic, imperative statements.

## Pointers

- Architecture decisions: `docs/adrs/`
- Current-state configuration registry (`backend.md`, `frontend.md`,
  `architecture.md`): `docs/reference/` — registry entries, not ADRs (ADR-0002)
- Authoring templates: `docs/domains/_contract_template.yaml`,
  `docs/domains/_concept_template.md`
