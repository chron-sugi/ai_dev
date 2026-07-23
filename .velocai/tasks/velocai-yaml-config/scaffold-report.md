# Scaffold report — configuration domain (STOPPED, nothing written)

## Contract

- Path: `docs/domains/configuration/CONTRACT.yaml`
- Domain: `configuration`
- Approval: human / dbroo / 2026-07-23T15:00:19Z
- Rules: R-001..R-003 (ADR-0015), R-004 (ADR-0016), R-005 (ADR-0022)
- Provenance: ADR-0015, ADR-0016, ADR-0022

## Backend

Derivation completed; generation NOT started (see Deviations).

| Module | Decision | Basis |
|---|---|---|
| `errors.py` | CREATE | always (rung 0) — hosts `SettingsValidationError` |
| `models.py` | CREATE | always (rung 1) — hosts `VelocaiSettings`, `ResolvedConfig` |
| `tables.py` + `store.py` | OMIT | no `backend.persistence` |
| `service.py` | OMIT | no `backend.service` |
| `config.py` | OMIT | no `backend.config` |
| `api/` | OMIT | no `http.backend` |
| `jobs.py` | OMIT | no `backend.jobs` |
| `testing.py` | OMIT | no `backend.testing` |

## Enforcement

Not performed — see stop condition 2.

## Deviations

Stopped without writing any file. Two stop conditions:

1. **Contract gap — public functions have no host module.**
   `backend.public_api` declares functions `load_settings` and
   `resolve_config`, but the contract activates no module that may contain
   behavior: `service.py` requires `backend.service`, `store.py` requires
   `backend.persistence`, and `models.py`/`errors.py` are vocabulary-only
   rungs. Placing the functions is a design decision absent from the YAML
   ("completing the scaffold would require a decision not present in the
   YAML"). Per protocol the contract returns to its author: the natural
   revision adds a `backend.service` block with operations `load_settings`
   and `resolve_config` (matching the declared signatures), which activates
   `service.py` as their home and requires re-approval.

2. **Missing assumed infrastructure — import-linter.**
   The domain prompt assumes import-linter wired into pre-commit and CI.
   The repo has no `[tool.importlinter]` in `pyproject.toml`, no
   `import-linter` dependency, and no pre-commit config. The privacy and
   rung-order contracts cannot be added or observed failing ("an enforcement
   contract cannot be observed failing" / missing infrastructure). Adding
   the dependency is an ASK-first action (AGENTS.md).

## Open items

- Revise the contract with `backend.service` (author + re-approve), or
  decide an alternative host for the two functions by ADR.
- Decide whether to add `import-linter` (dev dependency + `[tool.importlinter]`
  + wiring) or scaffold without enforcement contracts this run and record
  the debt.
