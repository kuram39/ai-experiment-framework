# Architecture

## One research question, two views

An experiment is one evolving research question. It is not a folder per chat session and not a permanent archive of every byte produced.

### Current view

- `README.md` owns the question, scope, current phase, navigation, reproduction instructions, and one concrete next step.
- `OUTCOME.md` owns the current evidence-based answer and its limits.
- `STATE.json` is optional. Add it when evolving structured artifacts need exact machine-readable pointers and hashes.
- Stable semantic paths hold current code and canonical artifacts. A logical artifact has at most one current materialization.

### Evidence ledger

- `runs/INDEX.md` lists attempts and their authority status.
- Each run has a new timestamped identity and an original receipt. Do not edit a past run to make it appear to be the current result.
- `DECISION.md` records an actual decision and its evidence, if one is made.
- Publication receipts are append-only when the user actually publishes something.

## Artifact lifecycle

```text
working -> candidate -> current -> superseded -> pruned
```

Create a candidate in a run or scratch space, validate it against the declared evaluation contract, and then promote it to the stable current path. Record why the previous authority was superseded. Pruning is a separate decision: first establish that no current work or publication depends on the bytes and that retention, license, privacy, and audit constraints permit removal.

## Grow from real content

The initial scaffold is intentionally small. Add `data/raw/` for an actual immutable input; `src/` for a real experiment script; `runs/` for a real attempt; `reports/` for a produced report; and `STATE.json` when a current artifact needs structured tracking. Do not make empty directories just because they appear in a conventional data-science tree.

## Provenance and claims

Record enough information to understand and, where feasible, reproduce a result: source or snapshot identity, integrity hash, command, configuration, runtime, code revision or fingerprint, outputs, and evaluation criteria. State what is evidence, what is inferred, and what remains unknown. Keep raw inputs immutable while active; scripts should write derived outputs elsewhere.

## What the tools guarantee

The generator creates a starting structure and refuses to overwrite an existing target. The validator checks structure and selected consistency conditions. Neither tool determines whether a research question is good, a result is valid, an artifact should be promoted, or data may legally be shared. Those remain human and agent responsibilities.
