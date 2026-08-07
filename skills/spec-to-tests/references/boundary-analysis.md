# Boundary value analysis

For every input: name the valid and invalid equivalence partitions, then test
the edge of each partition — the last accepted value and the first rejected one.
Interior values are one representative each; the bugs live on the edges.

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

## Where to stop

A boundary table is not a cartesian product. Two inputs with five partitions
each is ten cases, not twenty-five — vary one input at a time, holding the
others at a valid representative value. Combine two inputs only when the feature
states a rule about their interaction, and then test only that rule's edges.

If a feature produces more than ~20 cases, it is doing more than one thing.
Split the feature, not the table.
