# CLI Reference

The `agent-collab` command is implemented with Typer in `src/agent_collab/cli.py`. The console script is registered in `pyproject.toml`:

```toml
[project.scripts]
agent-collab = "agent_collab.cli:main"
```

## Command Surface

```bash
agent-collab --help
agent-collab <command> --help
```

All commands accept `--root /path/to/repo` when they need to target a repository other than the current working directory.

Most commands also accept `--force`. Without `--force`, existing files are skipped instead of overwritten.

## Commands

| Command | Function | Output |
| --- | --- | --- |
| `init` | `coordination.command_init` | `.agent/README.md`, `.agent/status.json`, and standard directories |
| `new-task` | `coordination.command_new_task` | `.agent/tasks/<task-key>.md` |
| `handoff` | `coordination.command_handoff` | `.agent/handoffs/<task-key>-<role>-<timestamp>.md` |
| `adr` | `coordination.command_adr` | `.agent/decisions/ADR-<number>-<slug>.md` |
| `review` | `coordination.command_review` | `.agent/reviews/<task-key>-review-<timestamp>.md` |
| `test-report` | `coordination.command_test_report` | `.agent/test-reports/<task-key>-test-report-<timestamp>.md` |
| `conflict` | `coordination.command_conflict` | `.agent/risks/<task-key>-conflict-<slug>.md` |
| `merge-recommendation` | `coordination.command_merge_recommendation` | `.agent/reviews/<task-key>-merge-recommendation-<timestamp>.md` |
| `file-ownership` | `coordination.command_file_ownership` | `.agent/protocols/file-ownership-<task-key>.md` |
| `human-decision` | `coordination.command_human_decision` | `.agent/risks/<task-key>-human-decision-<slug>.md` |

## Shared Options

### `--root`, `-r`

Target repository root. Defaults to the current git root if available, otherwise the current working directory.

```bash
agent-collab init --root /path/to/repo
```

### `--force`, `-f`

Overwrite existing generated files. Use carefully, because `.agent/` files are meant to become filled-in coordination records.

```bash
agent-collab new-task --id TASK-001 --title "Demo" --force
```

## Enums

Typer validates several option groups with string enums.

### Risk

Used by `new-task`, `merge-recommendation`, and `human-decision`.

```txt
low
medium
high
```

### Handoff Status

Used by `handoff`.

```txt
completed
partially_completed
blocked
needs_review
needs_tests
```

### Review Status

Used by `review`.

```txt
approved
changes_requested
blocked
needs_human_decision
```

### Review Recommendation

Used by `review`.

```txt
approve
request_changes
split_task
abandon
escalate
```

### Test Recommendation

Used by `test-report`.

```txt
merge_ready
needs_fix
needs_more_tests
needs_human_decision
```

### Conflict Type

Used by `conflict`.

```txt
semantic
textual
architectural
dependency
test
unknown
```

### Merge Recommendation

Used by `merge-recommendation`.

```txt
merge
do_not_merge
needs_changes
needs_human_decision
```

### Yes/No

Used by `conflict --requires-human` and `merge-recommendation --human-approval-required`.

```txt
yes
no
```

## Command Details

### `init`

Creates the standard `.agent/` workspace.

```bash
agent-collab init \
  --project demo \
  --active-task TASK-001-demo \
  --phase implementation \
  --protected-branches main,production
```

Defaults:

| Option | Default |
| --- | --- |
| `--project` | repository directory name |
| `--active-task` | `None` |
| `--phase` | `planning` |
| `--protected-branches` | `main,master,production,staging` |

Generated `status.json` includes:

- project;
- active task;
- current phase;
- protected branches;
- empty agent assignment map;
- merge status with default blockers.

### `new-task`

Creates a task definition.

```bash
agent-collab new-task \
  --id TASK-001 \
  --title "Refactor API client" \
  --owner coordinator \
  --status planned \
  --risk medium \
  --check lint \
  --check tests
```

Important behavior:

- `--id` and `--title` are required.
- `--check` can be repeated.
- If no checks are passed, defaults are `lint`, `typecheck`, `unit tests`, and `build`.
- The task key is normalized from ID and title.

### `handoff`

Creates a timestamped handoff.

```bash
agent-collab handoff \
  --task TASK-001-refactor-api-client \
  --role implementer \
  --branch agent/impl/TASK-001-refactor-api-client \
  --worktree ../repo-implementer \
  --status needs_review \
  --next-agent reviewer
```

Required options:

- `--task`
- `--role`
- `--branch`
- `--worktree`

### `adr`

Creates an architecture decision record.

```bash
agent-collab adr --number 1 --title "Use Server-Side API Wrapper"
```

The ADR number is zero-padded in the file name:

```txt
ADR-001-use-server-side-api-wrapper.md
```

### `review`

Creates a review template.

```bash
agent-collab review \
  --task TASK-001-refactor-api-client \
  --branch agent/impl/TASK-001-refactor-api-client \
  --reviewer reviewer \
  --status changes_requested \
  --recommendation request_changes
```

Default status is `blocked` and default recommendation is `request_changes`. This conservative default prevents an empty generated review from reading as approval.

### `test-report`

Creates a verification report.

```bash
agent-collab test-report \
  --task TASK-001-refactor-api-client \
  --branch agent/impl/TASK-001-refactor-api-client \
  --tester tester \
  --recommendation needs_more_tests
```

Default recommendation is `needs_more_tests`, because generated reports should be filled with real evidence before becoming merge support.

### `conflict`

Creates a conflict or blocker note.

```bash
agent-collab conflict \
  --task TASK-001-refactor-api-client \
  --title "API Client and Auth Boundary" \
  --type architectural \
  --requires-human yes
```

### `file-ownership`

Creates a file ownership map.

```bash
agent-collab file-ownership --task TASK-001-refactor-api-client
```

Use this before parallel implementation when agents may otherwise edit overlapping files.

### `human-decision`

Creates a human decision request.

```bash
agent-collab human-decision \
  --task TASK-001-refactor-api-client \
  --title "Choose Auth Boundary" \
  --risk high
```

### `merge-recommendation`

Creates final merge guidance.

```bash
agent-collab merge-recommendation \
  --task TASK-001-refactor-api-client \
  --recommendation needs_human_decision \
  --risk high \
  --human-approval-required yes
```

Default recommendation is `needs_changes`. Default human approval requirement is `yes`.

## Design Notes

- CLI command functions are intentionally thin wrappers.
- Business rules and file generation live in `coordination.py`.
- `SimpleNamespace` is used as a lightweight adapter between Typer parameters and coordination functions.
- Typer enum validation is tested in `tests/test_cli.py`.
- All command names use kebab-case on the command line, matching Typer's default conversion from Python function names.
