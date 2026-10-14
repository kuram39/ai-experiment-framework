# Human-agent workflow

## Starting a new question

1. Decide whether the work is a genuinely independent question or a continuation of an existing experiment.
2. For a new experiment, agree on a title, question, scope, and a testable hypothesis or explicit exploratory mode.
3. Before an authoritative run, specify the baseline, primary evaluation, supporting checks, and what counts as support, rejection, or inconclusive evidence.
4. Ask the agent to create the experiment using the skill or generator. Review the question and evaluation contract before analysis begins.

## Continuing an experiment

The agent reads applicable project instructions and the experiment's `README.md`, `OUTCOME.md`, and `STATE.json` when present. It establishes the current question, phase, last verified state, next step, and blockers before it changes files. It reads run indexes or detailed lifecycle guidance only when the task needs them.

The agent then performs the requested analysis, records a new run, updates the canonical document that owns any changed current result, and runs the structural validator before handoff. It does not create a sibling experiment just because another run is needed.

## Ending a session and resuming with another agent

Before ending, make the experiment resumable without chat:

- state what was actually run and what was not;
- link results to inputs, code, and a run receipt;
- update the current answer and its limits;
- leave one concrete next action and list real blockers;
- run the validator and report its actual result.

The next agent starts from those files, not from an assumed memory of the previous conversation. If a required fact is absent, it records the uncertainty or asks; it does not invent continuity.

To try that handoff in a fresh agent session, point it to the example folder and ask: “Continue this experiment from its saved state. Read the experiment instructions and current files first. Summarize what is supported, what is uncertain, and the next action. Do not change the existing run receipts.” The example is prepared for this check; the repository does not claim that a separate agent session has already performed it.

## Human responsibilities

The person remains responsible for choosing the research question, approving sensitive data use, deciding whether a result is fit for use, and authorizing external publication or irreversible actions. A skill is guidance for agent behavior; it is not permission to access, disclose, or mutate data.
