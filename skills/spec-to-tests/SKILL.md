---
name: spec-to-tests
description: >
  Use when the user wants tests written for one or more features without the
  implementation — "write the tests first", "generate the tests for these
  features", "tests only, no code", "red phase", « écris juste les tests »,
  « génère les tests », « les tests d'abord ». Also use when a feature list,
  backlog, or FEATURES.md needs an executable contract before anyone
  implements it. Works in English or French.
---

# Spec to Tests

Turn a feature list into a test harness that is verified red — every test fails,
for a reason you have read and recorded — then stop.

**Core principle:** the missing implementation IS the expected failure. A test
that cannot import its target is working correctly.

## The Iron Law

```
NO PRODUCTION CODE. NOT ONE LINE.
```

Not a stub. Not an empty function. Not `pass`, not `NotImplementedError`, not a
type-only declaration, not an `__init__.py` to make a package importable. If the
test cannot import its target, **that is the expected result** — record the
error and move on.

Wrote production code? Delete it. Delete means delete — don't keep it as
reference, don't comment it out, don't move it to a scratch file.

**Violating the letter of this rule is violating the spirit of this rule.**

| Rationalization | Reality |
|---|---|
| "The test can't even run without the module" | A collection error is a valid red. Record the message. |
| "It's just an empty stub, not a real implementation" | An empty stub is production code. It changes what the test proves. |
| "I need the signature so the test knows what to call" | The contract holds the signature. That is what Phase 2 is for. |
| "Adding `__init__.py` is packaging, not implementation" | It changes the import result. Out of scope. |
| "The user obviously wants working code eventually" | Eventually is another agent's turn. Your output is the harness. |

### Red flags — STOP

- About to create any file outside the test directory or `docs/test-contracts/`
- Typing `pass`, `...`, `NotImplementedError`, or an empty class
- Thinking "just enough so the import resolves"
- Reporting success without having run the suite

**All of these mean: stop, delete, re-run the suite, report the real red.**

## Workflow

| Phase | Do this | Gate |
|---|---|---|
| 0 Context | Detect runner and conventions (`references/stack-detection.md`). Run the existing suite: a green baseline is mandatory. | Suite already red → report which tests fail, ask before continuing |
| 1 Intake | Collect the features (chat, a file, or an existing `FEATURES.md` — read it, never write it). Clarify one at a time: observable behavior, input limits, expected errors. Never ask about implementation choices; they do not change the tests. | Over ~8 features → propose splitting the run |
| 2 Contracts | Per feature, a boundary contract → `docs/test-contracts/<slug>.md` (`references/boundary-analysis.md`, `references/contract-format.md`). | **STOP. The user validates the contracts before any test is written.** |
| 3 Generation | One test file per feature (`references/writing-the-harness.md`). | — |
| 4 Red check | Run the suite. Triage every new test. | No test may be left untriaged |
| 5 Report | The block below. Commit tests and contracts together. | — |

## Phase 4 — triage every new test

| Result | Diagnosis | Action |
|---|---|---|
| Fails, target does not exist | Good red | Record the exact failure message |
| Fails on a test defect (typo, bad import, missing fixture) | False red | Fix the test, re-run |
| Passes | Anomaly | See below |

A passing test has exactly two causes:

- **It asserts nothing meaningful** (tautology, mirror assertion, target mocked
  away) → defective. Fix it until it can fail.
- **The behavior already exists** in the codebase → the test is sound. Keep it as
  a regression test and list it under *already implemented*, outside the
  expected-red set. Do not delete it. Do not report the feature as still to build.

Never soften a test to make its failure look right.

On compiled or typed stacks a missing target fails the whole file at collection
time rather than test by test. Still a good red, if the message is the one you
expected — record it at file granularity and say so.

On a red you cannot explain: **REQUIRED SUB-SKILL:** use
superpowers:systematic-debugging rather than guessing.

## Phase 5 — report

Every field is REQUIRED. An empty field is a finding, not a formatting choice.

```
Contracts:                docs/test-contracts/<slug>.md × N
Test files:               <paths>
Expected reds:            <test id> → <exact runner message>      (one per test)
Already implemented:      <test id> → <behavior found in <file>>  (or "none")
Not covered:              <feature> → <why>                       (or "none")
Production files touched: MUST be none
Hand-off:                 <command>
```

Hand-off is `superpowers:test-driven-development` to implement feature by
feature, or `feature-status-tracker` for the full branch/PR pipeline.

## References

`stack-detection.md` · `boundary-analysis.md` · `contract-format.md` ·
`writing-the-harness.md` · `superpowers-integration.md` — each loaded by the
phase that cites it above.
