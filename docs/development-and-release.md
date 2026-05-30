# Development And Release

This document explains how to work on Agent Collab locally and how to prepare package releases.

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the package with development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Verify the CLI is available:

```bash
agent-collab --help
python -m agent_collab --help
```

## Development Commands

Run tests:

```bash
python3 -m pytest
```

Compile source files:

```bash
python3 -B -m py_compile src/agent_collab/*.py
```

Validate the skill:

```bash
python3 /path/to/quick_validate.py .
```

Smoke-test artifact generation:

```bash
tmpdir="$(mktemp -d)"
agent-collab init --root "$tmpdir" --project demo
agent-collab new-task --root "$tmpdir" --id TASK-001 --title "Demo Task"
find "$tmpdir/.agent" -maxdepth 2 -type f | sort
rm -rf "$tmpdir"
```

## Code Style

Current style is intentionally simple:

- standard library first;
- small helper functions;
- Typer commands as thin adapters;
- implementation logic in `coordination.py`;
- tests that assert behavior, paths, and stable template sections;
- no hidden network or service dependencies.

When changing code, follow the existing pattern before introducing abstractions.

## Adding A New Command

1. Add a `command_<name>` function to `src/agent_collab/coordination.py`.
2. Render the artifact in a deterministic path.
3. Use `ensure_agent_dirs`.
4. Use `write_new` for conservative writes.
5. Add a Typer command in `src/agent_collab/cli.py`.
6. Add enums only when accepted values should be constrained.
7. Add direct coordination tests.
8. Add CLI tests.
9. Update `docs/cli.md`.
10. Update `docs/artifact-model.md`.
11. Update `SKILL.md` or `references/` if the user-facing protocol changed.

## Versioning

Current version locations:

- `pyproject.toml`
- `src/agent_collab/__init__.py`

Before release, update both values consistently.

The project currently uses a simple manual versioning flow. If release automation is added later, prefer a single source of truth.

## Building

Install build tools:

```bash
python3 -m pip install build twine
```

Clean old build artifacts:

```bash
rm -rf dist build *.egg-info
```

Build source distribution and wheel:

```bash
python3 -m build
```

Check distributions:

```bash
python3 -m twine check dist/*
```

Inspect outputs:

```bash
ls -lh dist
```

## Publishing

Use PyPI trusted publishing or an API token. Do not commit tokens and do not document local secret file paths in repository docs.

Upload:

```bash
python3 -m twine upload dist/*
```

After publishing, verify:

```bash
python3 -m pip install --upgrade agent-collab
agent-collab --help
```

For a clean smoke test, use a temporary virtual environment:

```bash
tmpdir="$(mktemp -d)"
python3 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install agent-collab
"$tmpdir/venv/bin/agent-collab" --help
rm -rf "$tmpdir"
```

## Release Checklist

Before tagging or publishing:

- version updated in `pyproject.toml`;
- version updated in `src/agent_collab/__init__.py`;
- `README.md` still matches install and usage behavior;
- `docs/` matches CLI behavior and artifact names;
- `SKILL.md` and `references/` match protocol behavior;
- tests pass;
- skill validation passes;
- wheel and source distribution build;
- `twine check` passes;
- smoke test passes from a clean install;
- release commit uses a conventional commit message.

## Conventional Commits

The repository has been using conventional commit messages:

```txt
feat: add installable Typer CLI
test: add CLI and coordination coverage
docs: refresh README and banner
```

Use:

- `feat:` for user-facing capabilities;
- `fix:` for bug fixes;
- `docs:` for documentation-only changes;
- `test:` for tests;
- `chore:` for maintenance;
- `refactor:` for internal restructuring without behavior change.

## Git Hygiene

Before committing:

```bash
git status --short
git diff --stat
git diff
```

Do not commit unrelated generated files. Common ignored outputs include:

- `.venv/`;
- `.pytest_cache/`;
- `dist/`;
- `build/`;
- `*.egg-info/`;
- `tmp/`;
- `__pycache__/`.

## Documentation Maintenance

When changing public behavior:

- update root `README.md` for user-facing quick-start changes;
- update `docs/` for implementation and maintenance details;
- update `SKILL.md` for agent-facing rule changes;
- update `references/` for detailed protocol changes;
- update tests if generated output changed.
