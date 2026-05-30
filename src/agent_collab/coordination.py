#!/usr/bin/env python3
"""Create .agent coordination artifacts for multi-agent repository work."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any, List, Optional


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


def command_init(args: Any) -> None:
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


def command_new_task(args: Any) -> None:
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


def command_handoff(args: Any) -> None:
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


def command_adr(args: Any) -> None:
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


def command_review(args: Any) -> None:
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


def command_test_report(args: Any) -> None:
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


def command_conflict(args: Any) -> None:
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


def command_merge_recommendation(args: Any) -> None:
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


def command_file_ownership(args: Any) -> None:
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


def command_human_decision(args: Any) -> None:
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
