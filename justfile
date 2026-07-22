# Framework-owned justfile — overwritten on every framework deploy (ADR-0011).
# Do NOT add project-specific recipes here; they belong in justfile.local.

import? 'justfile.local'

# List available recipes
default:
    @just --list
