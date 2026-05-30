from __future__ import annotations

from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional

import typer

from . import coordination


class Risk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class HandoffStatus(str, Enum):
    completed = "completed"
    partially_completed = "partially_completed"
    blocked = "blocked"
    needs_review = "needs_review"
    needs_tests = "needs_tests"


class ReviewStatus(str, Enum):
    approved = "approved"
    changes_requested = "changes_requested"
    blocked = "blocked"
    needs_human_decision = "needs_human_decision"


class ReviewRecommendation(str, Enum):
    approve = "approve"
    request_changes = "request_changes"
    split_task = "split_task"
    abandon = "abandon"
    escalate = "escalate"


class TestRecommendation(str, Enum):
    merge_ready = "merge_ready"
    needs_fix = "needs_fix"
    needs_more_tests = "needs_more_tests"
    needs_human_decision = "needs_human_decision"


class ConflictType(str, Enum):
    semantic = "semantic"
    textual = "textual"
    architectural = "architectural"
    dependency = "dependency"
    test = "test"
    unknown = "unknown"


class YesNo(str, Enum):
    yes = "yes"
    no = "no"


class MergeRecommendation(str, Enum):
    merge = "merge"
    do_not_merge = "do_not_merge"
    needs_changes = "needs_changes"
    needs_human_decision = "needs_human_decision"


app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Create Agent Collab .agent coordination artifacts.",
)


def _root(root: Optional[Path]) -> Optional[str]:
    return str(root) if root else None


@app.command()
def init(
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    project: Optional[str] = typer.Option(None, help="Project name for .agent/status.json."),
    active_task: Optional[str] = typer.Option(None, help="Active task id for .agent/status.json."),
    phase: str = typer.Option("planning", help="Current coordination phase."),
    protected_branches: str = typer.Option(
        "main,master,production,staging", help="Comma-separated protected branches."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create the .agent directory structure."""
    coordination.command_init(
        SimpleNamespace(
            root=_root(root),
            project=project,
            active_task=active_task,
            phase=phase,
            protected_branches=protected_branches,
            force=force,
        )
    )


@app.command()
def new_task(
    id: str = typer.Option(..., "--id", help="Task id, such as TASK-001."),
    title: str = typer.Option(..., "--title", help="Human-readable task title."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    owner: str = typer.Option("unassigned", help="Task owner or role."),
    status: str = typer.Option("planned", help="Initial task status."),
    risk: Risk = typer.Option(Risk.low, help="Task risk level."),
    check: Optional[List[str]] = typer.Option(
        None, "--check", help="Required check. Repeat the option for multiple checks."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a task file under .agent/tasks."""
    coordination.command_new_task(
        SimpleNamespace(
            root=_root(root),
            id=id,
            title=title,
            owner=owner,
            status=status,
            risk=risk.value,
            check=check,
            force=force,
        )
    )


@app.command()
def handoff(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    role: str = typer.Option(..., "--role", help="Agent role writing the handoff."),
    branch: str = typer.Option(..., "--branch", help="Branch being handed off."),
    worktree: str = typer.Option(..., "--worktree", help="Worktree path for the branch."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    status: HandoffStatus = typer.Option(HandoffStatus.needs_review, help="Handoff status."),
    next_agent: str = typer.Option("reviewer", help="Suggested next agent role."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a handoff template under .agent/handoffs."""
    coordination.command_handoff(
        SimpleNamespace(
            root=_root(root),
            task=task,
            role=role,
            branch=branch,
            worktree=worktree,
            status=status.value,
            next_agent=next_agent,
            force=force,
        )
    )


@app.command()
def adr(
    number: int = typer.Option(..., "--number", help="ADR number."),
    title: str = typer.Option(..., "--title", help="ADR title."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create an ADR template under .agent/decisions."""
    coordination.command_adr(
        SimpleNamespace(root=_root(root), number=number, title=title, force=force)
    )


@app.command()
def review(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    branch: str = typer.Option(..., "--branch", help="Branch reviewed."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    reviewer: str = typer.Option("reviewer", help="Reviewer name or role."),
    status: ReviewStatus = typer.Option(ReviewStatus.blocked, help="Review status."),
    recommendation: ReviewRecommendation = typer.Option(
        ReviewRecommendation.request_changes, help="Final review recommendation."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a review template under .agent/reviews."""
    coordination.command_review(
        SimpleNamespace(
            root=_root(root),
            task=task,
            branch=branch,
            reviewer=reviewer,
            status=status.value,
            recommendation=recommendation.value,
            force=force,
        )
    )


@app.command()
def test_report(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    branch: str = typer.Option(..., "--branch", help="Branch tested."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    tester: str = typer.Option("tester", help="Tester name or role."),
    recommendation: TestRecommendation = typer.Option(
        TestRecommendation.needs_more_tests, help="Test recommendation."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a test report template under .agent/test-reports."""
    coordination.command_test_report(
        SimpleNamespace(
            root=_root(root),
            task=task,
            branch=branch,
            tester=tester,
            recommendation=recommendation.value,
            force=force,
        )
    )


@app.command()
def conflict(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    title: str = typer.Option(..., "--title", help="Conflict title."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    type: ConflictType = typer.Option(ConflictType.unknown, "--type", help="Conflict type."),
    requires_human: YesNo = typer.Option(
        YesNo.no, "--requires-human", help="Whether the conflict needs a human decision."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a conflict note under .agent/risks."""
    coordination.command_conflict(
        SimpleNamespace(
            root=_root(root),
            task=task,
            title=title,
            type=type.value,
            requires_human=requires_human.value,
            force=force,
        )
    )


@app.command()
def merge_recommendation(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    recommendation: MergeRecommendation = typer.Option(
        MergeRecommendation.needs_changes, help="Final merge recommendation."
    ),
    risk: Risk = typer.Option(Risk.medium, help="Risk level."),
    human_approval_required: YesNo = typer.Option(
        YesNo.yes, "--human-approval-required", help="Whether human approval is required."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a final merge recommendation under .agent/reviews."""
    coordination.command_merge_recommendation(
        SimpleNamespace(
            root=_root(root),
            task=task,
            recommendation=recommendation.value,
            risk=risk.value,
            human_approval_required=human_approval_required.value,
            force=force,
        )
    )


@app.command()
def file_ownership(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a file ownership map under .agent/protocols."""
    coordination.command_file_ownership(
        SimpleNamespace(root=_root(root), task=task, force=force)
    )


@app.command()
def human_decision(
    task: str = typer.Option(..., "--task", help="Task key, such as TASK-001-api-client."),
    title: str = typer.Option(..., "--title", help="Decision title."),
    root: Optional[Path] = typer.Option(
        None, "--root", "-r", help="Repository root. Defaults to git root or current directory."
    ),
    risk: Risk = typer.Option(Risk.medium, help="Decision risk level."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Create a human decision note under .agent/risks."""
    coordination.command_human_decision(
        SimpleNamespace(
            root=_root(root), task=task, title=title, risk=risk.value, force=force
        )
    )


def main() -> None:
    app()
