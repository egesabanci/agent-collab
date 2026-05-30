# Artifacts And Templates

Use `.agent/` as the durable coordination surface. If it matters to later work, write it here instead of relying on chat history.

## Source Of Truth Priority

When sources conflict, apply this priority:

1. Explicit user instruction
2. Task file
3. Accepted ADR
4. Latest coordinator handoff
5. Latest implementation handoff
6. Existing code behavior
7. Existing documentation
8. Agent inference

Document conflicts when user instructions override code, docs, or prior coordination artifacts.

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

Only coordinator agents or explicitly assigned agents should update `.agent/status.json`. If status ownership is unclear, write a handoff or risk note instead of racing on the shared JSON file.

## `.agent/status.json`

Track active task, phase, protected branches, assigned agents, and merge readiness.

```json
{
  "project": "example-project",
  "active_task": "TASK-002-api-client-refactor",
  "current_phase": "implementation",
  "protected_branches": ["main", "production", "staging"],
  "agents": {
    "implementer": {
      "branch": "agent/impl/TASK-002-api-client-refactor",
      "worktree": "../repo-implementer-api",
      "status": "in_progress",
      "last_handoff": null
    }
  },
  "merge_status": {
    "ready": false,
    "blocked_by": ["implementation incomplete", "review pending", "tests pending"]
  }
}
```

## Task Files

Path: `.agent/tasks/TASK-<number>-<short-name>.md`

Every task must include status, owner, related branches, goal, non-goals, context, scope, acceptance criteria, checks, risk level, dependencies, open questions, and final result.

Statuses:

```txt
planned | in_progress | blocked | review_ready | testing | merge_ready | merged | rejected
```

Create a task:

```bash
agent-collab new-task --id TASK-002 --title "API Client Refactor"
```

Run commands from the target repository root after installing the package. When coordinating another repository from elsewhere, pass `--root <repo-root>` to the command.

## Handoffs

Path: `.agent/handoffs/TASK-<number>-<role>-<timestamp>.md`

A handoff is invalid if it lacks branch name, status, files changed, verification results, open questions, risks, and suggested next agent.

Every handoff must answer:

- What changed?
- Why did it change?
- Where did it change?
- How was it verified?
- What risks remain?
- What should the next agent do?

Use open-question categories:

```md
## Open questions

### Blocking

- Question that must be answered before progress.

### Non-blocking

- Question that can be resolved later.

### Suggestions

- Optional improvement.

### Assumptions

- Assumption made to continue work.
```

## ADRs

Path: `.agent/decisions/ADR-<number>-<short-title>.md`

Create ADRs when introducing or changing:

- System boundaries
- Authentication or authorization behavior
- Data model shape
- API contracts
- Runtime architecture
- Deployment topology
- External service dependencies
- State management strategy
- Error handling policy
- Queue or job architecture
- Agent or tool architecture
- Security-sensitive patterns

Statuses:

```txt
proposed | accepted | rejected | superseded
```

## Reviews

Path: `.agent/reviews/TASK-<number>-review-<timestamp>.md`

Review status:

```txt
approved | changes_requested | blocked | needs_human_decision
```

Every review must cover correctness, architecture, security, reliability, maintainability, test coverage, required changes, suggested improvements, files requiring attention, human decision needs, and final recommendation.

## Test Reports

Path: `.agent/test-reports/TASK-<number>-test-report-<timestamp>.md`

Every test report must include environment, commands run, result table, failures, suspected cause, reproduction steps, coverage gaps, and recommendation.

Recommendations:

```txt
merge_ready | needs_fix | needs_more_tests | needs_human_decision
```

## Conflict Notes

Path: `.agent/risks/TASK-<number>-conflict-<short-name>.md`

Create a conflict note when two agents modify overlapping files or create semantic, dependency, test, architectural, or integration conflicts. Do not resolve silently.

Required fields:

- Task
- Branches involved
- Files in conflict
- Conflict type
- Summary
- Recommended resolution
- Whether a human decision is required

## File Ownership Maps

Path: `.agent/protocols/file-ownership-TASK-<number>.md`

Use file ownership maps for complex or parallel tasks. Include each agent's owned paths, forbidden paths, integration assumptions, dependencies, expected merge order, and known conflict areas.

Create a file ownership map:

```bash
agent-collab file-ownership --task TASK-002-api-client-refactor
```

Example:

```md
# File Ownership: TASK-002

## Backend implementer

Owns:

- `src/server/api/**`
- `src/lib/server-api.ts`

Must not edit:

- `src/components/**`

## Frontend implementer

Owns:

- `src/components/**`
- `src/hooks/**`

Must not edit:

- `src/server/api/**`
```

## Final Merge Recommendation

Create a merge recommendation before asking the user to merge. It must include recommendation, summary, implementation handoff, review, test report, check table, risk level, remaining risks, rollback plan, human approval requirement, and next step.

## Human Decision Notes

Path: `.agent/risks/TASK-<number>-human-decision-<short-name>.md`

Create a human decision note when a destructive, security-sensitive, production-affecting, billing, licensing, migration, public API, or ambiguous architecture decision blocks safe progress.
