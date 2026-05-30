from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from agent_collab import coordination


def ns(**kwargs):
    defaults = {
        "root": None,
        "force": False,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_slug_and_task_helpers():
    assert coordination.slugify(" API Client & Auth!! ") == "api-client-auth"
    assert coordination.normalize_task_key("1", "API Client Refactor") == "TASK-1-api-client-refactor"
    assert coordination.normalize_task_key("task-002-api-client") == "TASK-002-api-client"
    assert coordination.display_task_id("TASK-002-api-client") == "TASK-002: Api Client"
    assert coordination.display_task_id("CUSTOM") == "CUSTOM"
    assert coordination.split_csv("main, production, , staging") == [
        "main",
        "production",
        "staging",
    ]


def test_normalize_task_key_rejects_empty_id():
    with pytest.raises(ValueError, match="task id cannot be empty"):
        coordination.normalize_task_key("   ")


def test_repo_root_uses_explicit_path(tmp_path):
    assert coordination.repo_root(str(tmp_path)) == tmp_path.resolve()


def test_write_new_skips_existing_file_unless_forced(tmp_path, capsys):
    path = tmp_path / "note.md"
    coordination.write_new(path, "first")
    coordination.write_new(path, "second")
    assert path.read_text() == "first"
    assert "[skip]" in capsys.readouterr().out

    coordination.write_new(path, "second", force=True)
    assert path.read_text() == "second"


def test_init_creates_agent_tree_and_status(tmp_path):
    coordination.command_init(
        ns(
            root=str(tmp_path),
            project="demo",
            active_task="TASK-001-demo",
            phase="implementation",
            protected_branches="main,production",
        )
    )

    agent_dir = tmp_path / ".agent"
    for directory in coordination.AGENT_DIRS:
        assert (agent_dir / directory).is_dir()

    status = json.loads((agent_dir / "status.json").read_text())
    assert status["project"] == "demo"
    assert status["active_task"] == "TASK-001-demo"
    assert status["current_phase"] == "implementation"
    assert status["protected_branches"] == ["main", "production"]
    assert status["merge_status"]["ready"] is False
    assert "implementation handoff pending" in status["merge_status"]["blocked_by"]


def test_new_task_creates_task_with_defaults_and_checks(tmp_path):
    coordination.command_new_task(
        ns(
            root=str(tmp_path),
            id="TASK-001",
            title="API Client Refactor",
            owner="implementer",
            status="planned",
            risk="medium",
            check=["lint", "tests"],
        )
    )

    path = tmp_path / ".agent/tasks/TASK-001-api-client-refactor.md"
    text = path.read_text()
    assert "# TASK-001: Api Client Refactor" in text
    assert "implementer" in text
    assert "- [ ] lint" in text
    assert "- [ ] tests" in text
    assert "agent/impl/TASK-001-api-client-refactor" in text


def test_artifact_generators_create_expected_files(tmp_path, monkeypatch):
    monkeypatch.setattr(coordination, "today", lambda: "2026-05-30")
    monkeypatch.setattr(coordination, "timestamp", lambda: "2026-05-30-1200")

    root = str(tmp_path)
    coordination.command_handoff(
        ns(
            root=root,
            task="TASK-001-demo-task",
            role="implementer",
            branch="agent/impl/TASK-001-demo-task",
            worktree="../repo-implementer",
            status="needs_review",
            next_agent="reviewer",
        )
    )
    coordination.command_adr(ns(root=root, number=1, title="Use Server-Side API Wrapper"))
    coordination.command_review(
        ns(
            root=root,
            task="TASK-001-demo-task",
            branch="agent/impl/TASK-001-demo-task",
            reviewer="reviewer",
            status="blocked",
            recommendation="request_changes",
        )
    )
    coordination.command_test_report(
        ns(
            root=root,
            task="TASK-001-demo-task",
            branch="agent/impl/TASK-001-demo-task",
            tester="tester",
            recommendation="needs_more_tests",
        )
    )
    coordination.command_conflict(
        ns(
            root=root,
            task="TASK-001-demo-task",
            title="API Client and Auth Changes",
            type="architectural",
            requires_human="yes",
        )
    )
    coordination.command_merge_recommendation(
        ns(
            root=root,
            task="TASK-001-demo-task",
            recommendation="needs_changes",
            risk="medium",
            human_approval_required="yes",
        )
    )
    coordination.command_file_ownership(ns(root=root, task="TASK-001-demo-task"))
    coordination.command_human_decision(
        ns(root=root, task="TASK-001-demo-task", title="Choose Auth Boundary", risk="high")
    )

    expected_files = {
        ".agent/handoffs/TASK-001-demo-task-implementer-2026-05-30-1200.md": [
            "## Agent role",
            "implementer",
            "../repo-implementer",
            "reviewer",
        ],
        ".agent/decisions/ADR-001-use-server-side-api-wrapper.md": [
            "# ADR-001: Use Server-Side API Wrapper",
            "2026-05-30",
        ],
        ".agent/reviews/TASK-001-demo-task-review-2026-05-30-1200.md": [
            "## Review status",
            "blocked",
        ],
        ".agent/test-reports/TASK-001-demo-task-test-report-2026-05-30-1200.md": [
            "## Recommendation",
            "needs_more_tests",
        ],
        ".agent/risks/TASK-001-demo-task-conflict-api-client-and-auth-changes.md": [
            "architectural",
            "yes",
        ],
        ".agent/reviews/TASK-001-demo-task-merge-recommendation-2026-05-30-1200.md": [
            "needs_changes",
            "medium",
        ],
        ".agent/protocols/file-ownership-TASK-001-demo-task.md": [
            "# File Ownership: TASK-001: Demo Task",
            "Expected merge order",
        ],
        ".agent/risks/TASK-001-demo-task-human-decision-choose-auth-boundary.md": [
            "# Human Decision Needed: Choose Auth Boundary",
            "high",
        ],
    }

    for relative_path, snippets in expected_files.items():
        text = (tmp_path / relative_path).read_text()
        for snippet in snippets:
            assert snippet in text
