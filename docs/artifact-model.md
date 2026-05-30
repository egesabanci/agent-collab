# Artifact Model

Agent Collab creates a `.agent/` directory inside the target repository. This directory is the durable coordination surface for multi-agent work.

## Directory Structure

```txt
.agent/
  README.md
  status.json
  tasks/
  handoffs/
  decisions/
  reviews/
  test-reports/
  risks/
  protocols/
  scratch/
```

## Source Of Truth

When agents disagree, use this priority:

1. Repository files and git history.
2. `.agent/status.json`.
3. Current task file under `.agent/tasks/`.
4. Latest handoff for the relevant branch.
5. Review and test reports.
6. ADRs and file ownership maps.
7. Chat history.

Chat history is the weakest source because it is not durable, reviewable, or visible to every future agent.

## Artifact Lifecycle

```txt
task created
    |
    v
worktrees assigned
    |
    v
implementation handoff
    |
    v
review and test report
    |
    v
merge recommendation
    |
    v
human approval or further work
```

## Status File

`agent-collab init` creates `.agent/status.json`.

Default shape:

```json
{
  "project": "demo",
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

Use this file for shared state that needs to be machine-readable. Avoid stuffing narrative detail into it. Put narrative detail in Markdown artifacts.

## Task Files

Created by:

```bash
agent-collab new-task --id TASK-001 --title "Refactor API client"
```

Path:

```txt
.agent/tasks/TASK-001-refactor-api-client.md
```

Task files define:

- status;
- owner;
- related branches;
- goal;
- non-goals;
- context;
- in-scope and out-of-scope work;
- acceptance criteria;
- required checks;
- risk level;
- known risks;
- dependencies;
- open questions;
- final result.

Task files should be created before worktrees are assigned.

## Handoffs

Created by:

```bash
agent-collab handoff \
  --task TASK-001-refactor-api-client \
  --role implementer \
  --branch agent/impl/TASK-001-refactor-api-client \
  --worktree ../repo-implementer
```

Path pattern:

```txt
.agent/handoffs/<task-key>-<role>-<timestamp>.md
```

Handoffs should explain:

- what changed;
- why it changed;
- where it changed;
- how it was verified;
- what failed;
- what risks remain;
- what the next agent should do;
- how to roll back.

## ADRs

Created by:

```bash
agent-collab adr --number 1 --title "Use Server-Side API Wrapper"
```

Path pattern:

```txt
.agent/decisions/ADR-001-use-server-side-api-wrapper.md
```

Use ADRs for durable design decisions:

- system boundaries;
- security policies;
- API contracts;
- data models;
- runtime architecture;
- migration strategy;
- integration boundaries.

## Reviews

Created by:

```bash
agent-collab review \
  --task TASK-001-refactor-api-client \
  --branch agent/impl/TASK-001-refactor-api-client
```

Path pattern:

```txt
.agent/reviews/<task-key>-review-<timestamp>.md
```

Reviews should inspect the diff, not only final files. A useful review covers:

- correctness;
- architecture;
- security;
- reliability;
- maintainability;
- test coverage;
- required changes;
- suggested improvements;
- human decision requirements.

## Test Reports

Created by:

```bash
agent-collab test-report \
  --task TASK-001-refactor-api-client \
  --branch agent/impl/TASK-001-refactor-api-client
```

Path pattern:

```txt
.agent/test-reports/<task-key>-test-report-<timestamp>.md
```

Test reports should include:

- environment;
- commands run;
- result table;
- failures;
- reproduction steps;
- coverage gaps;
- recommendation.

Skipped checks need explicit justification.

## Conflict Notes

Created by:

```bash
agent-collab conflict \
  --task TASK-001-refactor-api-client \
  --title "API Client and Auth Boundary" \
  --type architectural \
  --requires-human yes
```

Path pattern:

```txt
.agent/risks/<task-key>-conflict-<slug>.md
```

Use conflict notes when:

- two agents touched overlapping files;
- branch changes conflict semantically;
- test failures are caused by interaction between branches;
- architecture direction is ambiguous;
- human approval is required.

## File Ownership Maps

Created by:

```bash
agent-collab file-ownership --task TASK-001-refactor-api-client
```

Path pattern:

```txt
.agent/protocols/file-ownership-<task-key>.md
```

Use file ownership maps before parallel work. They should state:

- which paths each agent owns;
- which paths each agent must not edit;
- integration assumptions;
- dependency order;
- expected merge order;
- known conflict areas.

## Human Decision Notes

Created by:

```bash
agent-collab human-decision \
  --task TASK-001-refactor-api-client \
  --title "Choose Auth Boundary" \
  --risk high
```

Path pattern:

```txt
.agent/risks/<task-key>-human-decision-<slug>.md
```

Use these when a decision is:

- destructive;
- irreversible;
- production-affecting;
- security-sensitive;
- billing-related;
- legally ambiguous;
- architecturally ambiguous.

## Merge Recommendations

Created by:

```bash
agent-collab merge-recommendation \
  --task TASK-001-refactor-api-client \
  --recommendation needs_changes \
  --risk medium \
  --human-approval-required yes
```

Path pattern:

```txt
.agent/reviews/<task-key>-merge-recommendation-<timestamp>.md
```

The merge recommendation should cite:

- implementation handoff;
- review;
- test report;
- check results;
- remaining risks;
- rollback plan;
- human approval status;
- next step.

## Naming Rules

Task keys are normalized by `normalize_task_key`:

- `1` plus title `Demo Task` becomes `TASK-1-demo-task`;
- `task-002-api-client` becomes `TASK-002-api-client`;
- title slugs are lowercase and dash-separated.

Timestamped artifacts use local time:

```txt
YYYY-MM-DD-HHMM
```

Because timestamped artifacts can be generated more than once per task, agents should link or cite the latest relevant artifact in handoffs and merge recommendations.
