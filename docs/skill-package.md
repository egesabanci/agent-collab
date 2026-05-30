# Skill Package

Agent Collab is both a Python CLI and a portable agent skill. The skill package is the set of files that an agent runtime or human coordinator can use as operating instructions.

## Files

```txt
SKILL.md
agents/
  openai.yaml
references/
  artifacts-and-templates.md
  quality-review-testing-merge.md
  role-playbooks.md
  security-and-escalation.md
  worktree-and-branch-protocol.md
```

## `SKILL.md`

`SKILL.md` is the agent-facing entry point.

It contains:

- YAML frontmatter with `name` and `description`;
- overview;
- core rules;
- standard workflow;
- coordination file structure;
- command examples;
- worktree protocol summary;
- role selection table;
- quality gate;
- security and escalation summary;
- links to reference files.

Keep this file concise. It should give an agent enough instruction to start safely, then route deeper detail to `references/`.

## Frontmatter

Current frontmatter:

```yaml
---
name: agent-collab
description: Coordinate multiple AI coding agents working on the same repository with git worktree isolation, task ownership, structured handoffs, review, testing, merge readiness, conflict handling, and human escalation. Use when an AI agent, agent runtime, automation workflow, or human coordinator needs to orchestrate parallel or sequential agents on one codebase, split work across architect/implementer/reviewer/tester/documentation/integration roles, create .agent coordination files, prevent agents from overwriting each other, or safely prepare multi-agent repository changes for merge.
---
```

The description should stay runtime-neutral. Avoid wording that makes the skill specific to one agent product.

## Runtime Metadata

`agents/openai.yaml` provides optional metadata for runtimes that read catalog files:

```yaml
interface:
  display_name: "Agent Collab"
  short_description: "Coordinate agents on one repo"
  default_prompt: "Use $agent-collab to coordinate multiple coding agents safely on this repository task."
```

This file should remain optional. The skill must still be understandable from `SKILL.md` alone.

## Reference Files

### `references/artifacts-and-templates.md`

Detailed artifact model:

- source-of-truth priority;
- `.agent/` directory structure;
- status file;
- task files;
- handoffs;
- ADRs;
- reviews;
- test reports;
- conflict notes;
- file ownership maps;
- merge recommendations;
- human decision notes.

### `references/worktree-and-branch-protocol.md`

Worktree rules:

- recommended layout;
- protected branches;
- branch naming;
- worktree creation;
- ownership;
- startup routine;
- clean handoff checks;
- duplicate work checks;
- parallelization rules;
- syncing.

### `references/role-playbooks.md`

Role instructions:

- coordinator;
- architect;
- implementer;
- reviewer;
- tester;
- documentation;
- integration.

Each role has responsibilities and forbidden actions.

### `references/quality-review-testing-merge.md`

Quality and merge rules:

- minimal change principle;
- existing conventions;
- dependencies;
- type safety;
- error handling;
- diff review;
- command discovery;
- commit protocol;
- pull request protocol;
- merge readiness;
- quality bar.

### `references/security-and-escalation.md`

Safety rules:

- human approval triggers;
- high-risk areas;
- secrets;
- database changes;
- API contracts;
- frontend security;
- backend security;
- runtime and infrastructure;
- failure handling;
- escalation template.

## Skill Maintenance Rules

When changing the CLI:

1. Update `docs/cli.md`.
2. Update `docs/artifact-model.md` if generated files change.
3. Update `SKILL.md` if agent behavior changes.
4. Update `references/` if detailed protocol guidance changes.
5. Update tests.

When changing the protocol:

1. Update the relevant reference file.
2. Keep `SKILL.md` as a concise summary.
3. Update docs if the change affects maintainers or users.
4. Run the skill validator.

When changing runtime metadata:

1. Keep runtime-specific metadata in `agents/`.
2. Do not move runtime-specific instructions into the core skill unless the rule is broadly applicable.
3. Validate YAML formatting.

## Validation

Use a skill validator when available:

```bash
python3 /path/to/quick_validate.py .
```

Manual checks:

- `SKILL.md` has valid YAML frontmatter.
- Linked reference paths exist.
- `agents/openai.yaml` parses as YAML.
- The skill description is broad enough to trigger on multi-agent coordination tasks.
- The skill does not depend on hidden local state or product-specific features.

## Design Guidance

The skill should be:

- **portable**: useful across agent runtimes;
- **operational**: tells agents exactly what to do;
- **safe**: protects branches, secrets, and high-risk decisions;
- **reviewable**: produces durable artifacts;
- **short at the entry point**: deep material belongs in references;
- **aligned with the CLI**: command examples must stay accurate.
