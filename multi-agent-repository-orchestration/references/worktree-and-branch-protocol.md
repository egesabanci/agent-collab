# Worktree And Branch Protocol

Agents must not share a physical working directory unless the user explicitly instructs them to. Use one git worktree and branch per role or independently owned task slice.

## Recommended Layout

```txt
repo/
../repo-architect/
../repo-implementer-auth/
../repo-implementer-api/
../repo-reviewer/
../repo-tester/
../repo-docs/
../repo-integration/
```

## Protected Branches

Treat `main`, `master`, `production`, `staging`, release branches, and deployment branches as protected.

Agents must not:

- Commit directly to protected branches
- Force-push protected branches
- Rebase shared branches without approval
- Delete remote branches without explicit instruction
- Push secrets or credentials
- Change deployment configuration casually
- Merge their own work without review

## Branch Naming

Use:

```txt
agent/<role>/<task-id>-<short-description>
```

Examples:

```txt
agent/architect/TASK-002-api-client-refactor
agent/impl/TASK-002-api-client-refactor
agent/review/TASK-002-api-client-refactor
agent/test/TASK-002-api-client-refactor
agent/docs/TASK-002-api-client-refactor
agent/integration/TASK-002-api-client-refactor
```

For multiple implementation agents:

```txt
agent/impl-frontend/TASK-002-api-client-refactor
agent/impl-backend/TASK-002-api-client-refactor
agent/impl-db/TASK-002-api-client-refactor
```

## Create Worktrees

```bash
git fetch origin
git worktree add ../repo-architect -b agent/architect/TASK-002-api-client-refactor origin/main
git worktree add ../repo-implementer-api -b agent/impl/TASK-002-api-client-refactor origin/main
git worktree add ../repo-reviewer -b agent/review/TASK-002-api-client-refactor origin/main
git worktree add ../repo-tester -b agent/test/TASK-002-api-client-refactor origin/main
```

If the branch already exists:

```bash
git worktree add ../repo-implementer-api agent/impl/TASK-002-api-client-refactor
```

List worktrees:

```bash
git worktree list
```

Remove completed worktrees:

```bash
git worktree remove ../repo-implementer-api
git worktree prune
```

## Ownership

An agent owns its assigned worktree. Agents must not edit another agent's worktree unless explicitly instructed.

If an agent needs files from another branch:

1. Fetch the branch.
2. Inspect the diff.
3. Cherry-pick only if appropriate.
4. Document the action.
5. Avoid silently overwriting work.

## Startup Routine

Before editing, every agent must run:

```bash
git status
git branch --show-current
git log --oneline -5
```

Then inspect:

```bash
cat .agent/tasks/TASK-002-api-client-refactor.md
ls .agent/handoffs/
```

Do not code before understanding the current branch, task, relevant handoffs, and project conventions.

## Clean Handoff Check

Before handoff, run:

```bash
git status
git diff
git diff --stat
```

The handoff must mention uncommitted changes, untracked files, generated files, modified lockfiles, failing checks, and skipped checks.

## Duplicate Work Check

Before starting, inspect:

```bash
git branch --all
ls .agent/tasks
ls .agent/handoffs
```

If another agent already owns the same task or files, coordinate before editing.

## Parallelization Rules

Parallel agents are safe when tasks touch different areas or have a file ownership map.

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

Risky splits require explicit coordination and usually a file ownership map under `.agent/protocols/`.

## Syncing

Prefer the repository's existing convention. If none is known, merge `origin/main` into task branches for integration work:

```bash
git fetch origin
git merge origin/main
```

Use rebase only when project convention allows it, and never rebase shared branches without approval.
