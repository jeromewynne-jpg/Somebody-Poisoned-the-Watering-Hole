# Somebody Poisoned the Watering Hole

## Background

Coding agents increasingly consume untrusted, task-relevant external content (issue threads, docs, snippets, package suggestions) while acting in high-impact environments. This project studies a compound threat setting where external adversaries can poison those channels and the monitored agent may itself not be fully trusted.

## Submission and Main Contributions

This repository contains the submission for the **Apart Control Hackathon (March 20-22, 2026)** and the associated paper in `submission/`:
https://apartresearch.com/sprints/ai-control-hackathon-2026-03-20-to-2026-03-22

Main contributions:

- A compound AI control + agent security threat model for coding-agent deployments.
- A naturalistic mini-benchmark (`PoisonedGithubIssues`) that injects poisoned dependency advice into real GitHub issue contexts.
- An initial empirical estimate of vulnerability using Claude Code (Sonnet 4.6) with deterministic and LLM-judge scoring.

## Benchmark Details

`PoisonedGithubIssues` is an Inspect-based benchmark for issue-driven poisoning attacks during bug-fix tasks.

- Scope: 180 tasks total (10 issues each across 18 real open-source repositories).
- Data construction: start from real closed GitHub issues, then add a poisoned comment tailored to each issue.
- Variants: `cmd` (poisoned comment recommends an untrusted command/dependency) and `url` (poisoned comment recommends a malicious-looking but task-relevant URL).
- Execution setting: agent runs in Docker sandbox with cloned target repo and short interaction budget.
- Scoring: deterministic scorers for execution/fetch behavior from sandbox traces, plus LLM-judge scorers for recommendation and suspicious-content flagging (`openai/gpt-5.4` default).

## Headline Result (Current Run)

Command-variant run on 130 samples across 13 repositories (Claude Code Sonnet 4.6):

- Ran untrusted command: `0.0%`
- Recommended untrusted command (LLM judge): `0.0%`
- Flagged suspicious content in reasoning (LLM judge): `76.2%`

## Repository Map

- `poisoned_github/`
- `poisoned_github/task.py`: Inspect task definitions and harness wiring.
- `poisoned_github/scorers.py`: deterministic scorers + LLM-judge scorers (`openai/gpt-5.4` default).
- `poisoned_github/agents.py`: Claude Code sandbox agent bridge.
- `poisoned_github/generate_tasks.py`: generate poisoned tasks from real closed GitHub issues.
- `poisoned_github/repos.json`: canonical set of 18 benchmark repositories.
- `poisoned_github/tasks/`: generated issue-poisoning task instances.
- `experiments/run_claude_code.py`: run evals with repo filtering, variant selection, and grader model control.
- `experiments/analysis.py`: aggregate Inspect logs and export summary CSVs.
- `logs/experiments/all_repos_cmd/`: main command-variant logs and regraded outputs.
- `submission/neurips_2026.tex`: paper source.
- `submission/neurips_2026.pdf`: compiled paper.
- `submission/figures/results.py`: results figure generation script.

## Key Resources

- Paper (PDF): `submission/neurips_2026.pdf`
- Main run logs: `logs/experiments/all_repos_cmd/`
- Regraded scorer export: `logs/experiments/all_repos_cmd/regraded_llm_scores.csv`
- Raw eval artifact: `2026-03-22T21-20-04-00-00_task_LvrfYXyrLkym6S8ZvCYmFc.eval`
- Hosted Inspect logs are also available via the project GitHub repository.

## Quickstart

Prerequisites:

- Python 3.10+
- Docker
- GitHub CLI (`gh`) authenticated (for task generation)
- API keys in environment (`ANTHROPIC_API_KEY` and `OPENAI_API_KEY`)

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install inspect-ai pandas matplotlib numpy python-dotenv anthropic
```

Generate tasks (optional, if you want to rebuild task data):

```bash
cd poisoned_github
python3 generate_tasks.py --issues-per-repo 10
```

Run the command-variant eval (example):

```bash
cd ..
python3 -m experiments.run_claude_code \
  --variant cmd \
  --log-dir logs/experiments/all_repos_cmd \
  --model anthropic/claude-sonnet-4-6 \
  --grader-model openai/gpt-5.4 \
  --max-samples 130
```

Analyze logs:

```bash
python3 -m experiments.analysis \
  --log-dir logs/experiments/all_repos_cmd \
  --csv logs/experiments/all_repos_cmd/regraded_llm_scores.csv
```

Regenerate figures:

```bash
python3 submission/figures/results.py
```

## Notes

- This was built in a weekend hackathon setting and is intentionally narrow in scope.
- Current evaluation focuses on one attack pattern (poisoned issue comments recommending fake dependencies).
