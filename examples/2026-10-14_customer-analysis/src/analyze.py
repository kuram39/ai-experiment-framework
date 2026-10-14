#!/usr/bin/env python3
"""Run one of the example's predeclared descriptive comparisons."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "customers.csv"


def load_rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize(rows: list[dict[str, str]], key_fn) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        grouped[key_fn(row)].append(int(row["churned"]))
    return {
        name: {"n": len(values), "churned": sum(values), "rate": sum(values) / len(values)}
        for name, values in sorted(grouped.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comparison", choices=("plan", "support"))
    args = parser.parse_args()
    rows = load_rows()
    if args.comparison == "plan":
        groups = summarize(rows, lambda row: row["plan"])
        difference = groups["monthly"]["rate"] - groups["annual"]["rate"]
        threshold = 0.05
        print("Comparison: monthly minus annual churn rate")
    else:
        groups = summarize(
            rows,
            lambda row: "2+ cases" if int(row["support_cases_last_90d"]) >= 2 else "0-1 cases",
        )
        difference = groups["2+ cases"]["rate"] - groups["0-1 cases"]["rate"]
        threshold = 0.10
        print("Comparison: 2+ support cases minus 0-1 cases churn rate")
    for label, result in groups.items():
        print(
            f"{label}: n={result['n']}, churned={result['churned']}, "
            f"rate={result['rate']:.4f} ({result['rate']:.1%})"
        )
    print(f"risk_difference={difference:.4f} ({difference:.1%})")
    print(f"predeclared_support_threshold={threshold:.1%}")
    print(f"threshold_met={abs(difference) >= threshold if args.comparison == 'plan' else difference >= threshold}")
    print("Interpretation: descriptive association only; no causal claim or uncertainty estimate.")


if __name__ == "__main__":
    main()
