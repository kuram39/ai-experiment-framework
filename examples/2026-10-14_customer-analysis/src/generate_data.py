#!/usr/bin/env python3
"""Generate the example's deterministic, wholly synthetic customer table."""

from __future__ import annotations

import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "customers.csv"
SEED = 20261014
ROWS = 1200


def main() -> None:
    rng = random.Random(SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "customer_id",
                "plan",
                "tenure_months",
                "support_cases_last_90d",
                "churned",
            ],
        )
        writer.writeheader()
        for index in range(1, ROWS + 1):
            plan = rng.choice(("monthly", "annual"))
            tenure = rng.randint(1, 60)
            support_cases = rng.choices((0, 1, 2, 3, 4), weights=(50, 30, 13, 5, 2))[0]
            churn_probability = 0.04
            if tenure < 6:
                churn_probability += 0.10
            if support_cases >= 2:
                churn_probability += 0.26
            churned = int(rng.random() < churn_probability)
            writer.writerow(
                {
                    "customer_id": f"synthetic-{index:04d}",
                    "plan": plan,
                    "tenure_months": tenure,
                    "support_cases_last_90d": support_cases,
                    "churned": churned,
                }
            )
    print(f"Generated {ROWS} synthetic rows at {OUTPUT.relative_to(ROOT)} (seed={SEED}).")


if __name__ == "__main__":
    main()
