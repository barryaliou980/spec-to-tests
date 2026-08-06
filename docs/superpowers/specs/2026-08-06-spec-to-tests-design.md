# Design — spec-to-tests

Date: 2026-08-06 · Status: approved by Aliou · Version target: 1.0.0

## Goal

Turn a list of features into a complete, **verified-red** test harness — and
stop there. The skill writes tests only. It never writes production code, not
even a stub: the missing module is the expected failure.

This gives a human or another agent an executable contract to implement
against, produced in one pass.

## Non-goals

- **No production code.** No implementation, no stub, no empty class, no type
  shim to "make the import resolve". A passing test at the end of the run is an
  anomaly to report, not a success.
- **No chaining into implementation.** The skill ends with a report and an
  explicit hand-off command. It does not offer to "go green".
- **No test-quality rulebook of its own.** Assertion quality is delegated to
  `superpowers:test-driven-development` → `writing-good-tests.md`.
- **No feature-table management.** If the user has a `FEATURES.md`, read it;
  do not create, migrate, or maintain it. That is `feature-status-tracker`'s job.

## Why a separate skill

`superpowers:test-driven-development` writes *one* test, then immediately
implements. That is the right loop when you own the whole cycle. It does not
produce a standing test harness as a deliverable.

`feature-status-tracker` clarifies features then develops them end to end;
tests are an internal step, not an output.

The gap: **freeze an executable contract for a batch of features, then hand
implementation off.** That is this skill.

## Decisions (from brainstorming)

- **Name:** `spec-to-tests` — names the transformation, and triggers better on
  "generate the tests for these features" than a method-based name would.
- **Framing method:** full boundary value analysis. For every input, identify
  valid/invalid equivalence partitions, then test the edges. Not a plain
  input/output spec.
- **Test levels:** unit tests on the logic, plus one acceptance test per feature
  describing end-to-end user-visible behavior. No integration tier — it would
  require the skill to negotiate containers, fixtures and DB seeding, which is
  out of scope for v1.0.0.
- **Stack:** auto-detected. Existing test files win over dependency manifests.
  Ask only when the project has neither.
- **Exit:** stop after verifying red, with an explicit hand-off. The report names
  the files created, the expected failure per test, and the command to continue.
- **Architecture:** standalone plugin (option A), added to the `aliou-skills`
  marketplace. Composable — `feature-status-tracker` may delegate to it later
  from its Phase 3.
- **Language:** `SKILL.md` in English, matching the two published skills.
  Bilingual EN/FR triggering in the `description`.

## Workflow

```
Phase 0 : Context      → detect runner + conventions; VERIFY the existing
                         suite is green (baseline)
Phase 1 : Intake       → feature list (chat, file, or FST table);
                         clarify one feature at a time
Phase 2 : Contracts    → per feature: equivalence partitions, boundary values,
                         expected outputs and errors
                         → write docs/test-contracts/<slug>.md
         ─── GATE: user validates the contracts before any test is written ───
Phase 3 : Generation   → table-driven unit tests + 1 acceptance test per
                         feature; one file per feature
Phase 4 : Red check    → every new test must fail FOR THE RIGHT REASON
Phase 5 : Report       → files created, expected reds, hand-off command
```

### Phase 0 — Context and baseline

1. Detect the test runner and conventions (see `references/stack-detection.md`).
2. Run the existing suite. **A green baseline is mandatory.** Without it, a
   failing test cannot be attributed to the new feature rather than to a
   pre-existing break.
   - Suite already red → report which tests fail and ask whether to continue
     anyway (recording the known-red set) or stop.
   - No tests at all → that is a valid green baseline; note it and continue.
3. Read one or two existing test files and copy their conventions: file naming,
   import style, fixture style, assertion library, parametrization idiom.

### Phase 1 — Intake and clarification

Accept, in priority order: features pasted in the conversation, a file the user
points to, or the `Clarifications` column of an existing `FEATURES.md`.

For each feature, one at a time, ask only the questions needed to write a
boundary table — the observable behavior, the inputs and their limits, the
expected errors. Do not ask about implementation choices (storage, framework,
algorithm): they do not change the tests.

Cap: beyond ~8 features, propose splitting into several runs. Boundary analysis
on 8 features already produces a large harness to review in one gate.

### Phase 2 — Boundary contracts

One file per feature: `docs/test-contracts/<feature-slug>.md`, in the format
given by `references/contract-format.md`. Contents: target units to import,
input partitions and boundaries, expected outputs, expected errors, the
acceptance criterion in Given/When/Then form, and an explicit out-of-scope list.

Method and per-type heuristics live in `references/boundary-analysis.md`.

**This phase ends at a gate.** Show a compact summary of the contracts and wait
for explicit validation. Never generate tests from an unvalidated contract — a
wrong contract produces a whole file of wrong tests.

### Phase 3 — Generation

One test file per feature, placed and named per the conventions found in
Phase 0.

- **Unit tests:** one parametrized table per input under analysis. A boundary
  case is a row in that table, never its own near-identical test function.
- **Acceptance test:** one per feature, expressing the Given/When/Then from the
  contract at the outermost boundary the feature owns.
- **Assertion quality:** load `writing-good-tests.md` from
  `superpowers:test-driven-development` before writing. Hand-derived literal
  `want` values; no mirror assertions; no change detectors.
- Each test names the break it catches, in its name or a one-line comment.

### Phase 4 — Red verification

Run the suite. Triage every new test:

| Result | Diagnosis | Action |
|---|---|---|
| Fails because the target does not exist | **Good red** | Record the exact failure message |
| Fails on a test defect (typo, bad import, missing fixture) | **False red** | Fix the test, re-run |
| **Passes** | Anomaly | Distinguish the two causes, below |

A passing test has exactly two causes, and they are handled differently:

- **The test asserts nothing meaningful** (tautology, mirror assertion, mocked
  away target). It is defective → fix it until it can fail.
- **The behavior already exists** in the codebase. The test is sound; keep it as
  a regression test, and list it in the report under *already implemented* —
  outside the expected-red set. Do not delete it, and do not report the feature
  as covered-to-be-built when it is already done.

A run is complete when every new test is either a recorded good red or an
explicitly listed already-implemented pass. Never soften a test to make its
failure "look right".

Note on compiled/typed stacks: a missing module can fail the whole file at
collection or compile time rather than per test. That is still a good red,
provided the message is the expected one. Record it at file granularity and say
so in the report.

### Phase 5 — Report and hand-off

Plain text, no widget:

- Contracts written, and the test files created.
- Per test (or per file, for collection-time failures) the expected red.
- Features left uncovered, and why.
- The hand-off command: `superpowers:test-driven-development` to implement
  feature by feature, or `feature-status-tracker` for the full branch/PR
  pipeline.

Commit the tests and contracts together, so the contract and the harness that
encodes it never drift apart.

## File structure

```
spec-to-tests/
├── .claude-plugin/plugin.json
├── skills/spec-to-tests/
│   ├── SKILL.md                        6-phase workflow
│   └── references/
│       ├── boundary-analysis.md         BVA method + per-type heuristics
│       ├── stack-detection.md           runner → conventions matrix
│       ├── contract-format.md           docs/test-contracts/<slug>.md format
│       └── superpowers-integration.md   delegations + no-Superpowers fallback
├── README.md
└── LICENSE
```

`SKILL.md` holds the workflow and the gates only. Per-type boundary heuristics,
the runner matrix and the contract template are references, loaded when the
phase needs them.

## Superpowers integration

| Step | Superpowers skill | Role |
|---|---|---|
| Phase 3, before writing | `test-driven-development` → `writing-good-tests.md` | Assertion quality rules |
| Phase 5 hand-off | `test-driven-development` | Implements against the harness |
| Phase 4, on a stubborn false red | `systematic-debugging` | Diagnose a test that fails for an unexplained reason |

`brainstorming` must not be invoked: Phase 1 already does the framing, from a
narrower angle.

Fallback when Superpowers is absent: mention it once, then apply the assertion
rules inline (literal expected values, no assertion computed by the code under
test, no assertion on a constant's value). Never block the workflow.

## Validating the skill itself

A document that instructs an agent is tested by the consuming agent's behavior.
Validation is an eval, not a unit test: run the skill against a fixture project
holding a known feature list, then assert on the run's artifacts.

Pass criteria:

1. No production file created or modified — only test files and contracts.
2. Every generated test either fails with a recorded reason matching the actual
   runner output, or is listed as already-implemented.
3. The boundary table for a bounded numeric input covers min, min−1, max,
   max+1 and the degenerate cases (null, empty, wrong type).
4. Boundary cases appear as parametrized rows, not as duplicated test functions.
5. The run stops at the Phase 2 gate and does not write a test before validation.

Criterion 1 is the one that matters most: it is the skill's central constraint,
and the easiest for a model to rationalize away when a test will not import.
