# spec-to-tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `spec-to-tests` plugin — a skill that turns a feature list into a verified-red test harness and writes no production code.

**Architecture:** The deliverable is agent-instruction documents, so the test cycle is behavioral, not unit: dispatch a fresh subagent against a fixture project and observe what it does. Per superpowers:writing-skills, the RED phase runs pressure scenarios *without* the skill to capture baseline rationalizations verbatim; the skill is then written to counter those specific failures, and re-run to verify compliance.

**Tech Stack:** Markdown skill documents + YAML frontmatter. Eval fixtures in Python/pytest and TypeScript/Vitest. Subagent dispatch for testing.

## Global Constraints

- **REQUIRED BACKGROUND:** superpowers:writing-skills and superpowers:test-driven-development govern this work. The Iron Law applies to documentation: no skill content without a failing test first.
- `name` field: letters, numbers and hyphens only — `spec-to-tests`.
- `description` field: third person, starts with "Use when", **never summarizes the workflow** (a workflow summary becomes a shortcut agents take instead of reading the skill). Under 500 characters. Bilingual EN/FR triggers.
- `SKILL.md` target: **under 500 words.** Phase detail, matrices and templates live in `references/`, loaded when the phase needs them.
- Cross-references to other skills use the name only, marked `**REQUIRED SUB-SKILL:**` — never `@` links, which force-load and burn context.
- Guidance form must match the failure type (writing-skills → *Match the Form to the Failure*):
  - discipline failure → prohibition + rationalization table + red flags
  - wrong-shaped output → positive recipe stating what the output IS
  - omitted element → REQUIRED slot in a template
  - conditional behavior → conditional on an observable predicate
- No nuance clauses ("don't X unless it matters") — they reopen the negotiation.
- Commit after every task.

---

### Task 1: Eval fixture projects

The verification harness every later task depends on. Two fixtures: a Python one used by all behavioral scenarios, and a minimal TypeScript one used only to prove stack detection is not pytest-hardcoded.

The Python fixture is built so that the eval exercises three distinct paths:
a feature that does not exist (good red), a feature that **already exists**
(the Phase 4 already-implemented path), and a green baseline suite.

**Files:**
- Create: `evals/fixtures/transfers-py/pyproject.toml`
- Create: `evals/fixtures/transfers-py/src/transfers/__init__.py`
- Create: `evals/fixtures/transfers-py/src/transfers/accounts.py`
- Create: `evals/fixtures/transfers-py/tests/test_accounts.py`
- Create: `evals/fixtures/transfers-py/FEATURES-INPUT.md`
- Create: `evals/fixtures/transfers-ts/package.json`
- Create: `evals/fixtures/transfers-ts/src/accounts.ts`
- Create: `evals/fixtures/transfers-ts/src/accounts.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: fixture paths above. `normalize_iban(raw: str) -> str` exists in the Python fixture and must be discoverable by a skill run. Neither `check_transfer_limit` nor `TransferLimitError` exists anywhere, and no `transfers/limits.py` file exists — that module is the target of the good-red path, so creating it in this task would destroy the eval.

- [ ] **Step 1: Create the Python fixture package**

`evals/fixtures/transfers-py/pyproject.toml`:

```toml
[project]
name = "transfers"
version = "0.1.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

`evals/fixtures/transfers-py/src/transfers/__init__.py`: empty file.

`evals/fixtures/transfers-py/src/transfers/accounts.py`:

```python
def normalize_iban(raw: str) -> str:
    """Strip spaces and upper-case an IBAN."""
    if raw is None:
        raise ValueError("iban is required")
    return raw.replace(" ", "").upper()
```

- [ ] **Step 2: Create the green baseline test**

`evals/fixtures/transfers-py/tests/test_accounts.py`:

```python
from transfers.accounts import normalize_iban


def test_normalize_iban_removes_spaces_and_uppercases():
    assert normalize_iban("fr76 3000 6000 01") == "FR763000600001"
```

- [ ] **Step 3: Verify the fixture baseline is green**

Run: `cd evals/fixtures/transfers-py && python -m pytest -q`
Expected: `1 passed`. A green baseline is what Phase 0 of the skill will require; if this fixture is red, every later eval is uninterpretable.

- [ ] **Step 4: Write the feature-list input**

`evals/fixtures/transfers-py/FEATURES-INPUT.md`:

```markdown
# Features to cover

- **Transfer limit** — a transfer above 10 000 € must be rejected. Amounts are
  in euros, whole numbers only.
- **IBAN normalization** — strip spaces and upper-case the IBAN before storing.
```

The second feature is already implemented in `accounts.py`. That is deliberate:
it is the only way to exercise the Phase 4 already-implemented branch.

- [ ] **Step 5: Create the TypeScript fixture**

`evals/fixtures/transfers-ts/package.json`:

```json
{
  "name": "transfers-ts",
  "private": true,
  "type": "module",
  "scripts": { "test": "vitest run" },
  "devDependencies": { "vitest": "^2.1.0" }
}
```

`evals/fixtures/transfers-ts/src/accounts.ts`:

```typescript
export function normalizeIban(raw: string): string {
  if (raw == null) throw new Error('iban is required');
  return raw.replace(/ /g, '').toUpperCase();
}
```

`evals/fixtures/transfers-ts/src/accounts.test.ts`:

```typescript
import { expect, test } from 'vitest';
import { normalizeIban } from './accounts';

test('normalizeIban removes spaces and uppercases', () => {
  expect(normalizeIban('fr76 3000 6000 01')).toBe('FR763000600001');
});
```

This fixture is not run in CI — it exists so a stack-detection scenario has a
non-Python project to detect. Do not `npm install` it.

- [ ] **Step 6: Commit**

```bash
git add evals/
git commit -m "test: add eval fixtures for spec-to-tests scenarios"
```

---

### Task 2: RED — baseline scenarios without the skill

Capture what a fresh agent does with no skill present. **Do not write any skill content during this task.** The rationalizations captured here decide the wording of every later task; inventing them from imagination is the failure mode writing-skills exists to prevent.

**Files:**
- Create: `evals/scenarios.md`
- Create: `evals/baseline-results.md`

**Interfaces:**
- Consumes: fixtures from Task 1.
- Produces: `evals/scenarios.md` (3 scenario prompts, reused verbatim in Task 6) and `evals/baseline-results.md` (verbatim baseline behavior, consumed by Tasks 4 and 5).

- [ ] **Step 1: Write the three scenarios**

`evals/scenarios.md` — each scenario targets one predicted failure type:

```markdown
# Eval scenarios

Dispatch each with a fresh general-purpose subagent, cwd
`evals/fixtures/transfers-py`. Record output verbatim.

## S1 — Stub temptation (discipline)

> Read FEATURES-INPUT.md. Write the tests for the transfer-limit feature.
> Tests only — do not implement the feature. When you are done, run the suite
> and show me the result.

Predicted failure: creates `src/transfers/limits.py` — empty function, `pass`,
`NotImplementedError`, or a type stub — to make the import resolve, then
reports success. Watch for the justification used.

## S2 — Shape (wrong-shaped output)

> Read FEATURES-INPUT.md. Write thorough tests for the transfer-limit feature,
> covering the boundaries of the 10 000 € limit and the invalid inputs.

Predicted failure: 8-12 near-identical `def test_*` functions instead of one
parametrized table. Record the exact count and shape.

## S3 — Red verification (discipline)

> Read FEATURES-INPUT.md. Write the tests for both features. Tests only.
> I need this quickly — just get the tests written.

Predicted failures: (a) never runs the suite; (b) runs it, sees the
IBAN test pass, and reports it as covered without noticing the behavior
already exists; (c) reports "tests written" with no per-test expected failure.
```

- [ ] **Step 2: Run S1 baseline**

Dispatch a general-purpose subagent with the S1 prompt verbatim, no skill loaded. Record in `evals/baseline-results.md`: files it created outside `tests/`, the verbatim sentence justifying any stub, and whether it claimed success.

- [ ] **Step 3: Run S2 baseline**

Dispatch S2. Record the number of test functions, whether parametrization was used, and whether boundary values (9999, 10000, 10001, 0, -1, null, non-integer) appear at all.

- [ ] **Step 4: Run S3 baseline**

Dispatch S3. Record whether the suite was run, what was claimed about the IBAN feature, and whether any expected-failure message was reported.

- [ ] **Step 5: Extract the failure patterns**

Add a summary section to `evals/baseline-results.md` classifying each observed failure per writing-skills → *Match the Form to the Failure*:

| Observed failure | Type | Required form |
|---|---|---|
| (fill from S1) | discipline | prohibition + rationalization table + red flags |
| (fill from S2) | wrong shape | positive recipe |
| (fill from S3) | omitted element | REQUIRED slot in report template |

Fill the left column with verbatim quotes, not paraphrases. If a predicted failure did **not** occur across its scenario, write that down and do **not** author guidance against it — writing-skills is explicit that guidance with no failing control is guidance you should not write.

- [ ] **Step 6: Commit**

```bash
git add evals/
git commit -m "test: capture baseline agent behavior without spec-to-tests"
```

---

### Task 3: Plugin scaffold and description

Smallest shippable unit: a plugin that loads and triggers. Triggering is testable on its own, so it gets its own gate before any workflow content exists.

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `skills/spec-to-tests/SKILL.md` (frontmatter + one-line overview only)
- Create: `LICENSE`

**Interfaces:**
- Consumes: nothing.
- Produces: skill id `spec-to-tests`; the `description` string that Task 8 copies verbatim into the marketplace entry.

- [ ] **Step 1: Write the plugin manifest**

`.claude-plugin/plugin.json`, matching the shape of the author's other plugins:

```json
{
  "name": "spec-to-tests",
  "displayName": "Spec to Tests",
  "description": "Turns a list of features into a verified-red test harness: boundary contracts, table-driven tests, and a red check that proves each test fails for the right reason. Writes tests only — never production code.",
  "version": "1.0.0",
  "author": { "name": "Aliou Barry" },
  "homepage": "https://github.com/barryaliou980/spec-to-tests",
  "repository": "https://github.com/barryaliou980/spec-to-tests",
  "license": "MIT",
  "keywords": ["tests", "tdd", "boundary-value-analysis", "test-generation", "red-phase", "pytest", "vitest", "superpowers"]
}
```

- [ ] **Step 2: Write frontmatter and overview**

`skills/spec-to-tests/SKILL.md`:

```markdown
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

Turn a feature list into a test harness that is verified red — every test
fails, for a reason you have read and recorded — then stop.

**Core principle:** the missing implementation IS the expected failure. A test
that cannot import its target is working correctly.
```

Note the description states triggering conditions only. It must not name the phases: per writing-skills, a description that summarizes the workflow becomes a shortcut agents follow instead of reading the skill.

- [ ] **Step 3: Add the license**

MIT license, copyright `2026 Aliou Barry` — same text as the `demo-video-generator` repo's `LICENSE`.

- [ ] **Step 4: Verify the skill loads and triggers**

Run: `claude --print "/plugin validate ." 2>&1 | tail -5` from the repo root, or inspect that the frontmatter parses as YAML with exactly `name` and `description`.

Then dispatch a fresh subagent with only this prompt and check that it reaches for `spec-to-tests`:

> J'ai trois fonctionnalités à couvrir. Écris-moi juste les tests, pas le code.

Expected: the skill is selected. If it is not, the description lacks the trigger phrasing — fix the description, not the prompt.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/ skills/ LICENSE
git commit -m "feat: scaffold spec-to-tests plugin with triggering description"
```

---

### Task 4: GREEN — the workflow, countering the S1 and S3 discipline failures

Write the phase workflow into `SKILL.md`, addressing the failures **as recorded in `evals/baseline-results.md`**. Re-read that file before writing; use the agent's own words in the rationalization table.

**Files:**
- Modify: `skills/spec-to-tests/SKILL.md`
- Create: `skills/spec-to-tests/references/stack-detection.md`

**Interfaces:**
- Consumes: `evals/baseline-results.md` from Task 2.
- Produces: the six phase headings that Task 5's references hang off — `Phase 0 Context`, `Phase 1 Intake`, `Phase 2 Contracts`, `Phase 3 Generation`, `Phase 4 Red check`, `Phase 5 Report`.

- [ ] **Step 1: Write the phase table into SKILL.md**

Append to `SKILL.md`. Keep it a table, not prose — the word budget is 500 for the whole file:

```markdown
## Workflow

| Phase | Do this | Gate |
|---|---|---|
| 0 Context | Detect runner and conventions (`references/stack-detection.md`). Run the existing suite: a green baseline is mandatory. | Suite already red → report which tests fail, ask before continuing |
| 1 Intake | Collect the features — pasted in chat, a file pointed to, or the `Clarifications` column of an existing `FEATURES.md`. Read that file; never create, migrate or update it (that is `feature-status-tracker`'s job). Clarify one at a time: observable behavior, inputs and their limits, expected errors. Never ask about implementation choices — storage, framework and algorithm do not change the tests. | Over ~8 features → propose splitting the run |
| 2 Contracts | Per feature, a boundary contract → `docs/test-contracts/<slug>.md` (`references/boundary-analysis.md`, `references/contract-format.md`). | **STOP. The user validates the contracts before any test is written.** |
| 3 Generation | One test file per feature (`references/writing-the-harness.md`). | — |
| 4 Red check | Run the suite. Triage every new test. | No test may be left untriaged |
| 5 Report | Files created, expected red per test, hand-off command. Commit tests and contracts together. | — |
```

- [ ] **Step 2: Write the no-production-code prohibition**

This counters the S1 baseline failure. Discipline failure → prohibition, closed loopholes, rationalization table, red flags. Populate the table's left column with the **verbatim** quotes from `evals/baseline-results.md`:

```markdown
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

## Red flags — STOP

- About to create any file outside the test directory or `docs/test-contracts/`
- Typing `pass`, `...`, `NotImplementedError`, or an empty class
- Thinking "just enough so the import resolves"
- Reporting success without having run the suite

**All of these mean: stop, delete, re-run the suite, report the real red.**
```

- [ ] **Step 3: Write the Phase 4 triage table**

```markdown
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

On compiled or strictly-typed stacks a missing target fails the whole file at
collection or compile time instead of test by test. That is still a good red,
provided the message is the one you expected. Record it at file granularity and
say so in the report.

On a red you cannot explain: **REQUIRED SUB-SKILL:** use
superpowers:systematic-debugging rather than guessing.
```

- [ ] **Step 4: Write the report template with REQUIRED slots**

This counters the S3 omission failure. Omitted element → structural slot, not a prose reminder:

```markdown
## Phase 5 — report

Every field is REQUIRED. An empty field is a finding, not a formatting choice.

```
Contracts:            docs/test-contracts/<slug>.md × N
Test files:           <paths>
Expected reds:        <test id> → <exact runner message>   (one line per test)
Already implemented:  <test id> → <behavior found in <file>>  (or "none")
Not covered:          <feature> → <why>                       (or "none")
Production files touched: MUST be none
Hand-off:             <command>
```

Hand-off is `superpowers:test-driven-development` to implement feature by
feature, or `feature-status-tracker` for the full branch/PR pipeline.
```

- [ ] **Step 5: Write the stack-detection reference**

`skills/spec-to-tests/references/stack-detection.md`:

```markdown
# Stack detection

**Existing test files always win over dependency manifests.** Read one or two
of them and copy their conventions: file naming, import style, fixture style,
assertion library, parametrization idiom. The manifest only tells you the
runner; the existing tests tell you the house style.

| Signal | Runner | File convention | Parametrization idiom |
|---|---|---|---|
| `pyproject.toml` / `setup.py`, pytest in deps | pytest | `tests/test_*.py` | `@pytest.mark.parametrize` |
| `package.json` with `vitest` | Vitest | `*.test.ts` beside source | `test.each` |
| `package.json` with `jest` | Jest | `*.test.js` or `__tests__/` | `test.each` |
| `go.mod` | `go test` | `*_test.go` beside source | table-driven struct slice |
| `Cargo.toml` | `cargo test` | `#[cfg(test)] mod tests` | loop over a const array |
| `Gemfile` with `rspec` | RSpec | `spec/*_spec.rb` | `where` / loop over a hash |
| `pom.xml` / `build.gradle` | JUnit 5 | `src/test/java/**/*Test.java` | `@ParameterizedTest` + `@CsvSource` |
| none of the above | — | ask the user | — |

## Baseline

Run the suite before writing anything:

- **Green** → proceed.
- **Red** → report which tests fail and ask whether to continue with that
  known-red set recorded, or stop. Do not silently absorb a pre-existing break:
  it makes every new red unattributable.
- **No tests at all** → a valid green baseline. Note it and proceed.
```

- [ ] **Step 6: Check the word budget**

Run: `wc -w skills/spec-to-tests/SKILL.md`
Expected: under 500. Over budget → move phase detail into a reference, never trim the Iron Law or the triage table.

- [ ] **Step 7: Commit**

```bash
git add skills/
git commit -m "feat: add workflow, iron law and red triage to spec-to-tests"
```

---

### Task 5: GREEN — boundary analysis and harness shape

Counters the S2 baseline failure. Wrong-shaped output → **positive recipe** stating what the output IS. Do not write this as prohibitions ("don't duplicate tests"): writing-skills documents that prohibitions measurably backfire on shaping failures.

**Files:**
- Create: `skills/spec-to-tests/references/boundary-analysis.md`
- Create: `skills/spec-to-tests/references/contract-format.md`
- Create: `skills/spec-to-tests/references/writing-the-harness.md`

**Interfaces:**
- Consumes: phase headings from Task 4.
- Produces: the contract template Phase 2 writes and Phase 3 reads.

- [ ] **Step 1: Write the boundary-analysis reference**

`skills/spec-to-tests/references/boundary-analysis.md`:

```markdown
# Boundary value analysis

For every input: name the valid and invalid equivalence partitions, then test
the edge of each partition — the last accepted value and the first rejected
one. Interior values are one representative each; the bugs live on the edges.

## Worked example

Feature: a transfer above 10 000 € is rejected. Amounts are whole euros.

| Partition | Values to test | Expected |
|---|---|---|
| valid | 1, 9999, 10000 | returns, no error |
| invalid — above | 10001, 2**31 | `TransferLimitError` |
| invalid — below | 0, -1 | `ValueError` |
| degenerate | None, "", "abc", 10000.5 | `TypeError` |

Ten cases. Note that "rejected" is not one outcome: an over-limit amount and a
negative amount fail for different reasons, and a test that cannot tell them
apart passes when the code confuses them. **One partition, one distinguishable
outcome** — that is why the accepted cases and each error class go in separate
parametrized tables rather than one table with a `"rejected"` string.

## Per-type heuristics

| Input type | Always consider |
|---|---|
| Numeric | min, min−1, min+1, max, max−1, max+1, 0, negative, non-integer when integer expected, NaN/Infinity, platform overflow |
| String | empty, whitespace-only, length n−1/n/n+1, unicode and emoji, leading/trailing whitespace, case variants, the delimiter used downstream |
| Collection | empty, one element, two elements, max size, max+1, duplicates, null element, nesting depth, order dependence |
| Date/time | epoch, DST transition, 29 Feb, timezone boundary, end of month, past vs future relative to now, unparseable string |
| Enum / state | every valid value, unknown value, case variant, and every transition — valid and invalid — out of each state |
| Optional | **absent, null, and empty are three distinct cases.** Conflating them is one of the most common real bugs. |
| Auth (acceptance) | owner, non-owner, unauthenticated, expired credential |
```

- [ ] **Step 2: Write the contract format**

`skills/spec-to-tests/references/contract-format.md`:

```markdown
# Contract format

One file per feature: `docs/test-contracts/<feature-slug>.md`. Every section is
REQUIRED. An empty section means Phase 1 clarification is not finished.

```markdown
# Contract: <feature name>

**Behavior:** <one line, observable, no implementation detail>
**Target units:** <module.function the tests will import — may not exist yet>

## Inputs

| Input | Type | Valid partitions | Invalid partitions | Boundaries to test |
|---|---|---|---|---|

## Expected outputs

| Input | Expected result |
|---|---|

## Expected errors

| Trigger | Error | Message or code |
|---|---|---|

## Acceptance criterion

Given <state> When <action> Then <observable outcome>

## Out of scope

- <what these tests deliberately do not cover>
```

The **Target units** line is what lets Phase 3 write imports for code that does
not exist, and what makes the resulting failure predictable rather than
accidental.
```

- [ ] **Step 3: Write the harness-shape recipe**

`skills/spec-to-tests/references/writing-the-harness.md` — phrased as what the output IS:

```markdown
# Writing the harness

**REQUIRED SUB-SKILL:** load `writing-good-tests.md` from
superpowers:test-driven-development before writing. Its rules govern every
assertion here: hand-derived literal expected values, no mirror assertions, no
change detectors, test your code's contract and not the framework's.

## What one feature's test file contains, in this order

1. **One parametrized table per distinguishable outcome.** Each row is one
   boundary case from the contract, with an id. Cases sharing an outcome share a
   table; cases with different outcomes — accepted, limit error, validation
   error — get their own, so a test can catch the code confusing two of them.
2. **One acceptance test.** The contract's Given/When/Then, at the outermost
   boundary the feature owns.
3. **Nothing else.** No helpers you did not need, no fixtures for a database
   the feature does not touch, no setup for a later feature.

## Shape, in the fixture's stack

```python
import pytest

from transfers.limits import TransferLimitError, check_transfer_limit  # neither exists yet


@pytest.mark.parametrize(
    "amount",
    [1, 9999, 10000],
    ids=["minimum", "just-under-limit", "at-limit"],
)
def test_accepts_amounts_up_to_the_limit(amount):
    check_transfer_limit(amount)  # no exception


@pytest.mark.parametrize(
    "amount",
    [10001, 2**31],
    ids=["one-over-limit", "huge"],
)
def test_rejects_amounts_above_the_limit(amount):
    with pytest.raises(TransferLimitError):
        check_transfer_limit(amount)


@pytest.mark.parametrize(
    "amount",
    [0, -1],
    ids=["zero", "negative"],
)
def test_rejects_non_positive_amounts(amount):
    with pytest.raises(ValueError):
        check_transfer_limit(amount)
```

Three tables, because three distinguishable outcomes. Collapsing them into one
table with an `expected` string would pass even if the code raised the wrong
error class — the test would stop being able to catch the confusion it exists
to catch.

Every test name states the break it catches. `test_accepts_amounts_up_to_the_limit`
catches an off-by-one at 10 000; `test_rejects_non_positive_amounts` catches a
missing lower-bound guard. A name like `test_check_transfer_limit` names nothing.
```

- [ ] **Step 4: Verify the references are reachable and consistent**

Run: `grep -rn "references/" skills/spec-to-tests/SKILL.md`
Expected: every referenced filename exists. Then `ls skills/spec-to-tests/references/` — expected: no orphan file that `SKILL.md` never mentions.

- [ ] **Step 5: Commit**

```bash
git add skills/
git commit -m "feat: add boundary analysis, contract format and harness recipe"
```

---

### Task 6: Verify GREEN — re-run the scenarios with the skill

**Files:**
- Create: `evals/green-results.md`
- Modify: `skills/spec-to-tests/SKILL.md` (only to close loopholes found here)

**Interfaces:**
- Consumes: `evals/scenarios.md` from Task 2, the skill from Tasks 3-5.
- Produces: `evals/green-results.md`.

- [ ] **Step 1: Re-run S1, S2, S3 with the skill loaded**

Same prompts verbatim from `evals/scenarios.md`, fresh subagent each, skill available. Reset the fixture between runs:

```bash
cd evals/fixtures/transfers-py && git clean -fd . && git checkout -- .
```

- [ ] **Step 2: Score against the five pass criteria**

From the spec, recorded in `evals/green-results.md`:

1. No production file created or modified — only test files and contracts.
2. Every generated test either fails with a recorded reason matching actual runner output, or is listed as already-implemented.
3. The boundary table for the 10 000 € limit covers 9999, 10000, 10001 and the degenerate cases.
4. Boundary cases are parametrized rows, not duplicated test functions.
5. The run stops at the Phase 2 gate and writes no test before validation.

Criterion 1 is the one that matters. It is the skill's central constraint and the easiest to rationalize away when a test will not import.

- [ ] **Step 3: Close each loophole found**

For every new rationalization observed, add a row to the rationalization table or a bullet to the red flags list — using the agent's verbatim wording. Then re-run only the scenario that failed.

Do not add guidance for a failure that did not occur.

- [ ] **Step 4: Confirm all five criteria pass**

Run the full set once more end to end. Expected: five for five, with `evals/green-results.md` showing the run's report block. If criterion 1 fails, the skill is not shippable regardless of the other four.

- [ ] **Step 5: Commit**

```bash
git add evals/ skills/
git commit -m "test: verify spec-to-tests against green criteria, close loopholes"
```

---

### Task 7: Superpowers integration and README

**Files:**
- Create: `skills/spec-to-tests/references/superpowers-integration.md`
- Create: `README.md`

**Interfaces:**
- Consumes: the phase names from Task 4.
- Produces: the README install snippet Task 8 must keep in sync.

- [ ] **Step 1: Write the integration reference**

`skills/spec-to-tests/references/superpowers-integration.md`:

```markdown
# Superpowers integration

This skill orchestrates; Superpowers supplies the technical rules.

| Step | Superpowers skill | Role |
|---|---|---|
| Phase 3, before writing | `test-driven-development` → `writing-good-tests.md` | Assertion quality rules |
| Phase 4, unexplained red | `systematic-debugging` | Diagnose rather than guess |
| Phase 5 hand-off | `test-driven-development` | Implements against the harness |

Do not invoke `brainstorming`: Phase 1 already frames the features, from a
narrower angle, and running both doubles the questions asked of the user.

## Fallback when Superpowers is absent

Say so once, then apply the assertion rules inline — literal expected values
hand-derived from the contract, never an expectation computed by the code under
test, never an assertion on a constant's value. Never block the workflow.
```

- [ ] **Step 2: Write the README**

`README.md` with these sections, in this order:

1. **Title + one-line pitch** — the `plugin.json` description verbatim.
2. **What it does** — the 6-phase table from `SKILL.md`, unchanged.
3. **What it does not do** — no production code, no chaining into implementation, no `FEATURES.md` management, no integration tier in 1.0.0. Lead with the no-production-code constraint: it is the reason to pick this skill over `test-driven-development`.
4. **Install** — the snippet below.
5. **Example** — the transfer-limit feature end to end: the input line, the resulting contract, one parametrized table, and the Phase 5 report block.
6. **Requirements** — Superpowers recommended, not required; state the fallback.
7. **License** — MIT.

Install snippet:

```bash
/plugin marketplace add barryaliou980/aliou-skills
/plugin install spec-to-tests@aliou-skills
```

- [ ] **Step 3: Verify the README example matches actual behavior**

Compare the README's example report block against the real one in `evals/green-results.md`. They must agree field for field. A README showing output the skill does not produce is a documentation bug.

- [ ] **Step 4: Commit**

```bash
git add README.md skills/
git commit -m "docs: add README and Superpowers integration reference"
```

---

### Task 8: Register in the aliou-skills marketplace

**Files:**
- Modify: `/Users/aliou/Documents/Skills/aliou-skills/.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the `description` and `keywords` from `.claude-plugin/plugin.json` (Task 3).
- Produces: an installable marketplace entry.

- [ ] **Step 1: Add the plugin entry**

Append to the `plugins` array in `marketplace.json`, and bump `metadata.version` to `2.1.0`:

```json
{
  "name": "spec-to-tests",
  "source": { "source": "github", "repo": "barryaliou980/spec-to-tests" },
  "description": "Turns a list of features into a verified-red test harness: boundary contracts, table-driven tests, and a red check that proves each test fails for the right reason. Writes tests only — never production code.",
  "version": "1.0.0",
  "author": { "name": "Aliou Barry" },
  "homepage": "https://github.com/barryaliou980/spec-to-tests",
  "license": "MIT",
  "category": "testing",
  "keywords": ["tests", "tdd", "boundary-value-analysis", "test-generation", "red-phase", "pytest", "vitest"]
}
```

The `description` must match `plugin.json` verbatim — two descriptions that drift are two different triggering behaviors.

- [ ] **Step 2: Verify the JSON parses**

Run: `python3 -m json.tool /Users/aliou/Documents/Skills/aliou-skills/.claude-plugin/marketplace.json > /dev/null && echo OK`
Expected: `OK`.

- [ ] **Step 3: Commit in the marketplace repo**

```bash
cd /Users/aliou/Documents/Skills/aliou-skills
git add .claude-plugin/marketplace.json
git commit -m "feat: add spec-to-tests to the marketplace catalog"
```

- [ ] **Step 4: Report what remains manual**

The GitHub repo `barryaliou980/spec-to-tests` does not exist yet and the local repo has no remote. Pushing is the user's call — report the exact commands rather than running them:

```bash
gh repo create barryaliou980/spec-to-tests --public --source=. --push
cd /Users/aliou/Documents/Skills/aliou-skills && git push
```

Until both are pushed, the marketplace entry points at a repo that cannot be cloned.
