---
id: ADR-0022
title: Concrete velocai.yaml settings schema and config package public API
status: accepted
date: 2026-07-23
domain: configuration
scope: "velocai.yaml,src/app/config/**"
rule: "Parse velocai.yaml only into the validated VelocaiSettings model exposed by the src/app/config package."
projection: instructions
---

## Context

Accepted ADR-0015 establishes the repository-root `velocai.yaml` as the sole
user-facing configuration interface and names its setting categories —
application identity, overwrite behavior, orphan cleanup, and the default
dry-run mode — without deciding exact key names, value types, or defaults.
Approved ADR-0016 assigns ownership of built-in synchronization targets and
configuration composition to the public `src/app/config` package API without
naming its operations. Drafting the configuration domain contract surfaced
both deferrals as unresolved gaps: a contract cannot declare a settings model
or a public API that no ADR has decided. The current public values live in the
legacy `config/app.yaml` `options:` block (`overwrite: true`,
`clean_orphans: false`, `dry_run_default: true`) and are the migration source
ADR-0015's consequences require.

## Decision

`velocai.yaml` contains exactly two top-level mappings, `app` and `sync`,
with these keys, types, and defaults:

| Key                  | Type | Default     |
| -------------------- | ---- | ----------- |
| `app.name`           | str  | `"velocai"` |
| `sync.overwrite`     | bool | `true`      |
| `sync.clean_orphans` | bool | `false`     |
| `sync.dry_run_default` | bool | `true`    |

Every key is optional and carries its default, so a missing `velocai.yaml`
yields a fully valid configuration; unknown keys and invalid value types are
validation errors, not warnings. The `sync.*` defaults migrate the legacy
`config/app.yaml` `options:` values unchanged.

The `src/app/config` package exposes this public API and nothing else for
user configuration:

- model `VelocaiSettings` — fields `app_name: str`, `overwrite: bool`,
  `clean_orphans: bool`, `dry_run_default: bool`, each with the default above
- model `ResolvedConfig` — fields `settings: VelocaiSettings`,
  `source_root: str` (built-in, `"src/assets"`), and `targets`, the built-in
  synchronization target definitions whose shape stays internal per ADR-0016
- error `SettingsValidationError` — raised when `velocai.yaml` contains
  unknown keys or invalid values
- function `load_settings(path: str | None = None) -> VelocaiSettings` —
  parse and validate `velocai.yaml`, returning defaults when the file is absent
- function `resolve_config(settings: VelocaiSettings | None = None) ->
  ResolvedConfig` — combine user settings with the built-in target definitions

`source_root` and the target definitions are application behavior, not user
settings, and never appear in `velocai.yaml`.

## Rejected Alternatives

- **Flat top-level keys with no `app`/`sync` grouping** — mixes identity and
  synchronization behavior at one level and leaves no stable place for the
  additional user-facing settings ADR-0015 anticipates.
- **Carrying over the legacy `options:` block name** — `options` describes
  nothing; `sync` names the behavior the settings govern.
- **Making the keys required** — forces boilerplate into every consuming
  repository when safe defaults exist for all four values.
- **Exposing the settings as environment-variable tunables** — creates a
  second configuration surface beside the one ADR-0015 fixed as sole
  interface.
- **Publishing the resolved target shape as part of the public API** — turns
  ADR-0016's internal target definitions into a de facto public schema.

## Consequences

The configuration domain contract can declare a complete settings model,
public API, and validation invariant with this ADR as provenance. The
`src/app/config` package must implement `VelocaiSettings` validation with
these defaults, and migrating means deleting the `options:` block from
`config/app.yaml` once consumers read `velocai.yaml`. Growing the user
schema later means a new ADR adding keys under `app` or `sync`; renaming or
removing a key supersedes this one.
