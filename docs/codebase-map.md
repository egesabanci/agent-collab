# Codebase Map

This document explains every major file and directory in the repository and how each piece contributes to Agent Collab.

## Root Files

| Path | Purpose |
| --- | --- |
| `README.md` | Public project overview, installation, quick start, workflow summary, CLI table, and links into deeper docs. |
| `LICENSE` | MIT license text. |
| `pyproject.toml` | Build system, package metadata, dependency declarations, console script entry point, package discovery, and pytest configuration. |
| `SKILL.md` | Portable agent-facing skill instructions. This is the main entry point for compatible agent runtimes. |

## Package Metadata

`pyproject.toml` defines the installable package:

- Build backend: `hatchling.build`
- Distribution name: `agent-collab`
- Python requirement: `>=3.9`
- Runtime dependency: `typer>=0.12.0`
- Development extra: `pytest>=8.0`
- Console script: `agent-collab = agent_collab.cli:main`
- Wheel package root: `src/agent_collab`
- Pytest paths: `tests`, with `src` on `pythonpath`

The package version is currently duplicated in:

- `pyproject.toml`
- `src/agent_collab/__init__.py`

When releasing a new version, update both unless the project later moves to a single-source versioning strategy.

## Source Package

```txt
src/
  agent_collab/
    __init__.py
    __main__.py
    cli.py
    coordination.py
```

### `src/agent_collab/__init__.py`

Defines package metadata:

- module docstring
- `__version__`

There are currently no public Python APIs exported from this file beyond the version value.

### `src/agent_collab/__main__.py`

Allows module execution:

```bash
python -m agent_collab
```

It imports `main` from `agent_collab.cli` and calls it under the standard `if __name__ == "__main__"` guard.

### `src/agent_collab/cli.py`

Defines the Typer command line interface. Responsibilities:

- declare enum values accepted by CLI options;
- define `agent-collab` commands;
- convert `Path | None` root values into the string format expected by the coordination engine;
- translate Typer command arguments into `SimpleNamespace` objects;
- call the corresponding `coordination.command_*` function;
- expose `main()` for the console script.

The CLI layer intentionally contains little business logic. It is a typed command surface over the coordination engine.

### `src/agent_collab/coordination.py`

Creates `.agent/` directories and artifact files. Responsibilities:

- normalize task identifiers;
- resolve repository roots;
- create the `.agent/` directory tree;
- write files idempotently by default;
- render Markdown templates for tasks, handoffs, ADRs, reviews, test reports, conflicts, file ownership maps, human decisions, and merge recommendations.

This module is the core implementation layer.

## Agent Skill Layer

```txt
SKILL.md
agents/
  openai.yaml
references/
  artifacts-and-templates.md
  quality-review-testing-merge.md
  role-playbooks.md
  security-and-escalation.md
  worktree-and-branch-protocol.md
```

### `SKILL.md`

Contains the concise operating instructions for agents. It includes:

- frontmatter name and description;
- core rules;
- standard workflow;
- coordination file structure;
- worktree protocol summary;
- role selection table;
- quality gate;
- security and escalation summary.

It links to the reference files for detailed guidance.

### `agents/openai.yaml`

Optional runtime metadata for platforms that understand catalog metadata:

- display name;
- short description;
- default prompt.

This file is not required for CLI operation.

### `references/`

Detailed protocol playbooks. These are intentionally separate from `SKILL.md` so the skill entry point stays short while the full protocol remains available.

| File | Covers |
| --- | --- |
| `artifacts-and-templates.md` | `.agent/` source-of-truth priority, artifact directories, required fields, and template guidance. |
| `quality-review-testing-merge.md` | coding standards, review requirements, testing, commit rules, PR rules, merge readiness, and quality bar. |
| `role-playbooks.md` | coordinator, architect, implementer, reviewer, tester, documentation, and integration role playbooks. |
| `security-and-escalation.md` | high-risk areas, secrets handling, database/API/runtime rules, failure handling, and escalation template. |
| `worktree-and-branch-protocol.md` | worktree layout, protected branches, branch naming, startup checks, ownership, syncing, and parallelization rules. |

## Tests

```txt
tests/
  test_cli.py
  test_coordination.py
```

### `tests/test_coordination.py`

Tests the implementation layer directly:

- string helper behavior;
- empty task ID rejection;
- explicit root resolution;
- write-once behavior with `force`;
- `.agent/` initialization;
- task file generation;
- all artifact generator outputs with deterministic dates and timestamps.

### `tests/test_cli.py`

Tests the command surface through `typer.testing.CliRunner`:

- help output includes all commands;
- init and new-task write expected files;
- every artifact command creates expected files;
- invalid enum values are rejected;
- module entry point file exists and `cli.main` is callable.

## Assets

```txt
assets/
  agent-collab-banner.png
```

The tracked banner image is used at the top of `README.md`.

Keep generated visual assets small enough for a source repository and prefer stable names so README links do not churn.

## Build Outputs

The following are ignored and should not be committed:

- `.venv/`
- `.pytest_cache/`
- `dist/`
- `build/`
- `*.egg-info/`
- `tmp/`
- Python bytecode caches

The repository may contain local generated outputs while developing, but release commits should only include intentional source, tests, docs, and assets.
