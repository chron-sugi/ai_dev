---
id: ADR-0015
title: Repository-root velocai.yaml as the user configuration interface
status: accepted
date: 2026-07-22
domain: configuration
scope: "velocai.yaml,config/**,src/**"
rule: "Expose user-adjustable application settings only through the repository-root velocai.yaml file."
projection: instructions
---

## Context

VelocAI needs one discoverable, human-editable configuration interface that works in repositories containing Python backends, React frontends, or both. The current `config/app.yaml` name reads as an internal implementation detail and does not establish a stable public contract. Users need to set application identity and synchronization behavior, including overwrite, orphan cleanup, and dry-run defaults, without editing framework code.

## Decision

The repository-root `velocai.yaml` file is the sole user-facing VelocAI configuration file. Its schema includes application identity and synchronization options such as app name, overwrite behavior, orphan cleanup, and the default dry-run mode, and it may grow with additional user-facing settings while internal runtime state remains outside this file.

## Rejected Alternatives

- **Keep `config/app.yaml` as the public file** — its generic name and nested location make ownership and discovery ambiguous in consuming repositories.
- **Use JSON** — it is broadly interoperable but lacks comments and is unnecessarily noisy for a configuration file maintained directly by people.
- **Use TOML** — it is strong for Python-centric tooling but is less natural for the nested target mappings VelocAI already uses and requires separate parsing support in Node-based tooling.
- **Use INI** — it cannot represent nested mappings, lists, and per-target configuration without ad hoc encoding conventions.
- **Split settings between backend and frontend configuration files** — it creates competing sources of truth for repository-wide synchronization behavior.

## Consequences

Users gain one predictable configuration entry point with comments and readable nested settings, regardless of repository stack. VelocAI must define and validate the `velocai.yaml` schema, migrate the current public values from `config/app.yaml`, and keep generated or machine-local state out of the file. Python and Node consumers require YAML parsing support, and any React code must receive only explicitly exported non-secret values rather than loading the repository configuration into the browser bundle.
