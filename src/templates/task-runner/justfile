# Framework-owned justfile — overwritten on every framework deploy (ADR-0011).
# Do NOT add project-specific recipes here; they belong in justfile.local.

import? 'justfile.local'

# just defaults to `sh` on Windows, which isn't installed — use PowerShell.
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# ADR-0012: py -3 on Windows, python3 on POSIX — never unqualified `python`.
python := if os_family() == "windows" { "py -3" } else { "python3" }

# Framework code lives under src/; pipeline modules run via -m (ADR-0008).
export PYTHONPATH := "src"

# List available recipes
default:
    @just --list

# Project ADR rules into tool-facing instruction surfaces (ADR-0006, ADR-0007)
project:
    {{python}} -m app.projection

# Drift guard: fail if committed surfaces differ from a fresh projection (ADR-0006)
project-check:
    {{python}} -m app.projection --check
