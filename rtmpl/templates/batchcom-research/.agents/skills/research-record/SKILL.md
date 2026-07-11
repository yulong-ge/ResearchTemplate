---
name: research-record
description: Use when recording research progress or results, deciding where a finding/log/decision/run-note belongs, resuming a research project, or initializing the research/ workspace.
---

# Research Record

## Overview

Recording hygiene for a human-collaborative research project. The human sets direction and rhythm; you record in the right place so nothing is lost and resume is fast. This skill answers **where each kind of information goes** and **how to read it back without blowing up context**.

## Resume

1. Read `research/overview.md` first — the only file meant for full-read. Keep it under ~150 lines.
2. Never blind-read anything else (see Read Discipline below).

## Where Each Fact Lives

Single home per fact; never duplicate content across files — link instead.

| File | Holds | Not here |
|---|---|---|
| `research/overview.md` | current state, direction, next step, blockers, pending decisions, success criteria | history, mature conclusions |
| `research/log.md` | append-only timeline: one-liner + link per event | full run records |
| `research/ideas.md` | hypotheses (prediction + rationale), candidate/parked/rejected | validated conclusions |
| `research/findings.md` | mature conclusions, cross-run patterns, constraints, ruled-out paths, open scientific questions | engineering pitfalls, running narrative |
| `research/decisions.md` | decisions + rationale + alternatives (topic-retrievable) | timeline |
| `research/environment.md` | conda env, CUDA/GPU, package versions, data/model registry, seeds | path-resolution logic (`src/paths.py`) |
| `research/runs/<YYYY-MM-DD>-<slug>.md` | one significant experiment: hypothesis→prediction→method→results→interpretation | cross-run synthesis |
| `literature/survey.md` (+ per-paper notes) | reading notes & aggregate map | |
| `paper/` | manuscript assets (later) | |

## Three Disciplines

**1. `runs/` admission threshold.** Not every run gets a record.
- Throwaway / exploratory runs (running someone's repo, debugging, tweaking) → one line in `log.md`.
- Significant runs (tests a hypothesis / citable result / surprise) → a `runs/<slug>.md` from `templates/runs/TEMPLATE.md`.
- Exploratory run that turns significant → promote: write the `runs/` entry, change the `log.md` line to link it.

**2. Pointer pattern — no content duplication.** Each fact has ONE home; other files hold LINKS.
- `overview.md` and `log.md` are indexes (summary + link), never re-narrate full content.
- Update a fact → update its home file; update a pointer only if its summary text changed.
- `runs/` records are immutable historical snapshots — a later hypothesis change does not make them "stale".

**3. Read discipline (context economy).**
- `overview.md` → only blind full-read; keep it curated and small.
- `log.md` → read the tail for recent state / next serial.
- cumulative files (`findings`, `ideas`, `decisions`, `environment`) → grep/offset, never blind full-read; archive to `<file>-archive.md` past ~300 lines.
- `runs/<slug>.md` → read individually by link or grep.

## W&B vs Markdown Boundary

- **→ W&B:** metrics, curves, media, hyperparams, system metrics, config snapshot, code version, data/model artifacts (versioned). NEVER checkpoints / `.pt` / `.safetensors` / caches.
- **→ Markdown:** human narrative, interpretation, decision rationale, single-run meaning, mature conclusions, ideas, provenance.
- **→ gitignored (neither):** large raw artifacts → `RESULTS_ROOT`; reusable project/shared data and models → their canonical roots in `src/paths.py`.

## Common Mistakes

| Mistake | Correct Pattern |
|---|---|
| Re-narrating a run in `overview.md` or `log.md` | One-liner + link; full record only in `runs/<slug>.md` |
| Blind full-reading `findings.md` or `decisions.md` | grep the topic or read by offset |
| Creating a `runs/` file for a throwaway debug run | One line in `log.md` instead |
| Copying a hypothesis definition into a run record | Reference `ideas.md#H#`; the run is a snapshot |
| Uploading checkpoints to W&B | Only metrics/media/config; checkpoints → `RESULTS_ROOT` |
| Updating one file and leaving a stale duplicate elsewhere | Single home + links; update the home, pointers only if summary changed |

## Notes

- **ctx_memory** / **ctx_search** are OpenCode cross-session machine-memory tools — NOT research files. If they conflict with repo docs or `overview.md`, trust the docs and clean the stale memory.
- **Git:** commit at real milestones — `research(init|run|finding|reflect): <summary>`.
- **Initializing a workspace:** scaffold `research/` from this skill's `templates/`; create `runs/` empty.
- **Quality test:** after ~30 runs, `research/findings.md` alone should let a human draft an Abstract. If it reads like a log, the synthesis is missing.
