# Security And Escalation

## Human Approval Required

Ask for explicit user approval before:

- Deleting important files
- Dropping database tables or columns
- Running destructive migrations
- Rotating production secrets
- Changing billing behavior
- Changing authentication or authorization boundaries
- Changing production deployment behavior
- Introducing paid external services
- Rewriting large parts of the system
- Removing public APIs
- Making irreversible changes
- Changing licensing terms
- Modifying legal, compliance, privacy-sensitive, or production-affecting logic

## High-Risk Areas

Treat these as high-risk:

- Authentication
- Authorization
- User identity
- Sessions
- Cookies
- CSRF
- CORS
- API keys
- Billing
- Payments
- Webhooks
- Admin panels
- Database migrations
- File uploads
- Multi-tenant data access
- PII handling
- Logging or analytics events containing user data
- Deployment secrets
- Infrastructure configuration

High-risk changes require reviewer focus and often human approval.

## Secrets

Never commit:

- API keys
- Tokens
- Private keys
- Passwords
- Session cookies
- Production `.env` files
- Service account credentials
- Database credentials

Before handoff, inspect:

```bash
git diff
git status --short
```

Search suspicious diffs for:

```txt
api_key
secret
token
password
private_key
BEGIN PRIVATE KEY
DATABASE_URL
OPENAI_API_KEY
ANTHROPIC_API_KEY
AWS_SECRET_ACCESS_KEY
```

If a secret was committed, stop and escalate. Do not merely delete it in a later commit and continue.

If a new environment variable is required, add it to `.env.example` or equivalent, document it, validate it at runtime if the project has env validation, and mention it in the handoff.

## Database Changes

For database changes:

- Create explicit migrations
- Avoid destructive migrations without human approval
- Preserve backward compatibility when possible
- Document rollback steps
- Consider existing data
- Consider production migration order
- Update schema types if applicable
- Update tests
- Update seed data if needed

Destructive examples include dropping tables, dropping columns, renaming columns without a compatibility layer, deleting data, changing primary keys, or changing auth/user identity semantics.

## API Contracts

When changing API behavior:

- Preserve existing contracts unless the task requires a breaking change
- Update request and response schemas
- Update client calls
- Update tests
- Update docs
- Document breaking changes
- Consider backward compatibility and migration notes

## Frontend Security

Preserve accessibility and responsive behavior. Keep server/client boundaries clear. Do not expose private backend details, internal service URLs, private tokens, or privileged endpoints to the browser. If client-side code needs data, it must call a public, authenticated, authorization-checked backend endpoint.

## Backend Security

Validate inputs, enforce authorization server-side, avoid trusting client-provided identity, avoid leaking internal errors, preserve logging observability, consider rate limits, consider idempotency, and account for concurrency or serverless runtime constraints.

## Runtime And Infrastructure

Deployment-affecting changes require extra care:

- CI/CD config
- Dockerfile
- Build command
- Runtime version
- Cloudflare Worker config
- Vercel config
- Database provisioning
- Environment bindings
- Scheduled jobs
- Cron triggers
- Domain or routing config

Include reason, risk, rollback, test plan, and human approval if production-impacting.

For serverless and edge environments, verify supported runtime APIs, native dependency risk, bundle size, cold start impact, environment variable availability, secret bindings, long-running task handling, and streaming support if relevant.

For background jobs, document trigger, queue, retry behavior, idempotency key, failure handling, timeout behavior, observability, and manual replay procedure.

## Failure Handling

When blocked, write a blocked handoff with blocker, what was tried, evidence, recommended next step, and whether work can continue.

When tests fail, document command, error, reproduction steps, suspected cause, whether the failure is related to current changes, and suggested fix.

When implementation becomes messy:

1. Stop expanding the diff.
2. Write a handoff explaining the issue.
3. Consider reverting only the task branch's own unclear work.
4. Ask coordinator whether to restart from main.
5. Do not pile fixes on top of unclear changes.

When scope expands:

1. Stop.
2. Document why scope expanded.
3. Propose a new task.
4. Continue only with approval or when expansion is necessary and low-risk.

## Escalation Template

```md
## Human decision needed

### Context

Explain the situation.

### Options

1. Option A
   - Pros
   - Cons

2. Option B
   - Pros
   - Cons

### Recommendation

State the recommended option.

### Risk

Explain risk level.

### Default safe action

State what to do if no decision is made.
```
