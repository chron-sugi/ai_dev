---
id: ADR-0016
title: Built-in synchronization targets owned by the config package API
status: accepted
date: 2026-07-22
domain: configuration
scope: "src/app/config/**,velocai.yaml,config/app.yaml"
rule: "Define built-in synchronization targets only through the public src/app/config package API."
projection: instructions
---

## Context

The current `config/app.yaml` mixes user-controlled options with VelocAI-owned synchronization target definitions, including tool-specific destinations and filename transformations. Those targets describe supported application behavior rather than repository preferences, so exposing them as ordinary user configuration permits unsupported combinations and makes every consumer interpret the same internal schema. Accepted ADR-0015 establishes `velocai.yaml` as the sole user-facing configuration interface, requiring a separate owner for application defaults and configuration composition.

## Decision

The `src/app/config` package owns the built-in synchronization target definitions as source code and exposes the public package API for loading user values and producing resolved application configuration. `velocai.yaml` contains user-adjustable values only; callers do not read target definitions from it or from the legacy `config/app.yaml` file.

## Rejected Alternatives

- **Keep targets in `velocai.yaml`** — application-supported destinations and transforms would appear user-editable, allowing invalid combinations and turning internal behavior into a permanent public schema.
- **Retain `config/app.yaml` as a second configuration file** — it creates two configuration authorities and forces runtime code to distinguish public settings from an internal YAML document.
- **Package the targets as a separate YAML resource** — it preserves a runtime parsing and packaging dependency without providing user customization or a stronger API boundary.
- **Define target constants in the CLI or synchronization module** — it couples configuration knowledge to one caller and leaves other consumers without a stable configuration API.

## Consequences

Built-in targets become versioned, testable application behavior, while `velocai.yaml` remains a smaller and safer user contract. The new package must validate user settings, combine them with built-in target definitions, and expose resolved configuration without leaking mutable internal registries. Migrating requires removing `targets` from `config/app.yaml`, adding package-level tests, and updating every consumer to depend on `src/app/config` rather than parsing target definitions directly.
