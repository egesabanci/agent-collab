# Agent Collab Documentation

This folder contains the detailed maintainer and implementation documentation for Agent Collab. The root `README.md` is the public landing page. These files explain how the repository is organized, how the Python package works, how the CLI maps to `.agent/` artifacts, and how the skill package should be maintained.

## Reading Order

| Document | Use it for |
| --- | --- |
| [Codebase Map](codebase-map.md) | A file-by-file tour of the repository. |
| [Architecture](architecture.md) | The system model, package boundaries, and data flow. |
| [CLI Reference](cli.md) | Command behavior, options, defaults, and generated files. |
| [Coordination Engine](coordination-engine.md) | Internal implementation details for `coordination.py`. |
| [Artifact Model](artifact-model.md) | The `.agent/` directory, generated templates, naming rules, and ownership rules. |
| [Skill Package](skill-package.md) | How `SKILL.md`, `references/`, and `agents/openai.yaml` fit together. |
| [Testing](testing.md) | Unit test coverage, validation strategy, and smoke tests. |
| [Development And Release](development-and-release.md) | Local setup, packaging, publishing, versioning, and maintenance workflow. |
| [Maintenance Checklist](maintenance-checklist.md) | Practical checklists for common repository changes. |

## Repository Layers

Agent Collab has four main layers:

1. **Public package layer**

   `pyproject.toml`, `README.md`, `LICENSE`, and `assets/` define how the project is presented, installed, licensed, and published.

2. **Agent skill layer**

   `SKILL.md`, `references/`, and `agents/openai.yaml` define the agent-facing protocol and optional runtime metadata.

3. **Python package layer**

   `src/agent_collab/cli.py` exposes the Typer CLI, while `src/agent_collab/coordination.py` creates `.agent/` artifacts.

4. **Quality layer**

   `tests/` verifies helper behavior, CLI behavior, artifact paths, generated content, and entry point wiring.

## Documentation Principles

- Keep the root `README.md` fast to scan.
- Put implementation and maintainer detail in `docs/`.
- Keep agent-facing operational rules in `SKILL.md` and `references/`.
- Keep docs aligned with generated artifact names and CLI defaults.
- Treat docs as part of the product surface: changes to commands, templates, or workflow rules should update docs in the same change.

## Quick Maintainer Commands

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 /path/to/quick_validate.py .
python3 -m build
python3 -m twine check dist/*
```

Use [Development And Release](development-and-release.md) for the full workflow.
