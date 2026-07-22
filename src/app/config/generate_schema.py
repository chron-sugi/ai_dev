"""Generate or verify the committed domain-contract JSON Schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .domain_contract import domain_contract_json_schema

DEFAULT_SCHEMA_PATH = (
    Path(__file__).with_name("schemas") / "domain-contract.schema.json"
)


def rendered_schema() -> str:
    """Render the canonical schema deterministically."""

    return json.dumps(domain_contract_json_schema(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    """Write the schema or return nonzero when the committed copy drifted."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args()
    expected = rendered_schema()
    if args.check:
        if (
            not args.output.exists()
            or args.output.read_text(encoding="utf-8") != expected
        ):
            sys.stderr.write(f"domain contract schema is stale: {args.output}\n")
            return 1
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
