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
