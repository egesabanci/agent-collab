# Maintenance Checklist

Use this document as a practical checklist when changing Agent Collab.

## Before Any Change

- Confirm the task scope.
- Run `git status --short`.
- Check for unrelated user changes.
- Read the relevant source or docs before editing.
- Decide whether the change affects CLI behavior, generated artifacts, skill instructions, package metadata, or only docs.

## Documentation-Only Change

- Update the relevant Markdown file.
- Check links and paths.
- Keep root `README.md` concise.
- Put deep detail under `docs/` or `references/`.
- Run the skill validator if `SKILL.md` or `references/` changed.
- Run tests if commands, examples, or generated artifacts are described differently.

## CLI Behavior Change

- Update `src/agent_collab/cli.py`.
- Keep command functions thin.
- Add or update enums for constrained string values.
- Pass values to the coordination layer explicitly.
- Update `tests/test_cli.py`.
- Update `docs/cli.md`.
- Update root `README.md` if quick-start usage changes.

## Artifact Template Change

- Update `src/agent_collab/coordination.py`.
- Preserve conservative write behavior.
- Keep generated headings stable when possible.
- Update `tests/test_coordination.py`.
- Update `docs/artifact-model.md`.
- Update `references/artifacts-and-templates.md`.
- Consider whether `SKILL.md` needs a summary update.

## New Artifact Type

- Add an artifact directory only if the existing directories do not fit.
- Add a generator in `coordination.py`.
- Add a Typer command in `cli.py`.
- Add direct generator tests.
- Add CLI tests.
- Document file path, purpose, and lifecycle.
- Update skill references if agents should use the artifact.

## Skill Protocol Change

- Update the relevant file in `references/`.
- Update `SKILL.md` only for concise operational instructions.
- Keep the protocol runtime-neutral.
- Validate skill metadata.
- Update docs if maintainers need to know about the behavior.

## Package Metadata Change

- Update `pyproject.toml`.
- If the version changes, update `src/agent_collab/__init__.py`.
- Verify package build.
- Run `twine check`.
- Smoke-test install if publishing.

## Asset Change

- Keep assets in `assets/`.
- Use stable file names for README links.
- Remove unused generated variants.
- Keep binary assets reasonably sized.
- Verify README renders the intended asset path.

## Pre-Commit Checklist

```bash
git status --short
git diff --stat
python3 /path/to/quick_validate.py .
python3 -m pytest
```

If using the project virtual environment:

```bash
.venv/bin/python -m pytest
```

Confirm:

- no unrelated files are staged;
- generated docs and examples match actual commands;
- tests pass;
- skill validation passes when applicable;
- commit message follows conventional commits.

## Post-Commit Checklist

```bash
git log -1 --oneline
git status --short
```

If pushing:

```bash
git push origin main
```

After push, confirm:

- remote accepted the commit;
- worktree is clean except intentional local-only files;
- README image and docs links point to committed paths.
