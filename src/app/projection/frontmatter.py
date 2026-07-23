"""Frontmatter extraction and validation for ADR source records.

Implements a strict subset-YAML parser for the frontmatter forms the ADR corpus
actually uses (plain/quoted scalars, flow lists, block lists). The corpus is
machine-authored via ``/write-adr``, so anything outside the subset is treated
as an authoring error and fails loudly with the offending filename rather than
being guessed at (ADR-0012 forbids a PyYAML dependency here: projection must
run from a bare interpreter).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: Frontmatter keys the parser accepts; anything else is an authoring error.
KNOWN_KEYS = frozenset(
    {"id", "title", "status", "date", "domain", "projection", "scope", "rule", "supersedes"}
)

#: Keys that must be present in every ADR frontmatter block.
REQUIRED_KEYS = frozenset({"id", "title", "status", "domain", "projection", "scope", "rule"})

#: The ADR lifecycle states the pipeline recognises.
VALID_STATUSES = frozenset({"accepted", "proposed", "superseded", "deprecated"})

#: Channel spellings found in the corpus, normalised to canonical channel names.
_CHANNEL_ALIASES = {
    "instructions": "instructions",
    "instruction-files": "instructions",
    "lint": "lint",
    "hooks": "hooks",
    "ci": "ci",
}

#: Config-file basenames that identify a legacy path-form projection entry as
#: the lint channel (ADR-0001's accepted, immutable frontmatter form).
_LINT_CONFIG_BASENAMES = frozenset({"pyproject.toml", "ruff.toml"})

_ID_RE = re.compile(r"^ADR-\d{4}$")
_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(.*)$")


class FrontmatterError(ValueError):
    """A frontmatter block is missing, malformed, or outside the supported subset."""


@dataclass(frozen=True)
class AdrRecord:
    """One validated ADR frontmatter record, normalised for projection.

    ``scope`` and ``projection`` are always tuples regardless of the authored
    form; ``projection`` holds canonical channel names only. ``date`` is kept
    as an opaque string — it is not a projection input and accepted ADRs are
    immutable, so a malformed date must not block the pipeline.
    """

    id: str
    title: str
    status: str
    date: str
    domain: str
    scope: tuple[str, ...]
    rule: str
    projection: tuple[str, ...]
    path: Path
    supersedes: str | None = None


def _fail(path: Path, message: str) -> FrontmatterError:
    """Build a FrontmatterError that always names the offending file."""

    return FrontmatterError(f"{path.name}: {message}")


def _strip_quotes(value: str) -> str:
    """Remove one matching pair of surrounding single or double quotes, if any."""

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _parse_block(lines: list[str], path: Path) -> dict[str, str | list[str]]:
    """Parse frontmatter lines into raw scalar-or-list values, fail-loud.

    Supports exactly: ``key: scalar``, ``key: [a, b]`` flow lists, and
    ``key:`` followed by indented ``- item`` block-list entries.
    """

    raw: dict[str, str | list[str]] = {}
    current_list: list[str] | None = None
    for line in lines:
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            if current_list is None:
                raise _fail(path, f"list item outside a block list: {line.strip()!r}")
            current_list.append(_strip_quotes(line.lstrip()[2:].strip()))
            continue
        match = _KEY_RE.match(line)
        if match is None:
            raise _fail(path, f"unparseable frontmatter line: {line.strip()!r}")
        key, rest = match.group(1), match.group(2).strip()
        if key in raw:
            raise _fail(path, f"duplicate frontmatter key: {key!r}")
        if key not in KNOWN_KEYS:
            raise _fail(path, f"unknown frontmatter key: {key!r}")
        if rest == "":
            current_list = []
            raw[key] = current_list
            continue
        current_list = None
        if rest.startswith("[") and rest.endswith("]"):
            raw[key] = [_strip_quotes(item.strip()) for item in rest[1:-1].split(",") if item.strip()]
        else:
            raw[key] = _strip_quotes(rest)
    return raw


def _normalize_scope(value: str | list[str], path: Path) -> tuple[str, ...]:
    """Normalise scope to a tuple of glob tokens; strings are comma-split."""

    items = value.split(",") if isinstance(value, str) else list(value)
    globs = tuple(item.strip() for item in items if item.strip())
    if not globs:
        raise _fail(path, "scope resolved to an empty glob list")
    return globs


def _channel_for_path_entry(entry: str, path: Path) -> str:
    """Map one legacy path-form projection entry to its channel by suffix.

    ``*.instructions.md`` targets are the instructions channel; known lint
    config basenames (optionally followed by an annotation) are lint. Anything
    else is an authoring error, never a guess.
    """

    first_token = entry.split()[0]
    if first_token.endswith(".instructions.md"):
        return "instructions"
    basename = first_token.rsplit("/", 1)[-1]
    if basename in _LINT_CONFIG_BASENAMES:
        return "lint"
    raise _fail(path, f"unmappable projection entry: {entry!r}")


def _normalize_projection(value: str | list[str], path: Path) -> tuple[str, ...]:
    """Normalise projection to a sorted tuple of canonical channel names.

    Accepts a channel scalar, a list of channels, or ADR-0001's legacy list of
    target file paths. ``none`` yields the empty tuple and is only valid alone.
    """

    items = [value] if isinstance(value, str) else list(value)
    if not items:
        raise _fail(path, "projection resolved to an empty list")
    if "none" in items:
        if len(items) != 1:
            raise _fail(path, "projection 'none' cannot be combined with channels")
        return ()
    channels = set()
    for item in items:
        if item in _CHANNEL_ALIASES:
            channels.add(_CHANNEL_ALIASES[item])
        else:
            channels.add(_channel_for_path_entry(item, path))
    return tuple(sorted(channels))


def extract_frontmatter_lines(text: str, path: Path) -> list[str]:
    """Return the lines between the leading ``---`` fence pair, fail-loud."""

    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise _fail(path, "no frontmatter fence on first line")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise _fail(path, "frontmatter fence is never closed")


def parse_adr(path: Path) -> AdrRecord:
    """Parse and validate one ADR file into an AdrRecord.

    Raises:
        FrontmatterError: on any missing key, unknown key, invalid id/status/
            domain form, or syntax outside the supported subset. The message
            always names the file.
    """

    raw = _parse_block(extract_frontmatter_lines(path.read_text(encoding="utf-8"), path), path)
    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise _fail(path, f"missing required frontmatter keys: {sorted(missing)}")

    def scalar(key: str) -> str:
        """Fetch a raw value that must be a scalar string."""

        value = raw[key]
        if not isinstance(value, str):
            raise _fail(path, f"expected a scalar for {key!r}")
        return value

    adr_id = scalar("id")
    if not _ID_RE.match(adr_id):
        raise _fail(path, f"invalid id: {adr_id!r}")
    status = scalar("status")
    if status not in VALID_STATUSES:
        raise _fail(path, f"invalid status: {status!r}")
    domain = scalar("domain")
    if not _KEBAB_RE.match(domain):
        raise _fail(path, f"domain is not kebab-case: {domain!r}")
    rule = scalar("rule").strip()
    if not rule:
        raise _fail(path, "rule is empty")
    supersedes = scalar("supersedes") if "supersedes" in raw else None
    return AdrRecord(
        id=adr_id,
        title=scalar("title"),
        status=status,
        date=scalar("date") if "date" in raw else "",
        domain=domain,
        scope=_normalize_scope(raw["scope"], path),
        rule=rule,
        projection=_normalize_projection(raw["projection"], path),
        path=path,
        supersedes=supersedes,
    )
