# Agent Collab

A general-purpose coordination protocol and artifact generator for multiple AI coding agents working on one repository.

## Overview

Agent Collab is a repository orchestration protocol for AI coding agents, automation workflows, and human coordinators. It gives a team of agents a shared operating model for working on the same codebase without overwriting each other, losing context, duplicating work, or merging unreviewed changes.

The core idea is simple:

- Each agent works in its own git worktree.
- Each agent owns a clearly scoped role, branch, and task.
- The repository is the durable source of truth.
- Agents communicate through structured files, diffs, commits, reviews, test reports, and handoff notes.
- Protected branches are not edited directly.
- Human approval remains required for destructive, ambiguous, production-affecting, or security-sensitive decisions.

This repository is both:

- A portable agent instruction package, with `SKILL.md` as the agent-facing entry point for runtimes that support skill-style instructions.
- A small tooling package, with `scripts/agent_coordination.py` for creating standardized `.agent/` coordination files.

## Why This Exists

AI agents are effective at focused coding tasks, but multi-agent work fails quickly when agents share one working directory or rely on hidden chat state. Common failure modes include:

- Two agents editing the same files without knowing it.
- A reviewer seeing final files but not the diff.
- A tester not knowing which branch or worktree was tested.
- An implementer claiming checks passed without actually running them.
- Architectural decisions living only in a conversation transcript.
- Generated files, lockfiles, migrations, or secrets slipping into a branch unnoticed.
- Integration happening without a clear handoff, review, test report, or rollback plan.

Agent Collab addresses these failures by making coordination explicit, durable, and reviewable.

## What Agent Collab Provides

- Worktree-first collaboration rules
- Branch naming conventions for agent-owned work
- Role playbooks for coordinator, architect, implementer, reviewer, tester, documentation, and integration agents
- Structured `.agent/` repository state
- Task, handoff, review, test report, ADR, risk, conflict, ownership, and merge recommendation templates
- Security and escalation rules for high-risk changes
- A helper script for creating coordination artifacts consistently
- A quality gate for merge readiness

## Repository Layout

```txt
agent-collab/
  SKILL.md
  README.md
  agents/
    openai.yaml
  references/
    artifacts-and-templates.md
    quality-review-testing-merge.md
    role-playbooks.md
    security-and-escalation.md
    worktree-and-branch-protocol.md
  scripts/
    agent_coordination.py
```

### `SKILL.md`

The agent-facing runtime instructions. Any compatible agent runtime can load this file, and humans can also use it as the concise operating guide.

### `agents/openai.yaml`

Optional runtime metadata for platforms that read skill catalog metadata. It is not required for standalone use.

### `references/`

Detailed playbooks that keep `SKILL.md` concise while preserving a comprehensive protocol.

### `scripts/agent_coordination.py`

A Python helper for creating `.agent/` coordination artifacts in a target repository.

## Installation And Use

Clone this repository wherever you keep shared agent instructions or workflow tools:

```bash
git clone git@github.com:egesabanci/agent-collab.git
cd agent-collab
```

Use it in any of these ways:

- Ask an agent to follow `SKILL.md`.
- Place this folder in your agent runtime's skill, plugin, or instruction directory if it supports one.
- Run `scripts/agent_coordination.py` directly to create `.agent/` coordination artifacts.
- Have human coordinators use the README and reference files as the team protocol.

Example agent prompt:

```txt
Use Agent Collab to coordinate multiple coding agents safely on this repository task.
```

## Quick Start

From the repository where agents will collaborate, initialize the coordination directory:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py init
```

Create a task:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py new-task \
  --id TASK-001 \
  --title "API Client Refactor" \
  --owner coordinator \
  --risk medium \
  --check lint \
  --check typecheck \
  --check tests \
  --check build
```

Create role worktrees:

```bash
git fetch origin
git worktree add ../repo-implementer -b agent/impl/TASK-001-api-client-refactor origin/main
git worktree add ../repo-reviewer -b agent/review/TASK-001-api-client-refactor origin/main
git worktree add ../repo-tester -b agent/test/TASK-001-api-client-refactor origin/main
```

After implementation, create a handoff:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py handoff \
  --task TASK-001-api-client-refactor \
  --role implementer \
  --branch agent/impl/TASK-001-api-client-refactor \
  --worktree ../repo-implementer
```

Create review and test reports:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py review \
  --task TASK-001-api-client-refactor \
  --branch agent/impl/TASK-001-api-client-refactor

python3 /path/to/agent-collab/scripts/agent_coordination.py test-report \
  --task TASK-001-api-client-refactor \
  --branch agent/impl/TASK-001-api-client-refactor
```

Prepare merge readiness:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py merge-recommendation \
  --task TASK-001-api-client-refactor \
  --recommendation needs_changes \
  --risk medium \
  --human-approval-required yes
```

## The `.agent/` Directory

Agent Collab creates and uses a `.agent/` directory in the target repository:

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

This directory is the durable memory layer for the agent team.

### `.agent/status.json`

Tracks the active task, current phase, protected branches, assigned agents, and merge readiness.

Only a coordinator agent or explicitly assigned agent should update this file. If ownership is unclear, write a handoff or risk note instead of racing on shared state.

### `.agent/tasks/`

Contains scoped task definitions with:

- Goal
- Non-goals
- Context
- Scope
- Acceptance criteria
- Required checks
- Risk level
- Dependencies
- Open questions
- Final result

### `.agent/handoffs/`

Contains structured handoffs between roles.

A valid handoff answers:

- What changed?
- Why did it change?
- Where did it change?
- How was it verified?
- What risks remain?
- What should the next agent do?

### `.agent/decisions/`

Contains ADRs for architectural decisions.

Use ADRs for changes to:

- System boundaries
- Authentication or authorization behavior
- Data models
- API contracts
- Runtime architecture
- Deployment topology
- External services
- Error handling policy
- Queue or job architecture
- Security-sensitive patterns

### `.agent/reviews/`

Contains reviewer output. Reviewers must inspect the diff, not just final files.

Reviews cover:

- Task alignment
- Correctness
- Architecture
- Security
- Reliability
- Maintainability
- Test coverage
- Scope control
- Rollback safety

### `.agent/test-reports/`

Contains verification evidence:

- Environment
- Commands run
- Result table
- Failures
- Suspected cause
- Reproduction steps
- Coverage gaps
- Recommendation

### `.agent/risks/`

Contains conflicts, blockers, high-risk notes, and human decision requests.

Use this directory when two agents touch overlapping files or when a decision needs human approval.

### `.agent/protocols/`

Contains task-specific protocols, especially file ownership maps for parallel work.

## Agent Roles

Agent Collab defines a small set of roles. Use only the roles needed for the task.

| Role | Purpose |
| --- | --- |
| Coordinator | Scope, sequencing, assignment, worktree routing, merge recommendation |
| Architect | Design, boundaries, ADRs, risk analysis, test strategy |
| Implementer | Scoped code changes, tests, commits, implementation handoff |
| Reviewer | Diff review for correctness, architecture, security, reliability, maintainability |
| Tester | Verification, reproduction, smoke tests, test reports |
| Documentation | README, docs, examples, migration notes, operational notes |
| Integration | Conflict resolution, branch freshness, final checks, merge readiness |

## Standard Agent Workflow

Every agent should begin by confirming:

1. Role
2. Assigned task
3. Branch
4. Worktree
5. Task file
6. Relevant handoffs
7. Relevant ADRs
8. Current git status
9. Project check commands
10. Planned next action

Before editing, an agent should run:

```bash
git status
git branch --show-current
git log --oneline -5
```

Before handoff, an agent should run:

```bash
git status
git diff
git diff --stat
```

## Helper Script Reference

The helper script is intentionally dependency-light and uses only Python's standard library.

Run from the target repository root:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py <command>
```

Or pass an explicit target:

```bash
python3 /path/to/agent-collab/scripts/agent_coordination.py --root /path/to/repo <command>
```

The command examples below use `scripts/agent_coordination.py` for local development inside this repository. When coordinating another repository, replace that path with `/path/to/agent-collab/scripts/agent_coordination.py` or pass `--root`.

### `init`

Create the `.agent/` directory structure.

```bash
python3 scripts/agent_coordination.py init \
  --project example-project \
  --phase planning \
  --protected-branches main,master,production,staging
```

### `new-task`

Create a task file.

```bash
python3 scripts/agent_coordination.py new-task \
  --id TASK-002 \
  --title "Improve checkout error handling" \
  --owner implementer \
  --risk high \
  --check lint \
  --check tests \
  --check build
```

### `handoff`

Create a role handoff.

```bash
python3 scripts/agent_coordination.py handoff \
  --task TASK-002-improve-checkout-error-handling \
  --role implementer \
  --branch agent/impl/TASK-002-improve-checkout-error-handling \
  --worktree ../repo-implementer \
  --status needs_review \
  --next-agent reviewer
```

### `adr`

Create an architecture decision record.

```bash
python3 scripts/agent_coordination.py adr \
  --number 1 \
  --title "Use Server-Side API Wrapper"
```

### `review`

Create a review template.

```bash
python3 scripts/agent_coordination.py review \
  --task TASK-002-improve-checkout-error-handling \
  --branch agent/impl/TASK-002-improve-checkout-error-handling \
  --status changes_requested \
  --recommendation request_changes
```

### `test-report`

Create a test report template.

```bash
python3 scripts/agent_coordination.py test-report \
  --task TASK-002-improve-checkout-error-handling \
  --branch agent/impl/TASK-002-improve-checkout-error-handling \
  --recommendation needs_fix
```

### `conflict`

Create a conflict note.

```bash
python3 scripts/agent_coordination.py conflict \
  --task TASK-002-improve-checkout-error-handling \
  --title "Checkout API and Billing Boundary" \
  --type architectural \
  --requires-human yes
```

### `file-ownership`

Create a file ownership map.

```bash
python3 scripts/agent_coordination.py file-ownership \
  --task TASK-002-improve-checkout-error-handling
```

### `human-decision`

Create a human decision note.

```bash
python3 scripts/agent_coordination.py human-decision \
  --task TASK-002-improve-checkout-error-handling \
  --title "Choose Billing Retry Policy" \
  --risk high
```

### `merge-recommendation`

Create a final merge recommendation.

```bash
python3 scripts/agent_coordination.py merge-recommendation \
  --task TASK-002-improve-checkout-error-handling \
  --recommendation needs_human_decision \
  --risk high \
  --human-approval-required yes
```

## Worktree Strategy

Agent Collab expects one worktree per agent role or independently owned task slice.

Example:

```txt
repo/
../repo-architect/
../repo-implementer-api/
../repo-implementer-ui/
../repo-reviewer/
../repo-tester/
../repo-integration/
```

Recommended branch names:

```txt
agent/architect/TASK-002-api-client-refactor
agent/impl/TASK-002-api-client-refactor
agent/impl-frontend/TASK-002-api-client-refactor
agent/impl-backend/TASK-002-api-client-refactor
agent/review/TASK-002-api-client-refactor
agent/test/TASK-002-api-client-refactor
agent/docs/TASK-002-api-client-refactor
agent/integration/TASK-002-api-client-refactor
```

## Safe Parallelization

Parallel work is safest when agents own different parts of the system.

Good split:

```txt
Agent A: backend API route
Agent B: frontend UI state
Agent C: documentation
Agent D: tests
```

Risky split:

```txt
Agent A: auth middleware
Agent B: API client
Agent C: session handling
Agent D: routing layer
```

Risky splits require a file ownership map and explicit integration plan.

## Merge Readiness

A task is merge-ready only when:

- Acceptance criteria are met.
- Scope is controlled.
- Implementation handoff exists.
- Review exists.
- Required checks were run or skipped with clear justification.
- Test report exists for non-trivial changes.
- No blocking questions remain.
- No unresolved high-risk issues remain.
- No secrets are present.
- Rollback path is documented.
- Human approval exists where required.

## Security Model

Agent Collab treats these areas as high risk:

- Authentication
- Authorization
- User identity
- Sessions and cookies
- CSRF and CORS
- Billing and payments
- Webhooks
- Admin panels
- Database migrations
- File uploads
- Multi-tenant data access
- PII handling
- Logging or analytics containing user data
- Deployment secrets
- Infrastructure configuration

High-risk changes require focused review and often human approval.

If a secret is committed, stop and escalate. Do not merely delete it in a later commit and continue.

## What Agent Collab Is Not

Agent Collab is not:

- A replacement for CI.
- A replacement for GitHub branch protection.
- A replacement for human architectural judgment.
- A merge bot.
- A distributed locking system.
- A guarantee that parallel work will never conflict.

It is a protocol and artifact generator that makes multi-agent work more explicit, inspectable, and recoverable.

## Validation

If your agent runtime provides a package or skill validator, run it against the repository root. At minimum, validate the frontmatter and metadata YAML:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml

skill = Path("SKILL.md").read_text()
yaml.safe_load(skill.split("---", 2)[1])
yaml.safe_load(Path("agents/openai.yaml").read_text())
print("metadata ok")
PY
```

Validate the helper script with:

```bash
python3 -B -m py_compile scripts/agent_coordination.py
python3 -B scripts/agent_coordination.py --help
```

Smoke-test artifact generation in a temporary directory:

```bash
tmpdir="$(mktemp -d)"
python3 scripts/agent_coordination.py --root "$tmpdir" init --project demo
python3 scripts/agent_coordination.py --root "$tmpdir" new-task --id TASK-001 --title "Demo Task"
find "$tmpdir/.agent" -maxdepth 2 -type f | sort
rm -rf "$tmpdir"
```

## Development Notes

Keep `SKILL.md` concise and agent-facing. Put detailed protocol material in `references/`, and keep deterministic, repeatable generation behavior in `scripts/`.

When changing the protocol:

1. Update `SKILL.md` only if the runtime entry point changes.
2. Update the relevant reference file for detailed behavior.
3. Update `scripts/agent_coordination.py` when templates or artifact names change.
4. Run validation and a temp-dir smoke test.
5. Use a conventional commit message.

## Suggested Repository Description

A general-purpose coordination protocol for multiple AI coding agents working on one repository with worktree isolation, structured handoffs, review, testing, and merge readiness.

## License

Agent Collab is released under the MIT License. See [LICENSE](LICENSE).
