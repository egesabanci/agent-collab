---
name: multi-agent-repository-orchestration
description: Coordinate multiple AI coding agents working on the same repository with git worktree isolation, task ownership, structured handoffs, review, testing, merge readiness, conflict handling, and human escalation. Use when Codex needs to orchestrate parallel or sequential agents on one codebase, split work across architect/implementer/reviewer/tester/documentation/integration roles, create .agent coordination files, prevent agents from overwriting each other, or safely prepare multi-agent repository changes for merge.
---

# Multi-Agent Repository Orchestration

## Overview

Use this skill to run multiple AI agents on one repository without shared working-directory edits, hidden state, duplicated work, or unreviewed merges. The repository is the coordination surface: task files, branches, worktrees, handoffs, reviews, test reports, ADRs, and status files must capture everything future agents need.

## Core Rules

- Use a dedicated git worktree and branch for each agent role or independently owned task slice.
- Never edit protected branches such as `main`, `master`, `production`, `staging`, or release branches directly.
- Keep tasks small, scoped, reviewable, testable, and reversible.
- Write durable coordination state under `.agent/`; do not rely on private chat context.
- Require implementation handoff, review evidence, and verification evidence before merge readiness.
- Escalate destructive, production-affecting, security-sensitive, billing, auth, licensing, or ambiguous architectural decisions to the user.
- Do not claim checks passed unless they were run.
- Do not silently resolve overlapping agent work; document conflicts under `.agent/risks/`.

## Standard Workflow

1. Initialize coordination files if `.agent/` does not exist:

   ```bash
   python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py init
   ```

2. Create or read the task file before assigning agents:

   ```bash
   python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py new-task --id TASK-001 --title "API Client Refactor"
   ```

3. Decide whether work can run in parallel. Parallelize only when agents have disjoint file ownership or a documented coordination plan.
4. Create one worktree per agent from the protected base branch.
5. Give each agent a role, task file, branch, worktree, owned files, non-goals, required checks, and handoff expectation.
6. Require each implementation agent to inspect status, branch, task, existing patterns, and relevant handoffs before editing.
7. Require handoff after implementation, review after handoff, test report after review, and integration check before merge.
8. Ask the user before destructive, irreversible, production, security, auth, billing, or licensing changes.

## Coordination Files

Use this repository structure:

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

Create durable artifacts with:

```bash
python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py handoff --task TASK-001-api-client-refactor --role implementer --branch agent/impl/TASK-001-api-client-refactor --worktree ../repo-implementer
python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py review --task TASK-001-api-client-refactor --branch agent/impl/TASK-001-api-client-refactor
python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py test-report --task TASK-001-api-client-refactor --branch agent/impl/TASK-001-api-client-refactor
python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py adr --number 1 --title "Use Server-Side API Wrapper"
python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py conflict --task TASK-001-api-client-refactor --title "API Client and Auth Changes"
python3 /path/to/multi-agent-repository-orchestration/scripts/agent_coordination.py merge-recommendation --task TASK-001-api-client-refactor
```

Read [references/artifacts-and-templates.md](references/artifacts-and-templates.md) for file names, required fields, source-of-truth priority, and complete template guidance.

## Worktree Protocol

Create sibling worktrees from the base branch:

```bash
git fetch origin
git worktree add ../repo-implementer -b agent/impl/TASK-001-api-client-refactor origin/main
git worktree add ../repo-reviewer -b agent/review/TASK-001-api-client-refactor origin/main
git worktree add ../repo-tester -b agent/test/TASK-001-api-client-refactor origin/main
git worktree list
```

Branch naming:

```txt
agent/<role>/<task-id>-<short-description>
agent/impl-frontend/<task-id>-<short-description>
agent/impl-backend/<task-id>-<short-description>
```

Before editing, every agent must run:

```bash
git status
git branch --show-current
git log --oneline -5
```

Read [references/worktree-and-branch-protocol.md](references/worktree-and-branch-protocol.md) before creating, sharing, rebasing, integrating, or removing worktrees.

## Role Selection

Use the smallest role set that makes the task safe:

| Role | Use for |
| --- | --- |
| Coordinator | Scoping, task flow, worktree assignment, handoff routing, merge recommendation |
| Architect | Solution design, boundaries, ADRs, split strategy, testing strategy |
| Implementer | Scoped code changes, tests, commits, implementation handoff |
| Reviewer | Diff review for correctness, architecture, security, reliability, maintainability, tests |
| Tester | Running checks, reproducing flows, smoke testing, test report |
| Documentation | README/docs/examples/migration notes aligned with implemented behavior |
| Integration | Conflict resolution, branch freshness, final checks, merge readiness |

Read [references/role-playbooks.md](references/role-playbooks.md) for responsibilities, forbidden actions, workflows, and role prompts.

## Quality Gate

Implementation is not ready for merge until:

- Task acceptance criteria are satisfied.
- Scope is controlled and unrelated churn is absent.
- Implementation handoff exists.
- Review exists and has no unresolved blocking findings.
- Required checks were run or skipped with clear justification.
- Test report exists for non-trivial changes.
- Secrets and high-risk changes were checked.
- Rollback path is documented.
- Human approval exists where required.

Read [references/quality-review-testing-merge.md](references/quality-review-testing-merge.md) for coding, review, testing, commit, PR, and merge rules.

## Security And Escalation

Treat auth, authorization, identity, sessions, cookies, CSRF, CORS, billing, payments, webhooks, admin panels, database migrations, file uploads, multi-tenant data access, PII, logging of user data, deployment secrets, and infrastructure as high-risk.

If a secret is committed, stop and escalate. Do not merely delete it in a later commit and continue.

Read [references/security-and-escalation.md](references/security-and-escalation.md) for high-risk areas, human approval triggers, database/API/runtime rules, failure handling, and escalation templates.
