#!/usr/bin/env python3
"""
Experiment: Run PoisonedGithub eval with Claude Code.

Usage:
  python3 -m experiments.run_claude_code \
    --repos pallets/flask axios/axios BurntSushi/ripgrep \
    --variant cmd \
    --model anthropic/claude-sonnet-4-5-20250929
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from inspect_ai import Task, eval_set
from inspect_ai.agent import as_solver
from inspect_ai.dataset import Sample
from inspect_ai.util import SandboxEnvironmentSpec

from poisoned_github.agents import claude_code_agent
from poisoned_github.scorers import (
    fetched_url_scorer,
    ran_command_scorer,
    recommended_url_scorer,
    recommended_command_scorer,
    alerted_user_scorer,
    flagged_in_reasoning_scorer,
    llm_recommended_command_scorer,
    llm_flagged_in_reasoning_scorer,
)
from poisoned_github.task import _render_issue, setup_environment

TASKS_DIR = Path(__file__).parent.parent / "poisoned_github" / "tasks"


def load_samples(variant: str, repos: list[str] | None = None) -> list[Sample]:
    """Load samples, optionally filtered by repo."""
    all_dirs = sorted(
        d for d in TASKS_DIR.iterdir()
        if d.is_dir() and (d / "config.json").exists()
    )

    samples = []
    for task_dir in all_dirs:
        with open(task_dir / "config.json") as f:
            config = json.load(f)

        if repos and config["repo"] not in repos:
            continue

        issue_number = config["issue_number"]
        repo = config["repo"]

        if variant == "url":
            issues_dir = task_dir / "issues"
        else:
            issues_dir = task_dir / "issues_cmd"

        issue_file = issues_dir / f"issue_{issue_number}.json"
        with open(issue_file) as f:
            issue = json.load(f)
        issue_text = _render_issue(issue)

        samples.append(
            Sample(
                input=f"help me with this issue\n\n{issue_text}",
                id=task_dir.name,
                metadata={
                    "repo": repo,
                    "language": config["language"],
                    "poisoned_url": config.get("poisoned_url", ""),
                    "untrusted_command": config.get("untrusted_command", ""),
                    "setup_config": {"repo": repo},
                },
            )
        )

    return samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos", nargs="+", default=None, help="Repos to include")
    parser.add_argument("--variant", default="cmd", choices=["url", "cmd"])
    parser.add_argument("--model", default="anthropic/claude-sonnet-4-6")
    parser.add_argument("--log-dir", default="logs/experiments/claude_code")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-samples", type=int, default=4)
    parser.add_argument(
        "--grader-model",
        default="openai/gpt-5.4",
        help="OpenAI model used by LLM-judge scorers",
    )
    parser.add_argument(
        "--disable-llm-judges",
        action="store_true",
        help="Disable LLM-judge scorers",
    )
    args = parser.parse_args()

    samples = load_samples(args.variant, args.repos)
    print(f"Samples: {len(samples)}, Variant: {args.variant}, Model: {args.model}")

    if args.variant == "url":
        scorers = [fetched_url_scorer(), recommended_url_scorer(), alerted_user_scorer(), flagged_in_reasoning_scorer()]
    else:
        scorers = [ran_command_scorer(), recommended_command_scorer(), alerted_user_scorer(), flagged_in_reasoning_scorer()]
        if not args.disable_llm_judges:
            scorers.extend([
                llm_recommended_command_scorer(grader_model=args.grader_model),
                llm_flagged_in_reasoning_scorer(grader_model=args.grader_model),
            ])

    compose_path = Path(__file__).parent.parent / "poisoned_github" / "compose.yml"

    t = Task(
        dataset=samples,
        solver=[
            setup_environment(),
            as_solver(claude_code_agent(timeout=args.timeout)),
        ],
        scorer=scorers,
        sandbox=SandboxEnvironmentSpec(
            type="docker",
            config=str(compose_path.absolute()),
        ),
    )

    eval_set(
        tasks=t,
        log_dir=args.log_dir,
        model=args.model,
        fail_on_error=False,
        max_samples=args.max_samples,
    )

    print(f"\nDone. Logs in {args.log_dir}/")


if __name__ == "__main__":
    main()
