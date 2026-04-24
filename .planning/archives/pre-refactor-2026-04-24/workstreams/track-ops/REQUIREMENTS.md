# Requirements — `track-ops`

## `v1.0` — Startup And Delivery Gate Reliability

### `OPS-01` Preflight Contract

Preflight must clearly report the minimum runtime prerequisites and current environment state.

### `OPS-02` Smoke-Check Reliability

Smoke-check must distinguish test failures from startup/boot failures and expose reliable status artifacts.

### `OPS-03` Restart Integrity

Restart flows must verify boot progress and preserve enough evidence to diagnose startup failures.

### `OPS-04` Operator State Truth

Control/status surfaces must report runtime state from canonical process and bootstrap facts rather than best guesses.

## `v1.1` — Scenario And Recovery Coverage

### `OPS-05` Scenario Taxonomy

Scenario coverage must be explicit enough to show which runtime behaviors are protected and which are not.

### `OPS-06` Recovery Suite

Recovery and resume flows need dedicated scenario/integration coverage rather than being inferred from happy-path tests.

### `OPS-07` Failure Artifacts

Scenario, restart, and smoke failures must leave consistent artifacts that explain what broke.

## `v1.2` — Diagnostics And Operator Workflow

### `OPS-08` Diagnostics Aggregation

Diagnostics must summarize runtime, session, and failure state in a way an operator can act on.

### `OPS-09` Operator Inspection

Operators need explicit inspection paths for audit/recovery state without digging into raw storage manually.

### `OPS-10` Gate Parity And Automation

Local checks, operator tooling, and future automation should agree on what “healthy” means.
