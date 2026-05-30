#!/usr/bin/env python3
"""Create .agent coordination artifacts for multi-agent repository work."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import List, Optional


AGENT_DIRS = [
    "tasks",
    "handoffs",
    "decisions",
    "reviews",
    "test-reports",
    "risks",
    "protocols",
    "scratch",
]


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")


def normalize_task_key(task: str, title: str = "") -> str:
    raw = re.sub(r"[^A-Za-z0-9-]+", "-", task.strip()).strip("-")
    if not raw:
        raise ValueError("task id cannot be empty")
    if not raw.upper().startswith("TASK-"):
        raw = f"TASK-{raw}"
    match = re.match(r"(?i)^(TASK-\d+)(?:-(.*))?$", raw)
    if match:
        prefix = match.group(1).upper()
        existing_slug = match.group(2) or ""
    else:
        prefix = raw.upper()
        existing_slug = ""
    slug = slugify(title) if title else slugify(existing_slug)
    return f"{prefix}-{slug}" if slug else prefix


def display_task_id(task_key: str) -> str:
    match = re.match(r"^(TASK-\d+)(?:-(.*))?$", task_key)
    if not match:
        return task_key
    if not match.group(2):
        return match.group(1)
    return f"{match.group(1)}: {match.group(2).replace('-', ' ').title()}"


def split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def repo_root(path: Optional[str]) -> Path:
    if path:
        return Path(path).expanduser().resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(result.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


def ensure_agent_dirs(root: Path) -> Path:
    base = root / ".agent"
    base.mkdir(exist_ok=True)
    for name in AGENT_DIRS:
        (base / name).mkdir(exist_ok=True)
    return base


def write_new(path: Path, content: str, force: bool = False) -> None:
    if path.exists() and not force:
        print(f"[skip] {path} already exists")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip(), encoding="utf-8")
    print(f"[write] {path}")


def command_init(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    project = args.project or root.name
    status = {
        "project": project,
        "active_task": args.active_task,
        "current_phase": args.phase,
        "protected_branches": split_csv(args.protected_branches),
        "agents": {},
        "merge_status": {
            "ready": False,
            "blocked_by": [
                "implementation handoff pending",
                "review pending",
                "test evidence pending",
            ],
        },
    }
    readme = f"""
    # Agent Coordination

    This directory is the repository source of truth for multi-agent work.

    - `status.json` tracks active task, phase, assigned agents, and merge status.
    - `tasks/` contains scoped task definitions and acceptance criteria.
    - `handoffs/` contains implementation, documentation, blocked, and role handoffs.
    - `decisions/` contains ADRs for architectural decisions.
    - `reviews/` contains structured reviewer output.
    - `test-reports/` contains verification evidence.
    - `risks/` contains conflicts, blockers, and risk notes.
    - `protocols/` contains file ownership maps and task-specific coordination rules.
    - `scratch/` is temporary and must not be treated as durable project truth.

    Protected branches: {", ".join(status["protected_branches"])}
    """
    write_new(base / "README.md", dedent(readme), args.force)
    write_new(base / "status.json", json.dumps(status, indent=2) + "\n", args.force)


def command_new_task(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.id, args.title)
    title = args.title.strip()
    branches = [
        f"agent/architect/{task_key}",
        f"agent/impl/{task_key}",
        f"agent/review/{task_key}",
        f"agent/test/{task_key}",
        f"agent/docs/{task_key}",
        f"agent/integration/{task_key}",
    ]
    checks = args.check or ["lint", "typecheck", "unit tests", "build"]
    content = f"""
    # {display_task_id(task_key)}

    ## Status

    {args.status}

    ## Owner

    {args.owner}

    ## Related branches

    {chr(10).join(f"- {branch}" for branch in branches)}

    ## Goal

    {title}

    ## Non-goals

    - TODO

    ## Context

    TODO

    ## Scope

    ### In scope

    - TODO

    ### Out of scope

    - TODO

    ## Acceptance criteria

    - [ ] TODO

    ## Required checks

    {chr(10).join(f"- [ ] {check}" for check in checks)}

    ## Risk level

    {args.risk}

    ## Known risks

    - TODO

    ## Dependencies

    - TODO

    ## Open questions

    ### Blocking

    - None currently documented.

    ### Non-blocking

    - None currently documented.

    ### Suggestions

    - None currently documented.

    ### Assumptions

    - None currently documented.

    ## Final result

    Fill after merge, rejection, or cancellation.
    """
    write_new(base / "tasks" / f"{task_key}.md", dedent(content), args.force)


def command_handoff(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    role = slugify(args.role)
    content = f"""
    # Handoff: {display_task_id(task_key)}

    ## Agent role

    {args.role}

    ## Date

    {today()}

    ## Branch

    {args.branch}

    ## Worktree

    {args.worktree}

    ## Status

    {args.status}

    ## Summary

    TODO

    ## Files changed

    - `path/to/file` - TODO

    ## Behavioral changes

    TODO

    ## Architectural changes

    TODO

    ## Commands run

    ```bash
    # TODO
    ```

    ## Verification results

    - lint: not run
    - typecheck: not run
    - tests: not run
    - build: not run

    ## Failing checks

    None currently documented.

    ## Assumptions

    - TODO

    ## Risks

    - TODO

    ## Open questions

    ### Blocking

    - None currently documented.

    ### Non-blocking

    - None currently documented.

    ### Suggestions

    - None currently documented.

    ### Assumptions

    - TODO

    ## Reviewer instructions

    TODO

    ## Tester instructions

    TODO

    ## Suggested next agent

    {args.next_agent}

    ## Rollback notes

    TODO

    ## Additional notes

    TODO
    """
    file_name = f"{task_key}-{role}-{timestamp()}.md"
    write_new(base / "handoffs" / file_name, dedent(content), args.force)


def command_adr(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    number = str(args.number).zfill(3)
    slug = slugify(args.title)
    content = f"""
    # ADR-{number}: {args.title}

    ## Status

    proposed

    ## Date

    {today()}

    ## Context

    TODO

    ## Decision

    TODO

    ## Alternatives considered

    ### Option A

    Pros:

    - TODO

    Cons:

    - TODO

    ### Option B

    Pros:

    - TODO

    Cons:

    - TODO

    ## Consequences

    ### Positive

    - TODO

    ### Negative

    - TODO

    ### Neutral

    - TODO

    ## Migration notes

    TODO

    ## Follow-up tasks

    - TASK-...
    """
    write_new(base / "decisions" / f"ADR-{number}-{slug}.md", dedent(content), args.force)


def command_review(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    content = f"""
    # Review: {display_task_id(task_key)}

    ## Reviewer

    {args.reviewer}

    ## Branch reviewed

    {args.branch}

    ## Review status

    {args.status}

    ## Summary

    TODO

    ## Correctness

    TODO

    ## Architecture

    TODO

    ## Security

    TODO

    ## Reliability

    TODO

    ## Maintainability

    TODO

    ## Test coverage

    TODO

    ## Required changes

    - [ ] TODO

    ## Suggested improvements

    - TODO

    ## Files requiring attention

    - `path/to/file` - TODO

    ## Human decision needed?

    no

    ## Human decision details

    None currently documented.

    ## Final recommendation

    {args.recommendation}
    """
    file_name = f"{task_key}-review-{timestamp()}.md"
    write_new(base / "reviews" / file_name, dedent(content), args.force)


def command_test_report(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    content = f"""
    # Test Report: {display_task_id(task_key)}

    ## Tester

    {args.tester}

    ## Branch tested

    {args.branch}

    ## Environment

    - OS:
    - Runtime:
    - Package manager:
    - Database:
    - Relevant env vars:

    ## Commands run

    ```bash
    # TODO
    ```

    ## Results

    | Check | Result | Notes |
    | --- | --- | --- |
    | install | not run | |
    | lint | not run | |
    | typecheck | not run | |
    | unit tests | not run | |
    | integration tests | not run | |
    | build | not run | |
    | manual smoke test | not run | |

    ## Failures

    None currently documented.

    ## Suspected cause

    TODO

    ## Reproduction steps

    1. TODO

    ## Coverage gaps

    TODO

    ## Recommendation

    {args.recommendation}
    """
    file_name = f"{task_key}-test-report-{timestamp()}.md"
    write_new(base / "test-reports" / file_name, dedent(content), args.force)


def command_conflict(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    slug = slugify(args.title)
    content = f"""
    # Conflict: {args.title}

    ## Task

    {task_key}

    ## Branches involved

    - TODO

    ## Files in conflict

    - `path/to/file`

    ## Conflict type

    {args.type}

    ## Summary

    TODO

    ## Recommended resolution

    TODO

    ## Requires human decision?

    {args.requires_human}
    """
    write_new(base / "risks" / f"{task_key}-conflict-{slug}.md", dedent(content), args.force)


def command_merge_recommendation(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    content = f"""
    # Final Merge Recommendation: {display_task_id(task_key)}

    ## Recommendation

    {args.recommendation}

    ## Summary

    TODO

    ## Evidence

    ### Implementation handoff

    - .agent/handoffs/...

    ### Review

    - .agent/reviews/...

    ### Test report

    - .agent/test-reports/...

    ## Checks

    | Check | Result |
    | --- | --- |
    | lint | not run |
    | typecheck | not run |
    | tests | not run |
    | build | not run |

    ## Risk level

    {args.risk}

    ## Remaining risks

    - TODO

    ## Rollback plan

    TODO

    ## Human approval required?

    {args.human_approval_required}

    ## Next step

    TODO
    """
    file_name = f"{task_key}-merge-recommendation-{timestamp()}.md"
    write_new(base / "reviews" / file_name, dedent(content), args.force)


def command_file_ownership(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    content = f"""
    # File Ownership: {display_task_id(task_key)}

    ## Purpose

    Define which agents own which paths for this task so parallel work stays reviewable and conflicts are surfaced early.

    ## Backend implementer

    Owns:

    - TODO

    Must not edit:

    - TODO

    ## Frontend implementer

    Owns:

    - TODO

    Must not edit:

    - TODO

    ## Tester

    Owns:

    - TODO

    Must not edit implementation unless assigned.

    ## Integration assumptions

    - TODO

    ## Dependencies between branches

    - TODO

    ## Expected merge order

    1. TODO

    ## Known conflict areas

    - TODO
    """
    file_name = f"file-ownership-{task_key}.md"
    write_new(base / "protocols" / file_name, dedent(content), args.force)


def command_human_decision(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    base = ensure_agent_dirs(root)
    task_key = normalize_task_key(args.task)
    slug = slugify(args.title)
    content = f"""
    # Human Decision Needed: {args.title}

    ## Task

    {task_key}

    ## Context

    TODO

    ## Why this needs a human decision

    TODO

    ## Options

    ### Option A

    Pros:

    - TODO

    Cons:

    - TODO

    ### Option B

    Pros:

    - TODO

    Cons:

    - TODO

    ## Recommendation

    TODO

    ## Risk

    {args.risk}

    ## Default safe action

    TODO
    """
    file_name = f"{task_key}-human-decision-{slug}.md"
    write_new(base / "risks" / file_name, dedent(content), args.force)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root. Defaults to git root or cwd.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create .agent directory structure.")
    init_parser.add_argument("--project")
    init_parser.add_argument("--active-task")
    init_parser.add_argument("--phase", default="planning")
    init_parser.add_argument("--protected-branches", default="main,master,production,staging")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=command_init)

    task_parser = subparsers.add_parser("new-task", help="Create a task file.")
    task_parser.add_argument("--id", required=True)
    task_parser.add_argument("--title", required=True)
    task_parser.add_argument("--owner", default="unassigned")
    task_parser.add_argument("--status", default="planned")
    task_parser.add_argument("--risk", default="low", choices=["low", "medium", "high"])
    task_parser.add_argument("--check", action="append", help="Required check. Repeatable.")
    task_parser.add_argument("--force", action="store_true")
    task_parser.set_defaults(func=command_new_task)

    handoff_parser = subparsers.add_parser("handoff", help="Create a handoff template.")
    handoff_parser.add_argument("--task", required=True)
    handoff_parser.add_argument("--role", required=True)
    handoff_parser.add_argument("--branch", required=True)
    handoff_parser.add_argument("--worktree", required=True)
    handoff_parser.add_argument(
        "--status",
        default="needs_review",
        choices=["completed", "partially_completed", "blocked", "needs_review", "needs_tests"],
    )
    handoff_parser.add_argument("--next-agent", default="reviewer")
    handoff_parser.add_argument("--force", action="store_true")
    handoff_parser.set_defaults(func=command_handoff)

    adr_parser = subparsers.add_parser("adr", help="Create an ADR template.")
    adr_parser.add_argument("--number", required=True)
    adr_parser.add_argument("--title", required=True)
    adr_parser.add_argument("--force", action="store_true")
    adr_parser.set_defaults(func=command_adr)

    review_parser = subparsers.add_parser("review", help="Create a review template.")
    review_parser.add_argument("--task", required=True)
    review_parser.add_argument("--branch", required=True)
    review_parser.add_argument("--reviewer", default="reviewer")
    review_parser.add_argument(
        "--status",
        default="blocked",
        choices=["approved", "changes_requested", "blocked", "needs_human_decision"],
    )
    review_parser.add_argument(
        "--recommendation",
        default="request_changes",
        choices=["approve", "request_changes", "split_task", "abandon", "escalate"],
    )
    review_parser.add_argument("--force", action="store_true")
    review_parser.set_defaults(func=command_review)

    test_parser = subparsers.add_parser("test-report", help="Create a test report template.")
    test_parser.add_argument("--task", required=True)
    test_parser.add_argument("--branch", required=True)
    test_parser.add_argument("--tester", default="tester")
    test_parser.add_argument(
        "--recommendation",
        default="needs_more_tests",
        choices=["merge_ready", "needs_fix", "needs_more_tests", "needs_human_decision"],
    )
    test_parser.add_argument("--force", action="store_true")
    test_parser.set_defaults(func=command_test_report)

    conflict_parser = subparsers.add_parser("conflict", help="Create a conflict note.")
    conflict_parser.add_argument("--task", required=True)
    conflict_parser.add_argument("--title", required=True)
    conflict_parser.add_argument(
        "--type",
        default="unknown",
        choices=["semantic", "textual", "architectural", "dependency", "test", "unknown"],
    )
    conflict_parser.add_argument("--requires-human", default="no", choices=["yes", "no"])
    conflict_parser.add_argument("--force", action="store_true")
    conflict_parser.set_defaults(func=command_conflict)

    merge_parser = subparsers.add_parser(
        "merge-recommendation", help="Create a final merge recommendation."
    )
    merge_parser.add_argument("--task", required=True)
    merge_parser.add_argument(
        "--recommendation",
        default="needs_changes",
        choices=["merge", "do_not_merge", "needs_changes", "needs_human_decision"],
    )
    merge_parser.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    merge_parser.add_argument("--human-approval-required", default="yes", choices=["yes", "no"])
    merge_parser.add_argument("--force", action="store_true")
    merge_parser.set_defaults(func=command_merge_recommendation)

    ownership_parser = subparsers.add_parser(
        "file-ownership", help="Create a file ownership map template."
    )
    ownership_parser.add_argument("--task", required=True)
    ownership_parser.add_argument("--force", action="store_true")
    ownership_parser.set_defaults(func=command_file_ownership)

    decision_parser = subparsers.add_parser(
        "human-decision", help="Create a human decision note."
    )
    decision_parser.add_argument("--task", required=True)
    decision_parser.add_argument("--title", required=True)
    decision_parser.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    decision_parser.add_argument("--force", action="store_true")
    decision_parser.set_defaults(func=command_human_decision)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
