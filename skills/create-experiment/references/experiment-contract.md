# Detailed experiment contract

This is the conditional lifecycle playbook. Load only the sections relevant to
the current work. It is a self-contained reference for this framework; runtime
use does not depend on an original template or its path.

## Grow the structure from real content

Do not create a directory or document merely because it appears in this table.

| first real event | create |
|---|---|
| immutable input | `data/raw/` and `data/raw/MANIFEST.json` |
| freely recomputable intermediate | `data/interim/` |
| canonical data output | `data/processed/` and an artifact manifest when needed |
| first evolving canonical artifact or promotion | `STATE.json` |
| experiment script | `src/`; each script must run independently |
| run | `runs/YYYYMMDD-HHMMSS_slug/` and `runs/INDEX.md` |
| produced report | `reports/` |
| consumed source material | `references/` |
| testable code | `tests/` |
| external-side-effect or data-pull script | `tools/` |
| temporary working trace | `.scratch/` |
| actual decision | `DECISION.md` |
| publication preparation | `handoff/README.md` |
| first real publication | `handoff/PUBLISHED.md` |
| experiment-specific durable agent rules | `AGENTS.md` |

`README.md` owns human navigation and reproduction, `OUTCOME.md` owns current
conclusions, optional `STATE.json` owns machine-readable current pointers, and
`DECISION.md` owns decisions. Never create two documents for one role.

Before adding another artifact, establish:

1. whether the information already exists in a canonical file that should be
   updated;
2. which lifecycle layer owns it;
3. whether it is temporary (`.scratch/`) or durable;
4. whether it is local history or a candidate for later sharing;
5. who will read it and what would invalidate it;
6. whether it creates a competing source of truth.

## Current view and evidence ledger

The current view is deliberately replaceable:

- `README.md`: current phase, navigation, reproduction, and next action;
- `OUTCOME.md`: current answer, scope, evidence, and limits;
- `STATE.json`: current run and exact current artifact identities when the
  experiment has evolving structured artifacts;
- `data/processed/`: one current materialization per logical output;
- `src/`: code currently needed to reproduce, validate, or continue the work.

The evidence ledger is durable but compact:

- `runs/INDEX.md`: every attempt, authority status, result, and replacement;
- retained run receipts: purpose, config, fingerprints, result, and pruning;
- `DECISION.md`: decisions and reversal conditions;
- `handoff/PUBLISHED.md`: append-only publication receipts.

Do not preserve stale bytes merely to make the folder look complete. Do not
delete the only evidence supporting a current or published claim merely to make
the folder small.

### Optional `STATE.json`

Create `STATE.json` with the first canonical artifact that will evolve or the
first candidate promotion. Do not create it as an empty scaffold. Minimum
shape:

```json
{
  "schema_version": 1,
  "updated_at": "YYYY-MM-DDThh:mm:ss+02:00",
  "phase": "data | baseline | variants | evaluation | closed",
  "current_run": "runs/YYYYMMDD-HHMMSS_slug",
  "current_artifacts": [
    {
      "id": "stable-kebab-case-id",
      "role": "current_input | canonical_output | work_queue | config | code",
      "path": "data/processed/artifact.json",
      "sha256": "...",
      "produced_by": "runs/YYYYMMDD-HHMMSS_slug"
    }
  ],
  "next_action": "one concrete action",
  "blockers": []
}
```

`current_run` and `produced_by` may be `null` when an externally supplied
artifact has not yet been produced by a run. Paths are experiment-relative.
`STATE.json` has no historical artifact list; history belongs to the ledger.
Update it only after the candidate and repository copy have been verified.

## Promotion and retirement

An artifact moves through:

```text
working -> candidate -> current -> superseded -> pruned
```

1. Produce a candidate in a new run or `.scratch/`; do not overwrite the
   current artifact while evaluating it.
2. Validate the candidate against the experiment's evaluation contract.
3. Promote it to the existing stable semantic path under `data/processed/` or
   the appropriate current layer. Update `STATE.json`, its manifest, README,
   and OUTCOME together.
4. Mark the previous authority `SUPERSEDED` in `runs/INDEX.md`, name its
   replacement, and state what remains valid and why it is no longer current.
5. Prune retired bytes only after the retirement gate passes.

Promotion is a state transition, not a filename convention. Never create
`artifact-v2.json`, `artifact-final.json`, or `latest-artifact.json` merely to
avoid replacing the canonical path.

### Retirement gate

Before deleting a raw snapshot, processed artifact, script, or run payload,
verify all of the following:

1. a verified replacement is current, or the path was conclusively rejected;
2. no current artifact, next action, publication, decision, or active benchmark
   depends on the bytes;
3. the durable conclusion, scope, and reason for retirement are recorded;
4. the removed material is identified by path/class and, when meaningful,
   SHA-256, record count, and source snapshot;
5. the ledger names `superseded_by` when a replacement exists;
6. sensitivity, license, contractual, and audit retention allow deletion.

If any condition is unknown, retain the bytes or ask. Deletion is not implied
by marking an artifact superseded.

Use the minimum retention tier justified by future use:

| tier | when | retain |
|---|---|---|
| full | supports current work, a publication, benchmark, or active decision | inputs, code/config, output, validation, and provenance |
| receipt | superseded but still explains a decision or rejected path | purpose, input/code identities, config, compact result, verdict, replacement, and pruning record |
| index-only | failed or diagnostic path with no remaining evidentiary use | one `runs/INDEX.md` entry stating what was tried, learned, and why the payload was removed |

Deleting bytes reduces reproducibility. Never describe a receipt-only or
index-only run as fully reproducible.

## Immutable inputs and provenance

A raw snapshot is immutable **while active**. Code in `src/` never edits it in
place. Acquire a replacement as a candidate, run dependent validation, and
only then promote the replacement and retire the old snapshot. An inactive raw
snapshot may be pruned after the retirement gate; its identity and reason for
removal remain in the manifest or run ledger.

`data/raw/MANIFEST.json` describes the active input set and records retired
input identities when the bytes are no longer retained. It must identify the
exact input, origin, integrity, sensitivity, and sharing boundary.

Minimum schema:

```json
{
  "schema_version": 1,
  "created_at": "YYYY-MM-DDThh:mm:ss+02:00",
  "purpose": "why these inputs exist",
  "acquisition": "copied | exported | referenced",
  "source": "path, URL, system, commit, or snapshot id",
  "source_created_at": "YYYY-MM-DDThh:mm:ssZ",
  "sensitivity": "public | internal | pii",
  "sharing": "what may be published and what must stay local",
  "license_or_terms": "when relevant",
  "files": {
    "input.json": {
      "bytes": 0,
      "sha256": "...",
      "records": 0
    }
  },
  "retired": [
    {
      "path": "previous-input.json",
      "sha256": "...",
      "retired_at": "YYYY-MM-DDThh:mm:ss+02:00",
      "reason": "why it is no longer used",
      "superseded_by": "input.json"
    }
  ]
}
```

For a pointer to another experiment, hash the referenced input as though it had
been copied. An absolute path alone is not provenance.

A manifest for a generated canonical or expensive artifact also records the
generating command, code version, hashes of all dependent inputs, output files
with size and SHA-256, regeneration procedure, runtime, and any cost or external
service. Canonical status and regeneration cost are independent properties.

## Run contract

Every execution starts with a new run directory and immutable run identity:

```text
runs/YYYYMMDD-HHMMSS_slug/
```

Do not use a descriptive name without the timestamp. A `run_id` or parameter
hash may be part of the slug but never replaces temporal identity. The run ID,
original receipt, and result are immutable. Later authority or retention
transitions must state their reason and replacement rather than rewriting the
old evidence. The directory's bulky outputs are not automatically permanent.

Each run preserves its config and at least this provenance:

```json
{
  "schema_version": 1,
  "status": "completed | failed | interrupted",
  "purpose": "why the run exists",
  "started_at": "YYYY-MM-DDThh:mm:ss+02:00",
  "duration_s": 0.0,
  "argv": ["python3", "src/run.py"],
  "runtime": {
    "python": "CPython 3.x",
    "platform": "...",
    "dependencies": "lockfile sha256 or standard-library-only"
  },
  "config": {},
  "seed": null,
  "code": {
    "kind": "git | fingerprint",
    "revision": "commit+dirty or sha256 over src/*.py"
  },
  "inputs": {
    "dataset": "sha256 or manifest sha256"
  },
  "outputs": ["metrics.json"]
}
```

In a Git repository, record the commit and dirty state. Outside Git, store a
`code_fingerprint` as SHA-256 over `src/*.py`. Fingerprint imported code from
another experiment or shared module as well. Write the config schema version
into each actual config rather than leaving it as an unused code constant.

Create `runs/INDEX.md` with the first run. For every run, record its purpose,
input, change, result, verdict, replacement, and retention:

```markdown
| WHEN | RUN | AUTHORITY | PURPOSE | INPUT | CHANGE | RESULT | REPLACED BY | RETENTION |
|---|---|---|---|---|---|---|---|---|
```

`AUTHORITY` is `AUTHORITATIVE`, `SUPERSEDED`, `INVALID`, or `DIAGNOSTIC`.
`RETENTION` is `FULL`, `RECEIPT`, or `INDEX_ONLY`. Technical `completed`,
`failed`, or `interrupted` belongs in the run config. When either ledger value
changes, preserve the original result and record why, when, and—if applicable—
by which run it was replaced.

For a pruned receipt, retain or add a compact `PRUNED.json` before deleting the
payload:

```json
{
  "schema_version": 1,
  "pruned_at": "YYYY-MM-DDThh:mm:ss+02:00",
  "reason": "why the payload has no future use",
  "superseded_by": "runs/YYYYMMDD-HHMMSS_slug or null",
  "removed": [
    {"path": "detail.json", "sha256": "...", "bytes": 0}
  ],
  "retained": ["run.json", "metrics-summary.json"]
}
```

If even a receipt has no future reader, remove the directory and keep an
`INDEX_ONLY` row. Publication receipts are never pruned by this rule.

## Conclusions and epistemic hygiene

`OUTCOME.md` is the replaceable current synthesis, not a chronological log.
Each question has exactly one `##` section with a direct answer, evidence,
confidence, validity scope, limits, self-check, impact, canonical artifacts,
and next step. When evidence changes the answer, rewrite the answer and keep
only the concise supersession fact needed to understand why the old path is no
longer current; detailed chronology belongs in `runs/INDEX.md`.

Use these exact Czech labels in Czech experiment documents:

- `jisté`: directly supported by an input, file, run, or cited source;
- `odvozené`: reasoning derived from supported facts;
- `nejisté`: material uncertainty that could change the decision;
- `bez zdroje`: a factual claim without an available source.

When the answer is unknown, write `otevřeno` and state what is missing. Never
invent a complete-looking conclusion. Before handoff, explicitly record possible
errors and assumptions in the same question section; if none remain, say so.

## Decisions and publication

Create `DECISION.md` only after a real decision. Record date, scope, decision,
evidence, considered alternatives, consequences, and the reversal condition.
Link to `OUTCOME.md` instead of duplicating the conclusions.

Create `handoff/README.md` only while preparing a publication. State what goes
out, what remains local, and why. Create `handoff/PUBLISHED.md` only after the
first real publication; it is append-only and records date, source and target
paths, commit or PR, and what remained local. Creating an experiment never
authorizes publication by itself.

Publication is a separate workflow. Creating an experiment never authorizes
copying its data or artifacts into a shared knowledge base or public
repository.

## Heavy directories in synchronized locations

Gitignore does not protect a filesystem synchronization service. When an
experiment lives in a synchronized tree, physical dependencies and agent
worktrees may need to live outside that tree. If using links, verify the target
and ensure collaborators can resolve it. For example:

```bash
mkdir -p ~/Code/<local-heavy-storage>/<experiment>/<component>
ln -s ~/Code/<local-heavy-storage>/<experiment>/<component> <path-in-experiment>
```

Resolve and verify the exact target before creating a link. Never replace
existing content.

## End-of-session check

- The experiment is resumable without chat and README names the next action.
- When evolving canonical artifacts exist, `STATE.json` identifies their exact
  current paths and hashes and agrees with README and OUTCOME.
- No `{{...}}` placeholders, empty documents, or empty directories remain.
- Local links resolve.
- Commands described as verified were actually run.
- Every run appears in `runs/INDEX.md` with authority and retention. Every full
  or receipt-tier run preserves the provenance appropriate to its tier.
- `OUTCOME.md` has one section per answered question and a self-check in each.
- If a decision occurred, `DECISION.md` exists.
- README identifies canonical or expensive artifacts and their regeneration.
- Heavy regenerable trees are not physically inside synchronized storage.
- A real publication has an append-only receipt; no publication means no
  receipt.
- Every deletion passed the retirement gate and left the promised receipt or
  index-only explanation.
- No competing source of truth was introduced.
