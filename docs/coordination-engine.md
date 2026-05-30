# Coordination Engine

`src/agent_collab/coordination.py` is the implementation core of Agent Collab. It handles path resolution, task-key normalization, directory creation, conservative file writing, and template rendering.

## Module Responsibilities

The coordination engine is responsible for:

- creating `.agent/` directories;
- writing `status.json`;
- writing Markdown templates;
- normalizing task IDs and file slugs;
- producing predictable file names;
- preserving existing files unless `force=True`;
- keeping template generation independent of Typer.

It is intentionally not responsible for:

- parsing command-line arguments;
- running git commands other than root discovery;
- validating whether branches exist;
- executing tests;
- updating pull requests;
- merging code.

## Constants

### `AGENT_DIRS`

```python
AGENT_DIRS = [
    "tasks",
    "handoffs",
    "decisions",
    "reviews",
    "test-reports",
    "risks",
    "protocols",
    "scratch",
]
```

These are the standard subdirectories created under `.agent/`. Tests assert that `command_init` creates every directory in this list.

## Date Helpers

### `today()`

Returns the local date in `YYYY-MM-DD` format.

Used in:

- handoffs;
- ADRs.

### `timestamp()`

Returns local timestamp in `YYYY-MM-DD-HHMM` format.

Used for generated file names that may occur multiple times per task:

- handoffs;
- reviews;
- test reports;
- merge recommendations.

Tests monkeypatch these functions to make file names deterministic.

## String Helpers

### `slugify(value: str) -> str`

Turns a human string into a lowercase file-safe slug:

```python
slugify(" API Client & Auth!! ") == "api-client-auth"
```

Behavior:

- trims surrounding whitespace;
- lowercases;
- replaces non-alphanumeric runs with `-`;
- collapses repeated dashes;
- strips leading and trailing dashes.

### `normalize_task_key(task: str, title: str = "") -> str`

Normalizes task IDs for file names and branch names.

Examples:

```python
normalize_task_key("1", "API Client Refactor")
# TASK-1-api-client-refactor

normalize_task_key("task-002-api-client")
# TASK-002-api-client
```

Rules:

- non-alphanumeric/dash characters are replaced;
- empty task IDs raise `ValueError`;
- IDs that do not start with `TASK-` are prefixed with `TASK-`;
- `TASK-<number>` prefixes are uppercased;
- title slug wins when a title is supplied;
- existing task slug is reused when title is omitted.

### `display_task_id(task_key: str) -> str`

Turns normalized task keys into readable headings:

```python
display_task_id("TASK-002-api-client")
# TASK-002: Api Client
```

Nonstandard task keys are returned unchanged.

### `split_csv(value: str) -> list[str]`

Splits comma-separated options and removes blank entries:

```python
split_csv("main, production, , staging")
# ["main", "production", "staging"]
```

Used for `init --protected-branches`.

## Path Helpers

### `repo_root(path: Optional[str]) -> Path`

Root resolution order:

1. Explicit `path`, expanded and resolved.
2. `git rev-parse --show-toplevel`.
3. Current working directory.

This supports normal CLI usage, test usage with temporary directories, and non-git directories.

### `ensure_agent_dirs(root: Path) -> Path`

Creates `.agent/` and every directory in `AGENT_DIRS`, then returns the `.agent/` path.

Every artifact generator calls this function, so commands can be run before `agent-collab init`. Running `init` first is still recommended because it also writes `README.md` and `status.json`.

### `write_new(path: Path, content: str, force: bool = False) -> None`

Writes text to disk with conservative overwrite behavior.

Behavior:

- If the target exists and `force` is false, print `[skip]` and leave the file unchanged.
- Otherwise, create parent directories, write UTF-8 text, and print `[write]`.
- `content.lstrip()` is used so multiline template indentation does not leak into generated files.

This function is the main safety mechanism against accidental template overwrites.

## Command Functions

Each `command_*` function accepts a namespace-like object. This keeps the engine independent from Typer while still allowing tests to call command behavior directly.

### `command_init(args)`

Creates:

- `.agent/README.md`
- `.agent/status.json`
- all standard subdirectories

`status.json` includes:

```json
{
  "project": "project-name",
  "active_task": null,
  "current_phase": "planning",
  "protected_branches": ["main", "master", "production", "staging"],
  "agents": {},
  "merge_status": {
    "ready": false,
    "blocked_by": [
      "implementation handoff pending",
      "review pending",
      "test evidence pending"
    ]
  }
}
```

### `command_new_task(args)`

Creates a task file in `.agent/tasks/`.

Generated content includes:

- status;
- owner;
- related role branches;
- goal;
- non-goals;
- context;
- scope;
- acceptance criteria;
- required checks;
- risk level;
- known risks;
- dependencies;
- open questions;
- final result.

Related branch suggestions are generated for:

- architect;
- implementer;
- reviewer;
- tester;
- documentation;
- integration.

### `command_handoff(args)`

Creates a timestamped handoff in `.agent/handoffs/`.

Generated content includes:

- agent role;
- date;
- branch;
- worktree;
- status;
- summary;
- files changed;
- behavioral changes;
- architectural changes;
- commands run;
- verification results;
- failing checks;
- assumptions;
- risks;
- open questions;
- reviewer instructions;
- tester instructions;
- suggested next agent;
- rollback notes.

### `command_adr(args)`

Creates an ADR in `.agent/decisions/`.

Generated content includes:

- status;
- date;
- context;
- decision;
- alternatives considered;
- consequences;
- migration notes;
- follow-up tasks.

### `command_review(args)`

Creates a timestamped review in `.agent/reviews/`.

Generated content includes:

- reviewer;
- reviewed branch;
- review status;
- summary;
- correctness;
- architecture;
- security;
- reliability;
- maintainability;
- test coverage;
- required changes;
- suggested improvements;
- files requiring attention;
- human decision details;
- final recommendation.

### `command_test_report(args)`

Creates a timestamped test report in `.agent/test-reports/`.

Generated content includes:

- tester;
- branch tested;
- environment;
- commands run;
- result table;
- failures;
- suspected cause;
- reproduction steps;
- coverage gaps;
- recommendation.

### `command_conflict(args)`

Creates a conflict note in `.agent/risks/`.

Generated content includes:

- task;
- branches involved;
- files in conflict;
- conflict type;
- summary;
- recommended resolution;
- human decision requirement.

### `command_merge_recommendation(args)`

Creates a final merge recommendation in `.agent/reviews/`.

Generated content includes:

- recommendation;
- summary;
- implementation handoff evidence;
- review evidence;
- test report evidence;
- checks table;
- risk level;
- remaining risks;
- rollback plan;
- human approval requirement;
- next step.

### `command_file_ownership(args)`

Creates a file ownership map in `.agent/protocols/`.

Generated content includes:

- backend implementer ownership;
- frontend implementer ownership;
- tester ownership;
- integration assumptions;
- dependencies between branches;
- expected merge order;
- known conflict areas.

### `command_human_decision(args)`

Creates a human decision request in `.agent/risks/`.

Generated content includes:

- task;
- context;
- why a human decision is needed;
- options;
- recommendation;
- risk;
- default safe action.

## Testing Considerations

When changing this module:

1. Add or update direct tests in `tests/test_coordination.py`.
2. If file paths change, update CLI tests too.
3. Monkeypatch `today` and `timestamp` when asserting generated file names.
4. Verify existing-file behavior when touching `write_new`.
5. Run a temp-dir smoke test to inspect generated files.
