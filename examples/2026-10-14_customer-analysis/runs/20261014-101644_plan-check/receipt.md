# Run receipt: plan comparison

- Status: completed
- Purpose: check whether monthly-plan churn exceeded annual-plan churn by the predeclared 5 percentage-point threshold.
- Command: `python3 src/analyze.py plan`
- Input: `data/raw/customers.csv`; see `data/raw/MANIFEST.json` for its identity and hash.
- Code: `src/analyze.py`; Python standard library only.
- Started: 2026-10-14T10:16:44Z; duration 0.030213 seconds.
- Result: annual 59/617 = 9.56%; monthly 44/583 = 7.55%; monthly minus annual = -2.02 percentage points.
- Verdict: threshold not met; the directional hypothesis was not supported.
- Limits: descriptive group comparison; no uncertainty estimate, adjustment, or causal interpretation.
