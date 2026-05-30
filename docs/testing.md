# Testing

Agent Collab currently uses unit tests for the Python package and a skill metadata validator for the skill package.

## Test Stack

Runtime:

- Python `>=3.9`
- `pytest`
- `typer.testing.CliRunner`

Configuration lives in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

## Running Tests

Install development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run tests:

```bash
python3 -m pytest
```

If using the repository virtual environment:

```bash
.venv/bin/python -m pytest
```

Avoid relying on a globally installed `pytest` executable if it is not running from the same interpreter that has project dependencies installed.

## Test Files

```txt
tests/
  test_cli.py
  test_coordination.py
```

## Coordination Tests

`tests/test_coordination.py` calls `coordination.py` functions directly.

Coverage areas:

- `slugify`;
- `normalize_task_key`;
- `display_task_id`;
- `split_csv`;
- empty task ID rejection;
- explicit root resolution;
- `write_new` skip and force behavior;
- `.agent/` directory initialization;
- `status.json` contents;
- task file generation;
- handoff generation;
- ADR generation;
- review generation;
- test report generation;
- conflict generation;
- merge recommendation generation;
- file ownership generation;
- human decision generation.

The tests monkeypatch `today()` and `timestamp()` to make generated paths deterministic:

```python
monkeypatch.setattr(coordination, "today", lambda: "2026-05-30")
monkeypatch.setattr(coordination, "timestamp", lambda: "2026-05-30-1200")
```

Use this pattern for new timestamped artifacts.

## CLI Tests

`tests/test_cli.py` exercises the Typer command surface through `CliRunner`.

Coverage areas:

- help output lists all commands;
- `init` writes status and protected branches;
- `new-task` writes task checks and owner;
- every artifact command creates the expected file;
- invalid enum values fail;
- module entry point exists;
- `cli.main` is callable.

This ensures CLI wiring does not drift from the coordination engine.

## Skill Validation

Use the skill validator available in your environment:

```bash
python3 /path/to/quick_validate.py .
```

The validator should confirm:

- skill frontmatter exists;
- skill metadata is valid;
- package shape matches expected skill layout.

## Smoke Tests

Use a temp directory to verify installed CLI behavior:

```bash
tmpdir="$(mktemp -d)"
agent-collab init --root "$tmpdir" --project demo
agent-collab new-task --root "$tmpdir" --id TASK-001 --title "Demo Task"
agent-collab handoff \
  --root "$tmpdir" \
  --task TASK-001-demo-task \
  --role implementer \
  --branch agent/impl/TASK-001-demo-task \
  --worktree ../repo-implementer
find "$tmpdir/.agent" -maxdepth 3 -type f | sort
rm -rf "$tmpdir"
```

This catches packaging or console-script issues that unit tests may miss.

## What To Test When Adding Features

### New Helper Function

Add direct unit tests in `tests/test_coordination.py`.

Test:

- normal input;
- edge input;
- invalid input;
- path or slug formatting.

### New Artifact Command

Add tests in both files:

- direct generator test in `test_coordination.py`;
- CLI command test in `test_cli.py`;
- help list assertion if a new command is added.

Also test:

- generated path;
- key generated content;
- enum validation if new enums are added;
- `force` behavior if overwrite behavior changes.

### New CLI Option

Update or add CLI tests that:

- pass the option;
- assert generated content changed as expected;
- assert invalid enum or required-option behavior when applicable.

### Template Change

Update tests only for stable, meaningful content. Avoid tests that assert every line of a template; they make docs and wording changes expensive. Prefer checking:

- heading exists;
- important option value appears;
- file path is correct;
- required section exists.

## Current Gaps

The project does not currently have:

- CI configuration;
- packaging build tests;
- documentation linting;
- markdown link checking;
- property-based tests for task key normalization;
- integration tests against an installed wheel.

These can be added later if the project grows.
