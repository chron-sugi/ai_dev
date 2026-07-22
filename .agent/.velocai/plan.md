# Plan: justfile-scaffold

status: approved
task-id: justfile-scaffold
source: docs/adrs/adr-0011-split-framework-and-project-justfiles.md (accepted)

## Goal

Create the two-justfile layout defined by ADR-0011 in the repo root, and the deployable template copies in `src/templates/task-runner/`.

## Steps (all mechanical — exact file contents given below)

### Step 1 — Create `justfile` (repo root)

Exact content:

```
# Framework-owned justfile — overwritten on every framework deploy (ADR-0011).
# Do NOT add project-specific recipes here; they belong in justfile.local.

import? 'justfile.local'

# List available recipes
default:
    @just --list
```

Verification: file exists at repo root named exactly `justfile` (no extension) with the content above.

### Step 2 — Create `justfile.local` (repo root)

Exact content:

```
# Project-specific just recipes (ADR-0011).
# This file is never overwritten by a framework deploy. Add project recipes here.
```

Verification: file exists at repo root named exactly `justfile.local` with the content above.

### Step 3 — Create `src/templates/task-runner/justfile`

Exact same content as Step 1.

Verification: file exists at `src/templates/task-runner/justfile`, byte-identical to the repo-root `justfile`.

### Step 4 — Create `src/templates/task-runner/justfile.local`

Exact same content as Step 2.

Verification: file exists at `src/templates/task-runner/justfile.local`, byte-identical to the repo-root `justfile.local`.

### Step 5 — Overall verification

If `just` is on PATH, run `just --list` from the repo root and confirm it exits 0 and lists the `default` recipe. If `just` is not installed, note that in the report and skip.

## Constraints

- Do not touch any other files.
- Do not commit or push.
