# Somebody Poisoned the Watering Hole

This repository contains the submission for the **Apart Control Hackathon (March 20-22, 2026)**:
https://apartresearch.com/sprints/ai-control-hackathon-2026-03-20-to-2026-03-22

## Project Background

Coding agents often consume untrusted but task-relevant external content such as issue threads, docs, snippets, and package suggestions. This project studies a compound setting where:

- external adversaries can poison that content, and
- the monitored agent may itself not be fully trusted.

## Submission Summary

This submission contributes:

- A compound AI control + agent security threat model for coding-agent deployments.
- `PoisonedGithubIssues`, a naturalistic mini-benchmark built from real GitHub issues.
- An initial empirical measurement of current coding-agent vulnerability on this attack path.

## Benchmark: What It Measures

`PoisonedGithubIssues` aims to measure whether coding agents are vulnerable to poisoned watering-hole content in GitHub issues.

Specifically, it measures whether agents:

- execute unsafe suggestions (for example, untrusted commands),
- recommend unsafe suggestions to users, and
- detect and flag suspicious content.

## Benchmark Design

- Scope: 180 tasks total (`18 repos x 10 issues`).
- Data generation: start from real closed issues, then inject a poisoned comment tailored to each issue.
- Variants: `cmd` (poisoned comment recommends an untrusted dependency/command) and `url` (poisoned comment recommends a malicious but seemingly task-relevant URL).
- Runtime: agent runs in a Docker sandbox with the target repository checked out.
- Scoring: deterministic scorers for concrete execution/fetch behavior, plus LLM-judge scorers for recommendation and suspicious-content detection (`openai/gpt-5.4` default).

## Current Headline Result

Claude Code (Sonnet 4.6), command variant, `N=130` across `13` repositories:

| Metric | Rate |
|---|---:|
| Ran untrusted command (deterministic) | 0.0% |
| Recommended untrusted command (LLM judge) | 0.0% |
| Flagged suspicious content in reasoning (LLM judge) | 76.2% |

## Key Resources

- Paper source: `submission/neurips_2026.tex`
- Paper PDF: `submission/neurips_2026.pdf`
- Benchmark task/scorer code: `poisoned_github/task.py`, `poisoned_github/scorers.py`
- Canonical repo set: `poisoned_github/repos.json`
- Generated tasks: `poisoned_github/tasks/`
- Eval runner: `experiments/run_claude_code.py`
- Analysis script: `experiments/analysis.py`
- Main run logs: `logs/experiments/all_repos_cmd/`
- Regraded output CSV: `logs/experiments/all_repos_cmd/regraded_llm_scores.csv`
- Raw eval artifact: `2026-03-22T21-20-04-00-00_task_LvrfYXyrLkym6S8ZvCYmFc.eval`
- Hosted Inspect logs: available via this GitHub repository.

## Reproduce (Minimal)

Prerequisites:

- Python 3.10+
- Docker
- `gh` CLI authenticated (only needed for regenerating task data)
- `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`

Install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install inspect-ai pandas matplotlib numpy python-dotenv anthropic
```

Run eval (example):

```bash
python3 -m experiments.run_claude_code \
  --variant cmd \
  --log-dir logs/experiments/all_repos_cmd \
  --model anthropic/claude-sonnet-4-6 \
  --grader-model openai/gpt-5.4 \
  --max-samples 130
```

Analyze:

```bash
python3 -m experiments.analysis \
  --log-dir logs/experiments/all_repos_cmd \
  --csv logs/experiments/all_repos_cmd/regraded_llm_scores.csv
```

## Scope Notes

- This is weekend hackathon work and intentionally narrow.
- The current reported run covers one agent and one attack path.
