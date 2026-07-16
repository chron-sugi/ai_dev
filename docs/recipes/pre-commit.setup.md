# Setup Guide: pre-commit + import-linter + dependency-cruiser + eslint-plugin-project-structure

> **Audience:** an AI coding agent executing this setup in a repository.
> **Contract:** complete each phase in order. Every phase ends with a **Verify** step — do not proceed until it passes. If a Verify step fails twice after remediation attempts, stop and report the failure to the human instead of working around it.
> **Do not** edit files under `scripts/hooks/**`, `.github/hooks/**`, or any file this guide marks as a gate, beyond what the guide specifies. If a gate fails, fix the code — never the gate.

---

## Phase 0 — Detect repository shape

Gather these facts before writing any config. Record answers; later phases substitute them.

1. `PY_ROOT` — the Python root package name (directory under `src/` or repo root containing `__init__.py`). Example: `myapp`.
2. `PY_LAYOUT` — `src` layout (`src/myapp/...`) or flat (`myapp/...`).
3. `PY_TOOL` — dependency manager: detect `uv.lock` (uv), `poetry.lock` (poetry), else pip.
4. `FE_DIR` — frontend root: directory containing `package.json` with React/TS deps. May be repo root or e.g. `frontend/`.
5. `FE_PM` — package manager: detect `pnpm-lock.yaml`, `yarn.lock`, or `package-lock.json`.
6. `TS_CONFIG` — path to the tsconfig that defines path aliases (often `tsconfig.json` or `tsconfig.app.json`).
7. Confirm ESLint flat config vs legacy: presence of `eslint.config.js|mjs|ts` (flat) vs `.eslintrc.*` (legacy).

**Verify:** echo all seven values. All must be resolved (no "unknown"). If the repo has no Python or no frontend, skip the corresponding phases and note the omission in the final report.

---

## Phase 1 — pre-commit framework

1. Install: `uv tool install pre-commit` (or `pipx install pre-commit`, or add as dev dependency via `PY_TOOL`).
2. Create `.pre-commit-config.yaml` at repo root:

```yaml
# Gate file: agents must not modify without human approval.
minimum_pre_commit_version: "3.5.0"
default_install_hook_types: [pre-commit, pre-push]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
```

3. Run `pre-commit autoupdate` to pin current revs, then `pre-commit install`.

**Verify:** `pre-commit run --all-files` exits 0 (or reports only pre-existing issues — if so, list them but continue). `git config core.hooksPath` must be empty or compatible; if a custom hooksPath exists, stop and report (it conflicts with pre-commit's installer).

---

## Phase 2 — import-linter (Python architecture contracts)

1. Add dev dependency: `import-linter` (e.g. `uv add --dev import-linter`).
2. Append to `pyproject.toml`, substituting `PY_ROOT`. Adjust the layer list to the packages that actually exist — inspect `src/PY_ROOT/` first and include only real packages:

```toml
[tool.importlinter]
root_package = "PY_ROOT"

[[tool.importlinter.contracts]]
name = "Features are independent"
type = "independence"
modules = ["PY_ROOT.features.*"]

[[tool.importlinter.contracts]]
name = "Layer direction: features -> core -> shared"
type = "layers"
layers = ["PY_ROOT.features", "PY_ROOT.core", "PY_ROOT.shared"]

[[tool.importlinter.contracts]]
name = "Shared imports nothing internal"
type = "forbidden"
source_modules = ["PY_ROOT.shared"]
forbidden_modules = ["PY_ROOT.features", "PY_ROOT.core"]
```

3. Run `lint-imports`.
4. **If violations exist:** do NOT refactor code in this task. Snapshot each violation as an `ignore_imports` entry under the relevant contract, with a `# BASELINE: burn down` comment above the block. New violations are now gated; existing ones are tracked debt.

**Verify:** `lint-imports` exits 0. Then run a probe: add a temporary illegal import (one feature importing another), confirm `lint-imports` exits non-zero and names the contract, then revert the probe. Both outcomes are required.

---

## Phase 3 — dependency-cruiser (frontend, defaults + resolver correctness)

Scope note: install the scaffold defaults only. Custom FSD boundary rules are a separate, deferred task — do not author them now.

1. In `FE_DIR`: install dev dependency `dependency-cruiser` via `FE_PM`.
2. Run `npx depcruise --init` — accept the self-contained `.dependency-cruiser.cjs` config.
3. Resolver correctness (this is the critical step — misresolution silently disables the tool):
   - In the generated config's `options`, set `tsConfig: { fileName: "TS_CONFIG" }`.
   - Ensure `doNotFollow: { path: "node_modules" }` is present.
   - If the repo uses path aliases (`@/`, `~/`), confirm they resolve (checked in Verify).
4. Add a package.json script: `"depcruise": "depcruise src --config .dependency-cruiser.cjs"`.

**Verify (two probes, both required):**
- Run the script; it exits 0 or reports only genuine pre-existing issues (baseline them with `--ignore-known` if noisy: `depcruise src --output-type baseline > .dependency-cruiser-known-violations.json`, then add `knownViolations` support per docs).
- Resolution probe: pick one real aliased import in the codebase; run `npx depcruise --output-type json src | grep` for the *resolved* target path. If the alias appears unresolved (`"couldNotResolve": true`), fix `tsConfig`/resolver options before proceeding. Do not continue with a config that cannot resolve aliases.

---

## Phase 4 — eslint-plugin-project-structure (co-located tests + slice isolation)

1. In `FE_DIR`: install dev dependency `eslint-plugin-project-structure` via `FE_PM`.
2. Flat config example (adapt paths to the real slice layout found in Phase 0; shown for `src/features/*`, `src/entities/*`, `src/shared/*`):

```js
// eslint.config.mjs (merge into existing config — do not clobber other plugins)
import { projectStructurePlugin, createIndependentModules } from "eslint-plugin-project-structure";

export default [
  // ...existing config entries...
  {
    plugins: { "project-structure": projectStructurePlugin },
    rules: {
      "project-structure/independent-modules": ["error", createIndependentModules({
        modules: [
          { name: "Shared", pattern: "src/shared/**",
            allowImportsFrom: ["src/shared/**"] },
          { name: "Entities", pattern: "src/entities/**",
            allowImportsFrom: ["src/entities/*/**", "src/shared/**"],
            errorMessage: "Entities may import only from within the same entity or shared." },
          { name: "Features", pattern: "src/features/**",
            allowImportsFrom: ["src/features/*/**", "src/entities/**", "src/shared/**"],
            errorMessage: "A feature may import only from itself, entities, or shared. Cross-feature imports are forbidden (ADR: feature independence)." },
        ],
      })],
    },
  },
];
```

3. Co-located tests via the `folder-structure` rule: enforce that component files have sibling tests. Configure `project-structure/folder-structure` so `*.tsx` component files in slice `ui/` segments require a matching `*.test.tsx` sibling (see plugin docs for the `folderStructure` schema; keep the rule scoped to `src/**` and exclude `shared/ui` only if the human confirms).
4. Error messages: keep them instructional and addressed to the agent/reader, as in the examples — they are part of the enforcement design, not decoration.

**Verify:** `eslint .` (or the repo's lint script) runs with the new rules active and exits 0 (baseline any pre-existing violations with inline disables marked `// BASELINE: burn down` — count and report them). Probe: create a temporary cross-feature import, confirm ESLint errors with the custom message, revert.

---

## Phase 5 — wire everything into pre-commit

Append to `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: import-linter
        name: import-linter (architecture contracts)
        entry: lint-imports
        language: system
        pass_filenames: false
        files: \.py$

      - id: depcruise
        name: dependency-cruiser (frontend dependency rules)
        entry: bash -c 'cd FE_DIR && npx depcruise src --config .dependency-cruiser.cjs --output-type err-long'
        language: system
        pass_filenames: false
        files: \.(ts|tsx|js|jsx)$

      - id: eslint
        name: eslint (incl. project-structure)
        entry: bash -c 'cd FE_DIR && npx eslint --max-warnings 0'
        language: system
        files: \.(ts|tsx|js|jsx)$
```

Notes:
- `language: system` + repo-local tools keeps versions pinned by the lockfiles (single source of truth), not by pre-commit's isolated environments — one less drift surface.
- `pass_filenames: false` for the two architecture tools: contracts are whole-graph properties; per-file runs give false confidence.
- Keep these hooks fast. If depcruise exceeds ~3s on this repo, move it to the `pre-push` stage: add `stages: [pre-push]`.

**Verify:** `pre-commit run --all-files` exits 0. Then run one end-to-end probe: introduce a cross-feature Python import, attempt `git commit`, confirm the commit is blocked with the import-linter contract named in output, revert. Repeat once for a frontend cross-feature import.

---

## Phase 6 — guardrails and closeout

1. **Gate integrity:** confirm `.pre-commit-config.yaml`, `.dependency-cruiser.cjs`, the `[tool.importlinter]` block, and the project-structure ESLint config are covered by the repo's agent auto-approval exclusion list (same class as `scripts/hooks/**`). If the exclusion mechanism doesn't yet cover them, report this as a required human action — do not proceed to modify approval settings yourself.
2. **CI backstop:** confirm CI runs `pre-commit run --all-files` (or the identical underlying commands). Client hooks are skippable (`--no-verify`); CI is the mechanism. If absent, report as required follow-up.
3. **Report:** summarize per phase — tools installed with versions, contracts/rules active, baseline violation counts snapshotted, probes passed, and any items deferred to humans (custom depcruise FSD rules, folder-structure fine-tuning, CI wiring).

## Failure protocol

At any point: if a gate blocks you, the correct fixes are (in order) fix the code, baseline with an explicit marker, or stop and ask. Editing gate configs to pass, using `--no-verify`, or disabling rules without a `BASELINE` marker are prohibited outcomes of this task.