# ResearchTemplate context

This repository defines a template lifecycle tool and a human-guided research workspace. The framework owns template files and update state; a generated project owns research facts and experiment evidence.

## Language

**Managed file**:
A template-maintained file that the updater may refresh after normal conflict handling.
_Avoid_: framework file, protected file

**Seed-only record**:
A file seeded by the template and then owned by the generated project. Template updates preserve it, including `--force`.
_Avoid_: immutable record, generated record

**Generated view**:
An index or graph derived from project records. It is disposable and can be rebuilt; project records remain authoritative.
_Avoid_: research state, canonical graph

**Research fact**:
A hypothesis, experiment, claim, decision, finding, or evidence item with one declared project-owned home.
_Avoid_: session dump, duplicate ledger

**Finite authorization**:
A human decision that binds an experiment to a protocol/configuration, run scope, budget, retry limit, stop condition, and optional expiry.
_Avoid_: blanket approval, unlimited grant
