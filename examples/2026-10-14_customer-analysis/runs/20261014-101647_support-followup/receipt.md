# Run receipt: support-case follow-up

- Status: completed
- Purpose: test whether the churn-rate difference between customers with 2+ and 0–1 recent support cases reached the predeclared 10 percentage-point threshold.
- Why this follow-up: the plan comparison did not meet its support threshold; the next analysis checks a different candidate factor, declared before this run.
- Command: `python3 src/analyze.py support`
- Input: `data/raw/customers.csv`; see `data/raw/MANIFEST.json` for its identity and hash.
- Code: `src/analyze.py`; Python standard library only.
- Started: 2026-10-14T10:16:47Z; duration 0.031330 seconds.
- Result: 2+ cases 67/251 = 26.69%; 0–1 cases 36/949 = 3.79%; difference = 22.90 percentage points.
- Verdict: the 10 percentage-point threshold was met in the synthetic data.
- Limits: descriptive group comparison; no uncertainty estimate, adjustment, or causal interpretation.
