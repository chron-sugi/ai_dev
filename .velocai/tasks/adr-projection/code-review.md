# Code review — adr-projection

Status: **APPROVED**
Scope reviewed: commits `75455bd^..c61eb39` on `dev` (9 commits).
Reviewer: reviewer role, 2026-07-23. Cycle 1 of 3.

## Verifications re-run (not trusted from report)

| Command | Result |
| --- | --- |
| `py -3 -m pytest -q` | 37 passed |
| `py -3 -m ruff check .` | All checks passed (repo-wide) |
| `just project-check` | exit 0; `22 ADRs read, 18 rules projected`; `excluded ADR-0013` reported; `drift: 0` |
| `just project` x2 | idempotent — `written: 0, deleted: 0, unchanged: 16`; generated dirs show clean `git status` |
| `just --list` | `project` and `project-check` present |

## Acceptance criteria — all met

1. Twice-run zero diff — confirmed live (0 written / 0 deleted; clean status). `emit.apply` writes only on byte difference.
2. Every accepted/proposed ADR with a domain projects to exactly one Copilot + one Claude file with per-line `(ADR-NNNN)` citation — confirmed in outputs; `render._body` emits `- {rule} ({id})`.
3. `applyTo` string set == `paths` list set == sorted/deduped scope union — `render.glob_union` sorted+deduped; dialect-equivalence test `test_dialects_share_identical_body_and_glob_set`; verified in `adr-pipeline` outputs.
4. Rule edit updates both files in place; notice-less files untouched — `test_update_in_place_when_rule_changes`, `test_hand_authored_file_survives_sweep`.
5. Removing a domain's last projectable ADR deletes both files, notice-gated — `test_orphaned_generated_file_is_deleted`, `_orphans` gates on exact `GENERATED_NOTICE`.
6. `project-check` non-zero on drift, zero clean — `test_check_detects_hand_edit_and_orphan`, `test_end_to_end_generate_update_delete`.
7. pytest + ruff pass; stdlib-only — asserted mechanically by `test_projection_package_is_stdlib_only` (ast walk vs `sys.stdlib_module_names`).

## Key judgment calls — all sound

1. **ADR-0013 RESEARCH.md exclusion.** Correct and reported. ADR-0013 (proposed, `scope: **/RESEARCH.md`, `projection: instructions`) passes the status+channel filter, then `model._references_research_md` excludes it with reason; `__main__` prints `excluded ADR-0013: ...` (seen in live `project-check`). This mechanically enforces ADR-0014's rule ("never add RESEARCH.md to any projection output or instruction glob"). The generator never reads/cites the RESEARCH.md file itself — it only globs `docs/adrs/adr-*.md` — so ADR-0013's boundary is respected. Test: `test_research_md_scope_is_excluded_per_adr_0014`.
2. **Include set accepted+proposed** — `model.INCLUDE_STATUSES`; superseded/deprecated excluded (`test_superseded_and_deprecated_are_excluded`). Matches OQ-1.
3. **`.gitattributes` LF pin + justfile var move** — sound. Generated paths pinned `text eol=lf` so `core.autocrlf` cannot manufacture drift against the byte-comparing guard. Moving `windows-shell`/`python` into the framework justfile is correct: `project`/`project-check` are framework recipes (not project-specific), so the framework justfile is their correct home; the ADR-0011 boundary protects consumer repos, and this repo is the framework. Mirrored byte-identically into the deploy-source template `src/templates/task-runner/justfile`.
4. **Byte-determinism** — sorted orders throughout (`glob_union`, `build_outputs` domain sort, `_orphans` sort, records sorted by id, universal sorted); `write_bytes` with `\n`; no timestamps in any output. `check` is a pure recompute-and-diff.

## Non-blocking findings

- `emit.py:97-99` (`merge_copilot_shared`): when there are no universal rules **and** an existing `.github/copilot-instructions.md` has no sentinels, the branch `merged = text... + [""] + block_lines` appends an empty sentinel pair to a previously sentinel-less hand-authored file. Unreachable in the current corpus (universal rules ADR-0003/0004/0012 always exist) and harmless (marks the region), but slightly surprising. Consider skipping the append when `block` is the empty sentinel pair. Not required for approval.
- Terminology: the plan/report call ADR-0014's rule "accepted"; it is `status: proposed` (operative under OQ-1). No code impact.
- Deploy note (out of scope): the template justfile now ships `project`/`project-check` to consumer repos; how the `src/app/projection` module reaches consumers is not defined by this task. Track as a follow-up, not a defect here.
- `test_projection_package_is_stdlib_only` / real-corpus tests use cwd-relative paths (`Path("src/app/projection")`, `Path("docs/adrs")`); works from repo root as configured, mildly fragile.

## Deviations (disclosed, accepted)

`.gitattributes` addition; shell/`python` var relocation to framework justfile; four pre-existing T201 `print` fixes in `install_claude_assets.py` (converted to `sys.stdout/stderr.write` + docstrings) to keep the repo-wide ruff-clean criterion. All reviewed and sound.

## Verdict

APPROVED. No blocking findings. Non-blocking items above may be handled as fast-follows at the coder's discretion.
