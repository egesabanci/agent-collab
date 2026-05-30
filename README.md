![Agent Collab banner](https://raw.githubusercontent.com/egesabanci/agent-collab/main/assets/agent-collab-banner.png)

<div align="center">

# Agent Collab

**A coordination protocol and CLI for multiple AI coding agents working safely in one repository.**

[PyPI](https://pypi.org/project/agent-collab/) ·
[Quick Start](#quick-start) ·
[Workflow](#workflow) ·
[CLI Reference](#cli-reference) ·
[License](#license)

[![PyPI](https://img.shields.io/pypi/v/agent-collab.svg)](https://pypi.org/project/agent-collab/)
[![Python](https://img.shields.io/pypi/pyversions/agent-collab.svg)](https://pypi.org/project/agent-collab/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

Agent Collab gives AI coding agents a shared operating model for parallel repository work. It combines a portable agent skill, a worktree-first collaboration protocol, and a Typer-based CLI that creates durable `.agent/` coordination artifacts.

Use it when several agents, automation workflows, or human reviewers need to work on the same codebase without hidden chat state, unclear ownership, duplicated edits, or unreviewed merges.

## Highlights

- **Worktree-first collaboration**: each agent works in its own branch and worktree.
- **Durable coordination state**: tasks, handoffs, reviews, test reports, risks, ADRs, and merge recommendations live in `.agent/`.
- **Role-based workflow**: coordinator, architect, implementer, reviewer, tester, documentation, and integration roles have explicit responsibilities.
- **CLI-generated artifacts**: repeatable templates reduce ambiguity and make handoffs reviewable.
- **Runtime-agnostic skill package**: `SKILL.md` can be used by any agent runtime that supports skill-style instructions.
- **Human approval gates**: destructive, ambiguous, security-sensitive, or production-affecting changes are escalated instead of guessed.

## Quick Start

Install the CLI:

```bash
python3 -m pip install agent-collab
```

Initialize coordination files in the repository where agents will collaborate:

```bash
agent-collab init
```

Create a task:

```bash
agent-collab new-task \
  --id TASK-001 \
  --title "Refactor API client" \
  --owner coordinator \
  --risk medium \
  --check lint \
  --check tests \
  --check build
```

Create role-specific worktrees:

```bash
git fetch origin
git worktree add ../repo-implementer -b agent/impl/TASK-001-refactor-api-client origin/main
git worktree add ../repo-reviewer -b agent/review/TASK-001-refactor-api-client origin/main
git worktree add ../repo-tester -b agent/test/TASK-001-refactor-api-client origin/main
```

After implementation, create the handoff, review, test report, and merge recommendation:

```bash
agent-collab handoff \
  --task TASK-001-refactor-api-client \
  --role implementer \
  --branch agent/impl/TASK-001-refactor-api-client \
  --worktree ../repo-implementer

agent-collab review \
  --task TASK-001-refactor-api-client \
  --branch agent/impl/TASK-001-refactor-api-client

agent-collab test-report \
  --task TASK-001-refactor-api-client \
  --branch agent/impl/TASK-001-refactor-api-client

agent-collab merge-recommendation \
  --task TASK-001-refactor-api-client \
  --recommendation needs_changes \
  --risk medium \
  --human-approval-required yes
```

## Workflow

Agent Collab is intentionally simple: it makes repository state the source of truth and makes every handoff inspectable.

| Step | What happens | Artifact |
| --- | --- | --- |
| 1. Plan | Scope the task, risks, checks, and ownership. | `.agent/tasks/` |
| 2. Isolate | Assign each role a branch and git worktree. | `.agent/protocols/` |
| 3. Implement | Make scoped changes and record verification. | commits and handoff |
| 4. Review | Inspect the diff for correctness, security, scope, and maintainability. | `.agent/reviews/` |
| 5. Test | Run required checks or document why they were skipped. | `.agent/test-reports/` |
| 6. Gate | Recommend merge, changes, escalation, or rejection. | merge recommendation |

Agents should start every session by confirming:

```txt
role, task, branch, worktree, relevant handoffs, current git status, and next action
```

Before editing, run:

```bash
git status
git branch --show-current
git log --oneline -5
```

Before handing off, run:

```bash
git status
git diff
git diff --stat
```

## The `.agent/` Directory

`agent-collab init` creates a coordination workspace in the target repository:

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

| Path | Purpose |
| --- | --- |
| `.agent/status.json` | Active task, current phase, protected branches, agent assignments, and merge status. |
| `.agent/tasks/` | Task goals, non-goals, scope, acceptance criteria, checks, risks, and result. |
| `.agent/handoffs/` | Structured role-to-role handoffs with changed files, verification, risks, and next steps. |
| `.agent/decisions/` | ADRs for architectural or policy decisions. |
| `.agent/reviews/` | Diff review and final merge recommendations. |
| `.agent/test-reports/` | Verification evidence, failures, skipped checks, and coverage gaps. |
| `.agent/risks/` | Conflicts, blockers, high-risk notes, and human decision requests. |
| `.agent/protocols/` | File ownership maps and task-specific coordination rules. |
| `.agent/scratch/` | Temporary notes that are not durable project truth. |

## CLI Reference

Run commands from the target repository root:

```bash
agent-collab <command>
```

Or pass an explicit repository:

```bash
agent-collab <command> --root /path/to/repo
```

| Command | Creates |
| --- | --- |
| `init` | `.agent/` directory structure and `status.json` |
| `new-task` | scoped task file |
| `handoff` | role handoff |
| `adr` | architecture decision record |
| `review` | review template |
| `test-report` | verification report |
| `conflict` | conflict or blocker note |
| `file-ownership` | file ownership map |
| `human-decision` | human decision request |
| `merge-recommendation` | final merge recommendation |

Use built-in help for the exact options:

```bash
agent-collab --help
agent-collab new-task --help
agent-collab handoff --help
```

## Agent Roles

Use only the roles needed for the task.

| Role | Responsibility |
| --- | --- |
| Coordinator | Scope, sequence, assign worktrees, track status, and recommend merge readiness. |
| Architect | Define boundaries, ADRs, risk analysis, and test strategy. |
| Implementer | Make scoped code changes, add tests, commit, and write implementation handoff. |
| Reviewer | Review the diff for correctness, architecture, security, reliability, and scope. |
| Tester | Run verification, reproduce failures, and write test reports. |
| Documentation | Update README, examples, migration notes, and operational docs. |
| Integration | Resolve conflicts, verify branch freshness, run final checks, and prepare merge guidance. |

## Worktree Strategy

One agent should not edit the same working directory as another agent. Give each role or task slice a separate worktree:

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
agent/architect/TASK-001-refactor-api-client
agent/impl/TASK-001-refactor-api-client
agent/impl-frontend/TASK-001-refactor-api-client
agent/impl-backend/TASK-001-refactor-api-client
agent/review/TASK-001-refactor-api-client
agent/test/TASK-001-refactor-api-client
agent/docs/TASK-001-refactor-api-client
agent/integration/TASK-001-refactor-api-client
```

Parallel work is safest when agents own different files or layers. If two agents may touch overlapping code, create a file ownership map before implementation:

```bash
agent-collab file-ownership --task TASK-001-refactor-api-client
```

## Using The Skill

This repository also ships a portable agent skill:

- `SKILL.md` is the agent-facing entry point.
- `references/` contains the deeper playbooks.
- `agents/openai.yaml` provides optional runtime metadata for platforms that read skill catalogs.

To use it manually, point an agent at `SKILL.md` and ask it to follow Agent Collab for the current repository task.

Example prompt:

```txt
Use Agent Collab to coordinate multiple coding agents on this repository. Start by identifying the task, role, branch, worktree, risks, and required handoffs.
```

## Merge Readiness

A task is merge-ready only when:

- acceptance criteria are met;
- scope is controlled;
- implementation handoff exists;
- review exists and is not blocking;
- required checks passed or skips are justified;
- test report exists for non-trivial changes;
- high-risk issues are resolved or escalated;
- no secrets are present;
- rollback notes exist when needed;
- human approval exists where required.

Agent Collab is not a replacement for CI, branch protection, human architectural judgment, or security review. It is a protocol and artifact generator that makes multi-agent work easier to inspect, recover, and merge deliberately.

## Repository Layout

```txt
agent-collab/
  SKILL.md
  README.md
  LICENSE
  pyproject.toml
  agents/
    openai.yaml
  references/
    artifacts-and-templates.md
    quality-review-testing-merge.md
    role-playbooks.md
    security-and-escalation.md
    worktree-and-branch-protocol.md
  src/
    agent_collab/
      cli.py
      coordination.py
  tests/
    test_cli.py
    test_coordination.py
```

## Development

Install locally:

```bash
python3 -m pip install -e ".[dev]"
```

Run tests:

```bash
python3 -m pytest
```

Validate the skill metadata:

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

## License

Agent Collab is released under the MIT License. See [LICENSE](LICENSE).
