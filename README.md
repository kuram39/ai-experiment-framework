# AI Experiment Framework

**A practical workflow for people and AI agents working on data experiments.**

The framework keeps an experiment understandable after a chat ends. It separates the question and current conclusion from immutable run evidence, gives each artifact a clear role, and includes small tools to create and validate an experiment workspace.

It is not a data platform or an experiment-tracking service. It is a lightweight working method built from Markdown, JSON, ordinary files, and optional scripts.

## What is included

- [`skills/create-experiment/`](skills/create-experiment/SKILL.md): an agent skill for creating or continuing a durable experiment.
- [`scripts/create_experiment.py`](skills/create-experiment/scripts/create_experiment.py): creates a dated minimal scaffold without overwriting an existing experiment.
- [`scripts/validate_experiment.py`](skills/create-experiment/scripts/validate_experiment.py): checks structural conventions and selected artifact references.
- [`examples/2026-10-14_customer-analysis/`](examples/2026-10-14_customer-analysis/README.md): a worked churn-analysis example using synthetic data. It records an unsupported first hypothesis, a second analysis, and a handoff another agent can continue.
- [`docs/architecture.md`](docs/architecture.md) and [`docs/agent-workflow.md`](docs/agent-workflow.md): explain the model and the human-agent handoff.

## Quick start

Requirements: Python 3.10 or newer. The generator and validator use only the Python standard library.

Create a new experiment in an existing project directory:

```bash
python3 skills/create-experiment/scripts/create_experiment.py \
  --root /path/to/your/project \
  --title "Evaluate a data-quality rule" \
  --question "Does the new rule reduce invalid records without rejecting valid ones?" \
  --hypothesis "The rule lowers invalid records by at least 10% while false rejection stays below 2%." \
  --in-scope "Compare the rule with the current baseline on the supplied snapshot." \
  --out-of-scope "This experiment does not authorize production changes."
```

The generator creates a dated directory with `README.md`, `OUTCOME.md`, and `.gitignore`. It does not move or inspect your data, run the experiment, or publish anything. Add only the directories and files the work actually needs.

Install the skill by copying `skills/create-experiment/` into the skills directory supported by your agent. For Codex, a repository-local location is `.agents/skills/create-experiment/`; the user-level location is `~/.codex/skills/create-experiment/`. Other agent tools may use a different skills directory; check that tool's current documentation.

## Try the worked example

The example includes a deterministic synthetic CSV, its generating script, analysis code, two run receipts, and a current state. Follow [its reproduction guide](examples/2026-10-14_customer-analysis/README.md) from the example directory. The first hypothesis is not supported by the declared threshold; the second analysis finds a descriptive association in the synthetic data. Neither result establishes causation or says anything about real customers.

## Core idea

An experiment has two complementary views:

1. **Current view:** what is being asked, what the best-supported answer is now, which artifacts are current, and what to do next.
2. **Evidence ledger:** what each attempt did, what it found, what was used as evidence, and whether it remains authoritative.

The current view can be updated as knowledge improves. Run identity and original receipts remain stable. A verified candidate may replace a current artifact at its stable path; the transition and superseded evidence are recorded.

## Privacy and sharing

The worked example uses generated synthetic data only. Do not put private customer records, credentials, or confidential data into a public repository. Keep real experiment data in its proper local or access-controlled location; share only what is permitted and needed to explain the method.

## Language and licensing

The framework documentation is primarily in English, with a Czech summary below. The skill preserves the source workflow's convention that generated local experiment documents are in Czech; adapt that convention if your team uses another language.

This repository is licensed under the MIT License; see [LICENSE](LICENSE). The license text is the standard form published by the [Open Source Initiative](https://opensource.org/license/mit). Confirm that you have the right to share all included material before reusing or redistributing it.

## Český souhrn

AI Experiment Framework je lehký pracovní postup pro systematickou práci člověka a AI s datovými experimenty. Uchovává otázku, aktuální závěr, běhy a další krok tak, aby nový agent mohl navázat i po skončení konverzace. Obsahuje agentní skill, generátor a validátor struktury a reprodukovatelnou ukázku se syntetickými daty. Ukázka demonstruje dvě analýzy: první hypotéza neprojde předem stanoveným kritériem, druhá ukáže popisnou souvislost. Nejde o důkaz příčinnosti ani o analýzu skutečných zákazníků.
