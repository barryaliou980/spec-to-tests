# Spec to Tests

Turns a list of features into a verified-red test harness: boundary contracts,
table-driven tests, and a red check that proves each test fails for the right
reason. **Writes tests only — never production code.**

## What it does

| Phase | |
|---|---|
| 0 Context | Detects your test runner and copies your existing conventions. Requires a green baseline. |
| 1 Intake | Collects the features, clarifies one at a time — behavior, input limits, expected errors. |
| 2 Contracts | Boundary analysis per feature → `docs/test-contracts/<slug>.md`. **Stops for your validation.** |
| 3 Generation | One test file per feature: parametrized boundary tables + one acceptance test. |
| 4 Red check | Runs the suite and triages every test. A feature not yet built fails; one already built passes — both are fine, an untriaged test is not. |
| 5 Report | Files created, the exact expected failure per test, and the command to hand off. |

## What it does not do

- **No production code.** Not a stub, not an empty function, not an `__init__.py`
  to make an import resolve. If the test cannot import its target, that is the
  expected result. This is the reason to reach for this skill instead of
  `superpowers:test-driven-development`, which implements as it goes.
- **No chaining into implementation.** It ends at the report and hands off.
- **No `FEATURES.md` management.** It reads that file; `feature-status-tracker`
  owns it.
- **No integration tier** in 1.0.0 — unit and acceptance tests only. An
  integration tier would require negotiating containers and database seeding.

## Install

```bash
/plugin marketplace add barryaliou980/aliou-skills
/plugin install spec-to-tests@aliou-skills
```

## Example

**Input** — a line in your backlog:

> Transfer limit — a transfer above 10 000 € must be rejected. Amounts are in
> euros, whole numbers only.

**Phase 2** writes `docs/test-contracts/transfer-limit.md`, and waits for you:

| Partition | Values to test | Expected |
|---|---|---|
| valid | 1, 9999, 10000 | returns, no error |
| invalid — above | 10001, 2**31 | `TransferLimitError` |
| invalid — below | 0, -1 | `ValueError` |
| degenerate | None, "", "abc", 10000.5 | `TypeError` |

**Phase 3** writes one table per distinguishable outcome — not one table with a
`"rejected"` string, which would still pass if the code raised the wrong error:

```python
@pytest.mark.parametrize(
    "amount", [10001, 2**31], ids=["one-over-limit", "huge"]
)
def test_rejects_amounts_above_the_limit(amount):
    with pytest.raises(TransferLimitError):
        check_transfer_limit(amount)
```

**Phase 4** runs the suite with `--continue-on-collection-errors`, so the missing
module does not abort your existing tests, and **Phase 5** reports:

```
Contracts:                docs/test-contracts/transfer-limit.md
Test files:               tests/test_transfer_limit.py
Expected reds:            tests/test_transfer_limit.py → ModuleNotFoundError: No module named 'transfers.limits'
                          (collection error: the file's 3 tests do not run until the module exists)
Already implemented:      none
Not covered:              none
Production files touched: none
Hand-off:                 superpowers:test-driven-development
```

Run it plainly and pytest reports `1 error` and stops — your green tests never
execute. That is why the flag is part of the phase, not an optional extra.

## Requirements

Superpowers is recommended, not required. With it, assertion quality is governed
by `writing-good-tests.md` and unexplained failures route to
`systematic-debugging`. Without it, the skill applies the equivalent rules
inline and says so once — it never blocks.

## Status

1.0.0. The Phase 4 runner behavior above is verified against pytest 8 — the
collection-error granularity and the `--continue-on-collection-errors`
requirement were measured, not assumed. The other runners in
`references/stack-detection.md` are documented from their published behavior.

The rationalization table in `SKILL.md` is written against *predicted* failure
modes; the skill has not yet been validated with behavioral evals against a
fixture project. Expect to refine that table as real runs surface real
rationalizations.

## License

MIT © 2026 Aliou Barry
