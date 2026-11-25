# Framework toolchain

Use Git, uv, Python 3.11 or newer, and Node 22.12 or newer. From the framework root:

```sh
uv sync --locked
npm ci
uv run --locked python scripts/check.py
```

Run `uv run --locked python scripts/check.py format` to apply source formatting.
Ruff formats Python and checks the existing framework and test rules. Prettier
formats active Markdown, JSON/JSONC, and YAML. Markdownlint checks Markdown,
Taplo checks TOML formatting and syntax, and `sh -n` checks the POSIX hooks.
pytest runs the existing product tests. The file list includes hidden tracked
files and unignored additions. Formatters preserve the legacy template payload,
historical ADRs and plans, historical research, and archived Agent Notes.
The legacy template still participates in the existing Ruff lint and product tests.

Python tools use [uv.lock](../uv.lock). Node tools use [package-lock.json](../package-lock.json).
Both locks are repository-owned. Upgrade tools by changing the owning dependency
and regenerating its lock.

## Git hooks

After installing dependencies, inspect `git config --get core.hooksPath` and
`git rev-parse --git-path hooks` for existing hook configuration. If no custom
hooks are installed, enable the repository hooks:

```sh
git config --local core.hooksPath .githooks
```

With an existing hook setup, integrate the staged and push commands in that setup.
The [commit hook](../.githooks/pre-commit) formats staged blobs, then copies the
index into a temporary directory and checks that snapshot. The formatter may
apply compatible formatting to the worktree. If it reports a patch conflict,
compare `git diff` and `git diff --cached` and keep the intended edits. Stage
formatting requires an existing commit. For a first commit, format before staging.
Formatter, lint, or test failures stop the commit. The [push hook](../.githooks/pre-push)
checks the current worktree.

[GitHub Actions](../.github/workflows/check.yml) uses the same check entry point
for PRs and pushes to `main`, with read-only repository permissions.
