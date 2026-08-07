# Superpowers integration

This skill orchestrates; Superpowers supplies the technical rules.

| Step | Superpowers skill | Role |
|---|---|---|
| Phase 3, before writing | `test-driven-development` → `writing-good-tests.md` | Assertion quality rules |
| Phase 4, unexplained red | `systematic-debugging` | Diagnose rather than guess |
| Phase 5 hand-off | `test-driven-development` | Implements against the harness |

Do not invoke `brainstorming`: Phase 1 already frames the features, from a
narrower angle, and running both doubles the questions asked of the user.

## Relationship to test-driven-development

They are not competing. `test-driven-development` writes one test, then
implements it immediately — the right loop when one agent owns the whole cycle.
This skill produces a standing harness for a batch of features and hands
implementation off. Use it when the person writing the tests is not the person
writing the code.

After Phase 5, `test-driven-development` resumes at GREEN: the RED phase is
already done and recorded.

## Relationship to feature-status-tracker

`feature-status-tracker` owns `FEATURES.md` and the branch/PR pipeline. This
skill only ever reads that file. If the user wants features clarified, tested
**and** implemented, they want `feature-status-tracker`; this skill covers the
test-writing slice of that pipeline.

## Fallback when Superpowers is absent

Say so once, then apply the assertion rules inline:

- Expected values are literals derived by hand from the contract.
- Never assert against a value computed by the code under test, or by its
  helpers — the assertion passes no matter what the code does.
- Never assert on a constant's value (`MAX_RETRIES == 5`); assert on the
  behavior that depends on it.
- Mock only what is genuinely slow or external. A mocked target cannot fail.

Never block the workflow because Superpowers is missing.
