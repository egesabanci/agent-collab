# Quality, Review, Testing, And Merge

## Minimal Change Principle

Implement the smallest change that satisfies the task. Avoid opportunistic refactors, unrequested rewrites, style-only churn, unrelated renames, broad formatting, and dependency changes for small tasks.

## Follow Existing Conventions

Before writing code, inspect existing patterns for:

- File structure
- Naming
- Error handling
- Logging
- Type definitions
- API response shape
- Validation style
- Test style
- Dependency injection
- State management
- Environment variable handling
- Build tooling

Prefer consistency over preference.

## Dependencies

Do not add dependencies unless necessary. Before adding one, check whether an existing dependency solves the problem, whether the package is maintained, bundle/runtime/security impact, native module requirements, serverless or edge compatibility, and license risk. Document the reason in the handoff.

## Type Safety

Do not bypass type errors casually. Avoid broad use of:

```ts
any
// @ts-ignore
// @ts-expect-error
as unknown as
```

If a type escape is necessary, keep it local and document why.

## Error Handling

Preserve or improve error handling. Do not swallow errors silently. Prefer clear messages, typed errors where useful, structured logs, user-safe responses, hidden internals, safe retries, and idempotency for repeated operations.

## Review The Diff

Reviewer agents must inspect:

```bash
git diff origin/main...HEAD
git diff --stat origin/main...HEAD
```

Review categories:

1. Task alignment
2. Correctness
3. Architecture
4. Security
5. Reliability
6. Maintainability
7. Test coverage
8. Scope control
9. Rollback safety

Request changes if tests fail, task is incomplete, scope expanded without justification, a security risk exists, a secret is committed, error handling is weak, contracts break, complexity is too high, edge cases are unhandled, risky behavior lacks tests, migration is unsafe, or human decision is required.

Approve only when the task is satisfied, scope is controlled, checks pass or skipped checks are justified, risks are documented, no blocking questions remain, no obvious security issue exists, code matches patterns, and rollback is reasonable.

## Determine Project Commands

Before testing, inspect:

```bash
cat package.json
ls
find . -maxdepth 2 -name "README.md" -o -name "Makefile" -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "go.mod"
```

Use commands that exist.

JavaScript and TypeScript:

```bash
npm run lint
npm run typecheck
npm test
npm run test
npm run build
pnpm lint
pnpm typecheck
pnpm test
pnpm build
yarn lint
yarn typecheck
yarn test
yarn build
```

Python:

```bash
pytest
python -m pytest
ruff check .
mypy .
```

Go:

```bash
go test ./...
go vet ./...
```

Rust:

```bash
cargo fmt --check
cargo clippy
cargo test
cargo build
```

Manual smoke tests may include happy path, empty state, error state, unauthorized state, loading state, form validation, API failure, refresh or retry behavior, backward compatibility, mobile or responsive layout, and production-like runtime constraints.

## Commit Protocol

Before committing:

```bash
git status
git diff
git diff --staged
```

Commit message format:

```txt
<TASK-ID>: <short imperative summary>
```

Examples:

```txt
TASK-002: refactor API client through server wrapper
TASK-002: add tests for internal API routing
TASK-002: document API client migration notes
```

Avoid messages like `fix`, `changes`, `wip`, `stuff`, `agent edits`, or `final`.

## Pull Request Protocol

If the workflow uses PRs, include:

```md
# Summary

# Task

# Changes

# Verification

# Risk

# Rollback

# Handoffs

# Reviews

# Test reports

# Open questions
```

## Merge Readiness

A task is merge-ready only if:

- Task acceptance criteria are met
- Implementation handoff exists
- Review exists
- Tests were run or skipped with justification
- Test report exists for non-trivial changes
- No blocking questions remain
- No unresolved high-risk issues remain
- No secrets are present
- Branch is safe enough to merge
- Rollback path is documented
- Human approval exists where required

Preferred merge method depends on project convention. Use squash for small task branches, merge commits when preserving multi-agent history matters, and rebase merge only if project convention allows.

After merge:

1. Update task status to `merged`.
2. Add final result to task file.
3. Remove or archive completed worktrees if appropriate.
4. Delete merged remote branches only if project convention allows.
5. Document follow-up tasks.
6. Keep ADRs and test reports.

## Quality Bar

A good agent output is scoped, tested, reviewable, documented, reversible, consistent with project patterns, honest about uncertainty, explicit about risks, and clear about next steps.

A bad output is large, unfocused, untested, poorly documented, full of unrelated refactors, silent about risks, based only on hidden context, hard to review, hard to roll back, or merged without review.
