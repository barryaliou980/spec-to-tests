# Stack detection

**Existing test files always win over dependency manifests.** Read one or two of
them and copy their conventions: file naming, import style, fixture style,
assertion library, parametrization idiom. The manifest only tells you the
runner; the existing tests tell you the house style.

| Signal | Runner | File convention | Parametrization idiom |
|---|---|---|---|
| `pyproject.toml` / `setup.py`, pytest in deps | pytest | `tests/test_*.py` | `@pytest.mark.parametrize` |
| `package.json` with `vitest` | Vitest | `*.test.ts` beside source | `test.each` |
| `package.json` with `jest` | Jest | `*.test.js` or `__tests__/` | `test.each` |
| `go.mod` | `go test` | `*_test.go` beside source | table-driven struct slice |
| `Cargo.toml` | `cargo test` | `#[cfg(test)] mod tests` | loop over a const array |
| `Gemfile` with `rspec` | RSpec | `spec/*_spec.rb` | loop over a hash of cases |
| `pom.xml` / `build.gradle` | JUnit 5 | `src/test/java/**/*Test.java` | `@ParameterizedTest` + `@CsvSource` |
| none of the above | — | ask the user | — |

## Running Phase 4 without aborting the suite

Every test file this skill writes imports something that does not exist yet.
That is an error at load time, and most runners treat a load error as fatal to
the whole run — the user's pre-existing green tests never execute, which looks
exactly like you broke their suite.

Verified in pytest: with one such file present, the default run reports
`1 error` and a neighbouring passing test does not run;
`--continue-on-collection-errors` reports `1 passed, 1 error`.

| Runner | Phase 4 invocation | Failure granularity |
|---|---|---|
| pytest | `pytest --continue-on-collection-errors` | one collection error per file |
| Vitest / Jest | default — a failing import fails that file, others still run | one suite-level failure per file |
| `go test` | `go test ./...` — the package fails to build | one build error per package |
| `cargo test` | default — the crate fails to compile | one compile error for the crate |
| RSpec | `rspec --force-color` — a load error aborts the run; run the new spec files separately to keep the baseline readable | one load error |
| JUnit 5 (Maven/Gradle) | compilation of the test sources fails | one compile error per module |

Where the runner aborts and has no continue flag, run the pre-existing suite and
the new files as two separate invocations. Never report a red you obtained by
deleting or excluding the user's tests.

## Baseline

Run the suite before writing anything:

- **Green** → proceed.
- **Red** → report which tests fail and ask whether to continue with that
  known-red set recorded, or stop. Do not silently absorb a pre-existing break:
  it makes every new red unattributable.
- **No tests at all** → a valid green baseline. Note it and proceed.

## Where the new files go

Follow the convention you detected, not a convention you prefer. If existing
tests sit beside their source, put yours there too; if they live in a `tests/`
tree that mirrors the source tree, mirror it.

The contracts are the exception: they always go in `docs/test-contracts/`,
whatever the stack, because they are documentation rather than test code.
