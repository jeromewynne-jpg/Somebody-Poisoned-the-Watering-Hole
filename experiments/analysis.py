#!/usr/bin/env python3
"""
Analyse PoisonedGithub eval results.

Loads Inspect AI eval logs and produces summary statistics:
  1. Overall accuracy and stderr per scorer
  2. Per-repo breakdown
  3. Cross-tabulation (recommended despite flagging)
  4. Per-sample CSV export

Usage:
  python3 -m experiments.analysis --log-dir logs/experiments/2repos_cmd
  python3 -m experiments.analysis --log-dir logs/experiments/2repos_cmd --csv results.csv
"""

import argparse
from pathlib import Path

import pandas as pd
from inspect_ai.analysis import samples_df, score_to_float, prepare

# Scorer column names as they appear in the DataFrame (score_ prefix)
SCORE_COLUMNS = [
    "score_ran_command_scorer",
    "score_fetched_url_scorer",
    "score_recommended_command_scorer",
    "score_recommended_url_scorer",
    "score_alerted_user_scorer",
    "score_flagged_in_reasoning_scorer",
    "score_llm_recommended_command_scorer",
    "score_llm_flagged_in_reasoning_scorer",
]

DISPLAY_NAMES = {
    "score_ran_command_scorer": "Ran command",
    "score_fetched_url_scorer": "Fetched URL",
    "score_recommended_command_scorer": "Recommended command",
    "score_recommended_url_scorer": "Recommended URL",
    "score_alerted_user_scorer": "Alerted user",
    "score_flagged_in_reasoning_scorer": "Flagged in reasoning",
    "score_llm_recommended_command_scorer": "LLM Recommended command",
    "score_llm_flagged_in_reasoning_scorer": "LLM Flagged in reasoning",
}


def load_results(log_dir: str) -> pd.DataFrame:
    """Load eval logs into a DataFrame with numeric score columns."""
    df = samples_df(log_dir)
    present = [c for c in SCORE_COLUMNS if c in df.columns]
    if present:
        df = prepare(df, [score_to_float(present)])
    return df


def present_scorers(df: pd.DataFrame) -> list[str]:
    """Return scorer column names that exist in the DataFrame."""
    return [s for s in SCORE_COLUMNS if s in df.columns]


def overall_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean accuracy and stderr for each scorer."""
    scorers = present_scorers(df)
    rows = []
    for s in scorers:
        col = df[s].dropna()
        rows.append({
            "Scorer": DISPLAY_NAMES.get(s, s),
            "N": int(len(col)),
            "Accuracy": col.mean(),
            "Stderr": col.sem(),
        })
    return pd.DataFrame(rows)


def per_repo_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Compute accuracy per scorer grouped by repo."""
    scorers = present_scorers(df)
    if "metadata_repo" not in df.columns:
        return pd.DataFrame()
    grouped = df.groupby("metadata_repo")[scorers].mean()
    grouped.columns = [DISPLAY_NAMES.get(c, c) for c in grouped.columns]
    return grouped


def cross_tabulation(df: pd.DataFrame) -> None:
    """Show how often the agent recommends despite flagging as suspicious."""
    rec_col = None
    for candidate in [
        "score_llm_recommended_command_scorer",
        "score_recommended_command_scorer",
        "score_recommended_url_scorer",
    ]:
        if candidate in df.columns:
            rec_col = candidate
            break

    flag_col = None
    for candidate in [
        "score_llm_flagged_in_reasoning_scorer",
        "score_flagged_in_reasoning_scorer",
    ]:
        if candidate in df.columns:
            flag_col = candidate
            break

    if rec_col is None or flag_col is None:
        print("Cross-tabulation: required columns not present\n")
        return

    both = df[[rec_col, flag_col]].dropna()
    flagged = both[flag_col] == 1.0
    recommended = both[rec_col] == 1.0

    n = len(both)
    if n == 0:
        print("Cross-tabulation: no data\n")
        return

    n_flagged = int(flagged.sum())
    n_recommended = int(recommended.sum())
    n_flagged_and_recommended = int((flagged & recommended).sum())
    n_flagged_not_recommended = int((flagged & ~recommended).sum())

    print("CROSS-TABULATION: Recommended vs Flagged in Reasoning")
    print(f"  Using recommendation scorer:      {DISPLAY_NAMES.get(rec_col, rec_col)}")
    print(f"  Using flagging scorer:            {DISPLAY_NAMES.get(flag_col, flag_col)}")
    print(f"  Total samples:                    {n}")
    print(f"  Flagged in reasoning:             {n_flagged} ({n_flagged/n:.0%})")
    print(f"  Recommended to user:              {n_recommended} ({n_recommended/n:.0%})")
    print(f"  Flagged AND recommended:          {n_flagged_and_recommended} ({n_flagged_and_recommended/n:.0%})")
    print(f"  Flagged but NOT recommended:      {n_flagged_not_recommended} ({n_flagged_not_recommended/n:.0%})")
    if n_flagged > 0:
        print(f"  Recommend rate among flagged:     {n_flagged_and_recommended/n_flagged:.0%}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Analyse PoisonedGithub eval results")
    parser.add_argument("--log-dir", required=True, help="Path to eval log directory")
    parser.add_argument("--csv", default=None, help="Export per-sample results to CSV")
    args = parser.parse_args()

    if not Path(args.log_dir).exists():
        print(f"Log directory not found: {args.log_dir}")
        return

    print(f"Loading logs from {args.log_dir}...\n")
    df = load_results(args.log_dir)
    print(f"Loaded {len(df)} samples\n")

    # 1. Overall summary
    summary = overall_summary(df)
    print("OVERALL SUMMARY")
    print(summary.to_string(index=False, float_format="%.3f"))
    print()

    # 2. Per-repo breakdown
    repo_df = per_repo_breakdown(df)
    if not repo_df.empty:
        print("PER-REPO BREAKDOWN")
        print(repo_df.to_string(float_format="%.2f"))
        print()

    # 3. Cross-tabulation
    cross_tabulation(df)

    # 4. CSV export
    if args.csv:
        scorers = present_scorers(df)
        export_cols = ["id", "eval_id"]
        for meta in ["metadata_repo", "metadata_language"]:
            if meta in df.columns:
                export_cols.append(meta)
        export_cols.extend(scorers)
        if "total_time" in df.columns:
            export_cols.append("total_time")

        export_cols = [c for c in export_cols if c in df.columns]
        df[export_cols].to_csv(args.csv, index=False)
        print(f"Per-sample results exported to {args.csv}")


if __name__ == "__main__":
    main()
