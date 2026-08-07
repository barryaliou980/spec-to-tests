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

## Usage

### 1. Open a session in your project

The skill reads your project to work out which test runner you use and how your
existing tests are written, so run it from the repository you want tests for —
not from an empty directory.

Your suite should be green before you start. If it is already red, the skill
says which tests fail and asks whether to continue; if you have no tests at all,
that counts as green and it proceeds.

### 2. Say what you want covered

In Claude Code, just describe it in plain language:

> Here are three features I need covered — write the tests only, no
> implementation.

Or point at a file:

> Write the tests for the features listed in `FEATURES.md`. Tests only.

Claude detects the skill automatically — you don't have to name it. If you'd
rather be explicit, type `/spec-to-tests`.

### 3. Answer the clarification questions

One feature at a time, it asks what it needs to draw a boundary table:
observable behavior, the limits on each input, which errors are expected. It
will not ask about storage, framework or algorithm — those don't change the
tests.

Answer normally, no special format.

### 4. Validate the contract

Before writing a single test, it shows you the cases it intends to cover and
stops:

```
valide   : 1, 9999, 10000
> limite : 10001, 2**31
< limite : 0, -1
dégénéré : None, "", "abc", 10000.5
```

Correct anything wrong here — this is the cheap moment. A wrong contract
produces a whole file of wrong tests.

### 5. Get your harness

Once you approve, it writes one test file per feature, runs the suite, and
reports the exact failure for each test. Then it stops.

### 6. Hand off

Implement them yourself, or pass the report to
`superpowers:test-driven-development` (feature by feature) or
`feature-status-tracker` (full branch/PR pipeline). The RED phase is already
done and recorded, so implementation resumes straight at GREEN.

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

## Utilisation

1. Ouvre une session Claude Code **dans le projet** à couvrir — le skill lit ton
   repo pour détecter ton runner de test et copier tes conventions existantes.
   Ta suite doit être verte au départ (aucun test = vert aussi).
2. Dis simplement : *« Voici les fonctionnalités à couvrir, écris juste les
   tests, pas le code. »* — ou pointe un fichier : *« Écris les tests des
   features de `FEATURES.md`, tests uniquement. »* Claude détecte le skill tout
   seul ; sinon tape `/spec-to-tests`.
3. Réponds aux questions de clarification, une fonctionnalité à la fois :
   comportement observable, limites des entrées, erreurs attendues. Aucun format
   particulier.
4. **Valide le contrat** — le skill te montre les cas qu'il compte tester et
   s'arrête. C'est le moment pas cher pour corriger : un contrat faux produit un
   fichier entier de tests faux.
5. Il écrit les tests, lance la suite, et te rend l'échec exact attendu pour
   chaque test. Puis il s'arrête là.
6. Implémente toi-même, ou passe le rapport à
   `superpowers:test-driven-development` ou `feature-status-tracker`. La phase
   RED est déjà faite et enregistrée : l'implémentation reprend directement au
   vert.

Au-delà de ~8 fonctionnalités, le skill propose de découper en plusieurs runs —
l'analyse aux frontières produit sinon un harnais trop gros pour être relu d'un
coup.

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
