# Contract format

One file per feature: `docs/test-contracts/<feature-slug>.md`. Every section is
REQUIRED. An empty section means Phase 1 clarification is not finished — go back
and ask, do not write the tests.

````markdown
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
````

The **Target units** line is what lets Phase 3 write imports for code that does
not exist, and what makes the resulting failure predictable rather than
accidental. Name the module path and the symbols, exactly as the tests will
import them.

**Out of scope** is not filler. It is where you record what the user said no to,
so the next reader does not mistake a deliberate omission for an oversight.

## Filled example

````markdown
# Contract: transfer limit

**Behavior:** a transfer above 10 000 € is rejected before any money moves.
**Target units:** `transfers.limits.check_transfer_limit`, `transfers.limits.TransferLimitError`

## Inputs

| Input | Type | Valid partitions | Invalid partitions | Boundaries to test |
|---|---|---|---|---|
| `amount` | int (euros) | 1 … 10000 | ≤ 0 ; > 10000 ; non-integer | 1, 9999, 10000, 10001, 0, -1, 10000.5, None |

## Expected outputs

| Input | Expected result |
|---|---|
| 1, 9999, 10000 | returns, no exception |

## Expected errors

| Trigger | Error | Message or code |
|---|---|---|
| amount > 10000 | `TransferLimitError` | "transfer exceeds the 10000 EUR limit" |
| amount ≤ 0 | `ValueError` | "amount must be positive" |
| amount not an int | `TypeError` | "amount must be a whole number of euros" |

## Acceptance criterion

Given an account with sufficient balance
When a transfer of 10 001 € is requested
Then it is rejected and the balance is unchanged

## Out of scope

- Currencies other than EUR — the user confirmed EUR only for now.
- Daily cumulative limits — separate feature.
````
