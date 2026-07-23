



As of **July 19, 2026**, there is a defined **file envelope** for VS Code `*.instructions.md` files, but there is **no required universal set of Markdown sections**.

The emerging accepted practice is:

> Standardize the metadata and writing style across instruction files, but let each file’s body reflect its specific concern.

## 1. Canonical file format

Store workspace files under:

```text
.github/instructions/
  python.instructions.md
  api.instructions.md
  testing.instructions.md
  frontend/
    react.instructions.md
```

VS Code searches `.github/instructions` recursively, so organizing files by language, module, team, or concern is supported. citeturn730893view0

A strong canonical format is:

```markdown
---
name: "Python Testing"
description: "Use when creating, modifying, or reviewing Python unit and integration tests."
applyTo: "tests/**/*.py,**/test_*.py,**/*_test.py"
---

# Python Testing

## Rules

- Use pytest fixtures for reusable setup.
- Test externally observable behavior rather than implementation details.
- Keep tests deterministic and independent.
- Name tests using `test_<behavior>_<condition>_<expected_result>`.

## Preferred patterns

```python
def test_create_user_with_duplicate_email_returns_conflict() -> None:
    ...
```

## Avoid

- Do not depend on test execution order.
- Do not use production network services in unit tests.
- Do not mock the unit under test.

## Validation

- Run `pytest tests/path/to/changed_tests.py`.
- Run the relevant package test suite before completing the change.

## References

- [Testing architecture](../../docs/testing.md)
```

The technically supported frontmatter fields are:

| Field | Status | Purpose |
|---|---|---|
| `name` | Optional | Display name; defaults to the filename |
| `description` | Optional in the public schema, strongly recommended | Explains the concern and helps VS Code discover task-relevant instructions |
| `applyTo` | Optional | Glob patterns for automatic file-based application |

The remainder is ordinary Markdown. citeturn730893view0turn730893view1

## 2. Treat `description` as effectively required

There is a small inconsistency in the current documentation:

- The public format table says `description` is optional.
- The current VS Code source guidance describes it as required for on-demand discovery.
- VS Code also states that instruction selection can use semantic matching between the description and the current task. citeturn730893view0turn550003view3

Therefore, the practical rule should be:

> Every `*.instructions.md` file should have a keyword-rich `description`, even when it has an `applyTo`.

Good:

```yaml
description: "Use when creating database migrations, changing schemas, or modifying persisted data. Covers compatibility, rollback, and deployment safety."
```

Weak:

```yaml
description: "Database guidelines."
```

The description should answer:

1. When should this file be loaded?
2. What concern does it govern?
3. What important topics does it contain?

For deterministic routing, still include `applyTo`. Do not rely exclusively on semantic description matching.

## 3. Recommended frontmatter convention

For consistency, I would standardize all repository instruction files on:

```yaml
---
name: "<Human-readable topic>"
description: "<Use when... trigger plus concise scope>"
applyTo: "<glob or comma-separated globs>"
---
```

Use a quoted, comma-separated string for multiple patterns:

```yaml
applyTo: "**/*.ts,**/*.tsx"
```

Current VS Code source guidance also shows YAML arrays as accepted:

```yaml
applyTo:
  - "src/**"
  - "lib/**"
```

However, GitHub’s cross-surface documentation consistently demonstrates the comma-separated form. The quoted string is therefore the conservative format when files may also be consumed by Copilot code review, the cloud agent, or Copilot CLI. citeturn550003view4turn550003view7

Avoid this except for genuinely universal instructions:

```yaml
applyTo: "**"
```

A targeted instruction with `applyTo: "**"` becomes effectively always-on, wastes context, and can incorrectly influence unrelated work. Current VS Code guidance explicitly identifies overly broad `applyTo` values as an anti-pattern. citeturn550003view4

## 4. What sections should it contain?

There is no mandatory section schema. For most files, use only the sections that add useful information.

### Recommended default

```markdown
# <Concern>

## Rules

## Preferred patterns

## Avoid

## Validation

## References
```

### What each section does

**Title**

Use one H1 that names the governed concern:

```markdown
# FastAPI Endpoint Design
```

It should not repeat “Instructions” or “Guidelines” unnecessarily if the filename and name already establish that.

**Rules**

This is the core section. Use concise, imperative, independently testable statements:

```markdown
- Return domain models from the service layer.
- Convert domain failures to HTTP responses only in the API layer.
- Use dependency injection for authentication and database sessions.
```

**Preferred patterns**

Include only when a compact code example communicates the convention better than prose. VS Code recommends concrete preferred/avoided examples because models respond more reliably to examples than abstract descriptions. citeturn550003view2

**Avoid**

Use this for locally plausible patterns that are nevertheless prohibited:

```markdown
- Do not raise `HTTPException` from repositories or services.
- Do not instantiate database sessions inside endpoint functions.
```

This is generally more valuable than listing generic coding mistakes.

**Validation**

Include this when the concern has a deterministic completion check:

```markdown
## Validation

- Run `pytest tests/api`.
- Run `ruff check src tests`.
- Run `pyright`.
```

Do not turn this into a complete implementation workflow. Include only the checks relevant to files covered by this instruction.

**References**

Link to authoritative repository documents instead of copying them:

```markdown
## References

- [API architecture](../../docs/architecture/api.md)

```

VS Code supports Markdown links in instruction files and recommends referencing rather than duplicating shared information. citeturn550003view0turn550003view2

## 5. What belongs in `*.instructions.md`?

A scoped instruction file should contain **durable, non-obvious constraints that should influence work on matching files**.

Good candidates include:

- Language- or framework-specific conventions
- Module or package boundaries
- Approved architectural patterns
- Required error-handling behavior
- Security constraints specific to a technology or directory
- Testing conventions
- Serialization and API contract rules
- Persistence and migration safety rules
- Documentation style for a particular documentation tree
- Preferred and prohibited local patterns
- Relevant validation commands

VS Code explicitly positions these files for frontend/backend differences, language rules, framework patterns, tests, documentation, and rules for specific portions of a codebase. citeturn550003view0turn369847view0

The best test is:

> Would an agent working on a matching file repeatedly benefit from this instruction, and is the rule not reliably inferable from the code or tooling?

VS Code recommends focusing on information that the AI cannot easily infer, such as non-default conventions, architectural adrs, and environmental constraints. citeturn369847view1

## 6. What should not be in `*.instructions.md`?

### Repository-wide context

Do not repeat universal project information in every scoped file:

- Overall project purpose
- Global architecture summary
- Universal naming rules
- Universal security policy
- General contribution requirements

These belong in `.github/copilot-instructions.md`, `AGENTS.md`, or referenced architecture/contribution documents. Scoped files should contain only the delta for their concern. VS Code combines applicable instruction files and does not guarantee their ordering, so duplicated or conflicting rules create ambiguity. citeturn550003view0

### Agent roles or personas

Do not put this in a Python instruction file:

```markdown
You are a senior Python architect.
First explore the repository, then create a plan.
Ask the reviewer agent to validate your changes.
```

Role, behavior, tool permissions, handoffs, and specialist responsibilities belong in a custom `.agent.md` file. Custom instructions define standards; custom agents define specialized roles and workflows. citeturn419561view4turn419561view6

### Reusable task prompts

Do not include:

```markdown
When asked to create an endpoint:
1. Gather requirements.
2. Create an implementation plan.
3. Implement the endpoint.
4. Summarize the changes.
```

That is a reusable task invocation and belongs in a `.prompt.md` file. Prompt files are explicitly designed for manually invoked tasks such as scaffolding, fixing tests, or preparing pull requests. citeturn419561view5

### Complex workflows and supporting resources

Do not turn an instruction file into:

- A deployment procedure
- A migration playbook
- A debugging decision tree
- A multi-stage implementation methodology
- A collection of scripts and examples
- A specialized capability package

Those increasingly belong in an Agent Skill. Skills can contain instructions, scripts, examples, and supporting resources; `*.instructions.md` files are intended to contain instructions only. citeturn419561view4

### Linter-enforced trivia

Avoid spending tokens on rules already enforced deterministically:

```markdown
- Use four spaces.
- End files with a newline.
- Sort imports according to Ruff.
- Use double quotes because Black formats strings that way.
```

VS Code specifically recommends skipping conventions already enforced by linters and formatters. citeturn550003view2

Instead, mention the validation mechanism only when useful:

```markdown
- Do not manually reformat code against Ruff or Black output.
- Run `ruff check --fix` and `ruff format` after modifying Python files.
```

### Duplicated documentation

Do not copy substantial parts of:

- `README.md`
- `ARCHITECTURE.md`
- ADRs
- API documentation
- Security standards
- Contribution guides

Link to the relevant section and state the behavioral implication. Duplicating documentation is one of the explicit VS Code anti-patterns because copies drift and consume context. citeturn550003view4

### Temporary project state

Avoid:

```markdown
- The authentication refactor is currently 70% complete.
- John is working on the database layer this week.
- Do not touch endpoint X until the next release.
- The current branch is expected to merge Friday.
```

These details decay quickly and should live in plans, issues, session handoffs, or work tracking—not persistent instructions.

### Aspirational or vague commands

Avoid:

```markdown
- Write high-quality code.
- Follow best practices.
- Be accurate.
- Make the code maintainable.
- Consider security.
- Do not introduce bugs.
```

They provide no decision rule. GitHub’s guidance similarly identifies vague quality-improvement instructions as ineffective. citeturn369847view0

### Secrets or environment-specific credentials

Never include passwords, tokens, internal secrets, personal paths, or credentials. Also avoid machine-specific instructions unless the file is intentionally user-level and excluded from version control.

## 7. Should all `*.instructions.md` files use the same layout?

**Use the same metadata contract and editorial principles, but not necessarily the same headings.**

Standardize:

- Frontmatter field order
- Description style
- Glob syntax style
- Imperative rule wording
- Heading depth
- `Preferred` versus `Avoid` terminology
- Reference format
- Validation format
- One concern per file

Do not require every file to contain empty boilerplate sections.

For example, a terminology file might need only:

```markdown
# Domain Terminology

## Canonical terms

## Deprecated terms
```

A migration file might need:

```markdown
# Database Migrations

## Compatibility rules

## Rollback requirements

## Prohibited operations

## Validation
```

A React file might need:

```markdown
# React Components

## Component boundaries

## State ownership

## Accessibility

## Preferred patterns
```

Forcing all three into identical sections would make the files longer and less precise.

The current VS Code authoring guidance recommends **one concern per file**, concise actionable content, and brief examples instead of long explanations. It explicitly discourages mixing testing, API design, and styling in a single file. citeturn550003view4

## Recommended project standard

I would adopt this rule for your framework:

```markdown
Every workspace `*.instructions.md` file MUST:

1. Reside under `.github/instructions/`.
2. Include `name`, `description`, and `applyTo` frontmatter.
3. Govern one durable, clearly named concern.
4. Use concise imperative rules.
5. State prohibited patterns when they are locally plausible.
6. Include examples only when they disambiguate a rule.
7. Include validation only when specific to the governed concern.
8. Link to authoritative documentation instead of duplicating it.
9. Exclude personas, task workflows, transient state, and linter-enforced trivia.
10. Avoid `applyTo: "**"` unless the instruction is genuinely universal.
```

The most useful conceptual model is:

- **`copilot-instructions.md` / root `AGENTS.md`**: global project context and invariants
- **`*.instructions.md`**: scoped engineering policy
- **`.prompt.md`**: manually invoked task
- **`.agent.md`**: role, behavior, tools, and handoffs
- **`SKILL.md`**: specialized workflow or capability with supporting resources

That separation matches the current VS Code customization model and prevents `*.instructions.md` files from becoming miniature agents or duplicated documentation repositories. citeturn369847view2turn419561view4turn419561view5turn419561view6