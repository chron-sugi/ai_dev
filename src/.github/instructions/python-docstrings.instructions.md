---
applyTo: "**/*.py"
---

# Docstrings (ADR-0001)

- Every module, class, function, and method gets a Google-style docstring — **including private/underscore-prefixed members**. CI gates on 100% coverage via `interrogate`; Ruff enforces format.
- Docstrings state **why and contract**: intent, invariants, side effects, `Raises:`, units. Never restate the signature ("Gets the user" on `get_user` is a defect).
- One-liners are fine for simple helpers: `"""Deduplicate hooks by path, keeping first occurrence."""`
- Pydantic models and dataclasses: document fields with `Field(description=...)`, not comments. Descriptions project into JSON Schema and tool schemas.
- Follow the exemplar in `docs/golden/documented_module.py`. Do not remove or hollow out existing docstrings when editing a function.
