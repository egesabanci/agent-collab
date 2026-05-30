from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agent_collab import cli, coordination


runner = CliRunner()


def invoke(args):
    result = runner.invoke(cli.app, args)
    assert result.exit_code == 0, result.output
    return result


def test_cli_help_lists_all_commands():
    result = invoke(["--help"])
    for command in [
        "init",
        "new-task",
        "handoff",
        "adr",
        "review",
        "test-report",
        "conflict",
        "merge-recommendation",
        "file-ownership",
        "human-decision",
    ]:
        assert command in result.output


def test_cli_init_and_new_task(tmp_path):
    invoke(
        [
            "init",
            "--root",
            str(tmp_path),
            "--project",
            "demo",
            "--active-task",
            "TASK-001-demo-task",
            "--phase",
            "implementation",
            "--protected-branches",
            "main,production",
        ]
    )
    invoke(
        [
            "new-task",
            "--root",
            str(tmp_path),
            "--id",
            "TASK-001",
            "--title",
            "Demo Task",
            "--owner",
            "coordinator",
            "--risk",
            "high",
            "--check",
            "lint",
            "--check",
            "tests",
        ]
    )

    status = json.loads((tmp_path / ".agent/status.json").read_text())
    assert status["project"] == "demo"
    assert status["protected_branches"] == ["main", "production"]

    task_text = (tmp_path / ".agent/tasks/TASK-001-demo-task.md").read_text()
    assert "coordinator" in task_text
    assert "- [ ] lint" in task_text
    assert "- [ ] tests" in task_text


def test_cli_artifact_commands(tmp_path, monkeypatch):
    monkeypatch.setattr(coordination, "today", lambda: "2026-05-30")
    monkeypatch.setattr(coordination, "timestamp", lambda: "2026-05-30-1200")
    root = str(tmp_path)

    commands = [
        [
            "handoff",
            "--root",
            root,
            "--task",
            "TASK-001-demo-task",
            "--role",
            "implementer",
            "--branch",
            "agent/impl/TASK-001-demo-task",
            "--worktree",
            "../repo-implementer",
        ],
        [
            "review",
            "--root",
            root,
            "--task",
            "TASK-001-demo-task",
            "--branch",
            "agent/impl/TASK-001-demo-task",
            "--status",
            "changes_requested",
            "--recommendation",
            "request_changes",
        ],
        [
            "test-report",
            "--root",
            root,
            "--task",
            "TASK-001-demo-task",
            "--branch",
            "agent/impl/TASK-001-demo-task",
            "--recommendation",
            "needs_fix",
        ],
        [
            "adr",
            "--root",
            root,
            "--number",
            "1",
            "--title",
            "Use Server-Side API Wrapper",
        ],
        [
            "conflict",
            "--root",
            root,
            "--task",
            "TASK-001-demo-task",
            "--title",
            "API Client and Auth Changes",
            "--type",
            "semantic",
            "--requires-human",
            "yes",
        ],
        ["file-ownership", "--root", root, "--task", "TASK-001-demo-task"],
        [
            "human-decision",
            "--root",
            root,
            "--task",
            "TASK-001-demo-task",
            "--title",
            "Choose Auth Boundary",
            "--risk",
            "high",
        ],
        [
            "merge-recommendation",
            "--root",
            root,
            "--task",
            "TASK-001-demo-task",
            "--recommendation",
            "needs_human_decision",
            "--risk",
            "high",
            "--human-approval-required",
            "yes",
        ],
    ]

    for command in commands:
        result = invoke(command)
        assert "[write]" in result.output

    expected = [
        ".agent/handoffs/TASK-001-demo-task-implementer-2026-05-30-1200.md",
        ".agent/reviews/TASK-001-demo-task-review-2026-05-30-1200.md",
        ".agent/test-reports/TASK-001-demo-task-test-report-2026-05-30-1200.md",
        ".agent/decisions/ADR-001-use-server-side-api-wrapper.md",
        ".agent/risks/TASK-001-demo-task-conflict-api-client-and-auth-changes.md",
        ".agent/protocols/file-ownership-TASK-001-demo-task.md",
        ".agent/risks/TASK-001-demo-task-human-decision-choose-auth-boundary.md",
        ".agent/reviews/TASK-001-demo-task-merge-recommendation-2026-05-30-1200.md",
    ]

    for relative_path in expected:
        assert (tmp_path / relative_path).is_file()


def test_cli_rejects_invalid_enum_value(tmp_path):
    result = runner.invoke(
        cli.app,
        [
            "new-task",
            "--root",
            str(tmp_path),
            "--id",
            "TASK-001",
            "--title",
            "Demo Task",
            "--risk",
            "extreme",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_module_entrypoint_imports_main():
    assert callable(cli.main)
    assert Path("src/agent_collab/__main__.py").is_file()
