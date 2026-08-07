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
3. **Nothing else.** No helpers you did not need, no fixtures for a database the
   feature does not touch, no setup for a later feature.

## Shape

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
error class — the test would stop being able to catch the confusion it exists to
catch.

Port the same shape to whatever runner Phase 0 detected: `test.each` tables in
Vitest and Jest, a slice of case structs in Go, `@ParameterizedTest` with
`@CsvSource` in JUnit.

## Naming

Every test name states the break it catches. `test_accepts_amounts_up_to_the_limit`
catches an off-by-one at 10 000; `test_rejects_non_positive_amounts` catches a
missing lower-bound guard. A name like `test_check_transfer_limit` names nothing
— it repeats the function under test and would still be accurate if the test
asserted the opposite.

## The acceptance test

One per feature, expressed at the boundary a user actually touches — the HTTP
route, the CLI command, the exported function — not at the internal helper the
unit tests already cover. It is the test that fails when every unit passes and
the feature still does not work.

Write it from the contract's Given/When/Then verbatim. If you cannot, the
acceptance criterion is too vague and Phase 1 is not finished.
