from __future__ import annotations

import argparse
import subprocess
import sys


ALLOWED_SCHEMAS = [
    "bkchoi21",
    "go23",
    "hgpark05",
    "hyungjin_moon",
    "jbyun",
    "jsbyeon",
    "junnyunk",
    "kcjang7",
    "mcolors",
    "namss",
    "seulki",
    "spjeong",
    "spy28",
]


def run_alembic(schema: str, *args: str) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "alembic",
        "-c",
        "alembic.ini",
        "-x",
        f"schema={schema}",
        *args,
    ]
    return subprocess.run(command, cwd="backend", text=True, capture_output=True, check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply Alembic revisions to education schemas.")
    parser.add_argument(
        "--schemas",
        nargs="*",
        default=ALLOWED_SCHEMAS,
        help="Target schemas. Defaults to all 13 education schemas.",
    )
    parser.add_argument(
        "--revision",
        default="head",
        help="Alembic revision target. Defaults to head.",
    )
    return parser.parse_args()


def validate_schemas(schemas: list[str]) -> None:
    invalid = [schema for schema in schemas if schema not in ALLOWED_SCHEMAS or schema == "public"]
    if invalid:
        raise SystemExit(f"Invalid target schemas: {', '.join(invalid)}")


def main() -> int:
    args = parse_args()
    validate_schemas(args.schemas)

    succeeded: list[str] = []

    for schema in args.schemas:
        current = run_alembic(schema, "current")
        if current.returncode != 0:
            print(f"[{schema}] current revision lookup failed")
            print(current.stderr.strip())
            return 1

        current_revision = current.stdout.strip() or "base"
        print(f"[{schema}] current={current_revision} target={args.revision}")

        upgraded = run_alembic(schema, "upgrade", args.revision)
        if upgraded.returncode != 0:
            print(f"[{schema}] migration failed")
            if upgraded.stdout.strip():
                print(upgraded.stdout.strip())
            if upgraded.stderr.strip():
                print(upgraded.stderr.strip())
            print(f"successful={succeeded}")
            remaining = [item for item in args.schemas if item not in succeeded and item != schema]
            print(f"failed={schema}")
            print(f"not_run={remaining}")
            return 1

        print(f"[{schema}] PASS")
        succeeded.append(schema)

    print(f"all_successful={succeeded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
