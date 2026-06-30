# Repository Layout Restructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move the old root research workspace into a nested copyable template and establish root framework-development docs.

**Superseding note:** The template no longer carries its own `README.md`; human-facing template documentation now belongs in the framework root `README.md`, while copied projects use `AGENTS.md` as the in-project operating guide.

**Architecture:** The repository root becomes the framework source layer. `templates/ara-research-workspace/` becomes the complete research workspace copied into downstream projects.

**Tech Stack:** Markdown, shell scripts, OpenCode project configuration, managed skills, Python project scaffold.

---

### Task 1: Move Copyable Workspace Files

**Files:**
- Move: `AGENTS.md`, `README.md`, `.agents/`, `.opencode/`, `scripts/`, `research/`, `literature/`, `experiments/`, `ara/`, `src/`, `tests/`, `data/`, `paper/`, `external/`, `to_human/`, `opencode.jsonc`, `skills-lock.json`
- Target: `templates/ara-research-workspace/`

**Step 1: Create the target directory**

Run: `mkdir -p templates/ara-research-workspace`

**Step 2: Move workspace-owned files**

Move project files into `templates/ara-research-workspace/`. Keep local generated caches, such as `.opencode/node_modules/`, out of the template.

**Step 3: Verify expected files exist**

Run: `test -f templates/ara-research-workspace/AGENTS.md && test ! -e templates/ara-research-workspace/README.md`

### Task 2: Add Framework Root Files

**Files:**
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `docs/README.md`
- Create: `docs/adr/0001-framework-template-split.md`

**Step 1: Write root development guide**

Create a root `AGENTS.md` that clearly targets framework-development agents.

**Step 2: Write root README**

Create a root `README.md` that points users to `templates/ara-research-workspace/` for the copyable template.

**Step 3: Record the layout decision**

Create an ADR explaining the framework/template split.

### Task 3: Verify Structure

**Files:**
- Read: repository tree
- Run: shell syntax checks

**Step 1: Inspect top-level layout**

Run: `find . -maxdepth 2 -type d | sort`

Expected: root contains `docs/` and `templates/ara-research-workspace/`.

**Step 2: Check shell syntax**

Run: `bash -n templates/ara-research-workspace/scripts/remote_targets.sh templates/ara-research-workspace/scripts/remote_env.sh templates/ara-research-workspace/scripts/remote_python.sh templates/ara-research-workspace/scripts/remote_sync.sh templates/ara-research-workspace/scripts/remote_preflight.sh`

Expected: no output and exit code 0.
