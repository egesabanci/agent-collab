# Architecture

Agent Collab is a small Python package plus a portable agent skill. Its architecture is intentionally direct: the CLI receives user intent, the coordination engine writes deterministic Markdown/JSON artifacts, and agent runtimes consume the skill protocol.

## High-Level Model

```txt
human / agent / automation
        |
        v
agent-collab CLI
        |
        v
coordination engine
        |
        v
target repository .agent/ workspace
        |
        v
agents, reviewers, testers, and integrators read/write durable artifacts
```

The package does not run agents, manage background workers, inspect pull requests, or merge code. It creates a shared coordination surface that other agents and humans can use safely.

## Main Boundaries

| Boundary | Files | Responsibility |
| --- | --- | --- |
| Command surface | `src/agent_collab/cli.py` | Parse and validate command-line input with Typer. |
| Artifact generation | `src/agent_collab/coordination.py` | Resolve roots, normalize names, create directories, and write templates. |
| Agent instructions | `SKILL.md`, `references/` | Tell agents how to coordinate, review, test, escalate, and hand off work. |
| Package metadata | `pyproject.toml`, `src/agent_collab/__init__.py` | Define installability, dependencies, scripts, and version. |
| Verification | `tests/` | Assert behavior for helpers, commands, and artifact outputs. |

## Data Flow

### CLI Invocation

Example:

```bash
agent-collab new-task \
  --id TASK-001 \
  --title "Refactor API client" \
  --owner coordinator \
  --risk medium
```

Flow:

1. Typer routes the command to `cli.new_task`.
2. Enum options are validated by Typer.
3. `Path | None` root input is converted with `_root`.
4. CLI values are packed into a `SimpleNamespace`.
5. `coordination.command_new_task` receives the namespace.
6. The coordination engine resolves the repository root.
7. The `.agent/` directory tree is created if missing.
8. The task key is normalized from ID and title.
9. Markdown content is rendered.
10. `write_new` writes the file or skips it if it already exists and `--force` was not passed.

### Repository Root Resolution

`coordination.repo_root` follows this order:

1. If `--root` is provided, expand and resolve that path.
2. Otherwise, run `git rev-parse --show-toplevel`.
3. If git root detection fails, use the current working directory.

This allows commands to work both inside a git repository and against explicit target directories used in tests or automation.

### Write Semantics

`coordination.write_new` is conservative:

- Existing files are skipped by default.
- Existing files are overwritten only when `force=True`.
- Parent directories are created as needed.
- Content is written as UTF-8 text.
- The function prints `[write]` or `[skip]` messages for CLI visibility.

This is important because `.agent/` files are human-editable records. Regenerating templates should not silently destroy completed handoffs, reviews, or decisions.

## Runtime-Agnostic Skill Design

The skill layer avoids tying the protocol to one agent runtime. `SKILL.md` describes behavior that any capable coding agent can follow:

- use worktrees;
- avoid protected branches;
- write durable `.agent/` state;
- create handoffs, reviews, and test reports;
- escalate high-risk decisions;
- do not claim checks passed unless they were run.

`agents/openai.yaml` is optional metadata, not a hard dependency.

## Why Markdown And JSON

The `.agent/` workspace uses Markdown for human-readable artifacts and JSON for machine-readable repository status.

Markdown is used because:

- agents can write it reliably;
- humans can review it in diffs and pull requests;
- templates can include code fences, checklists, tables, and instructions;
- it does not require a database or service.

JSON is used for `status.json` because:

- it can be updated by tools;
- active task, phase, protected branch list, and merge status are structured;
- it is easy to inspect in tests and automation.

## Non-Goals

Agent Collab intentionally does not provide:

- an agent scheduler;
- a distributed lock service;
- a merge bot;
- CI execution;
- GitHub API automation;
- conflict resolution algorithms;
- secret scanning;
- runtime-specific orchestration.

Those can be layered on top later. The current project focuses on a portable protocol and repeatable artifact generation.

## Extension Points

Future extensions should fit one of these seams:

- **New artifact type**: add a `command_*` function in `coordination.py`, expose it in `cli.py`, add tests, update docs and references.
- **New CLI option**: update Typer option definitions, pass the value through `SimpleNamespace`, update template rendering and tests.
- **New role guidance**: update `references/role-playbooks.md` and, if core enough, summarize it in `SKILL.md`.
- **New quality rule**: update `references/quality-review-testing-merge.md`, tests if generated output changes, and docs if command behavior changes.
- **New runtime metadata**: add or update files under `agents/`, keeping the skill itself runtime-neutral.

## Failure Modes To Preserve Against

The architecture exists to prevent common multi-agent failures:

- agents editing the same working directory;
- hidden chat state becoming the only handoff;
- completed work being overwritten by template regeneration;
- reviewers inspecting final files without the diff context;
- testers lacking branch or environment details;
- high-risk changes reaching merge without human approval;
- integration happening without review and verification evidence.
