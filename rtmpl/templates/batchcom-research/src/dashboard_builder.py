"""Build to_human/dashboard.html from the project's research state.

Stdlib + PyYAML only (the project already depends on pyyaml). Run from the
project root:

    uv run python src/dashboard_builder.py

The output is a single self-contained HTML page with inline CSS — no JS and no
external assets — so it opens from a file:// link and can be regenerated after
every record update.
"""
from __future__ import annotations

import csv
import html
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "research-state.yaml"
POLICY_FILE = ROOT / "research" / "policy.yaml"
TRAJECTORY_FILE = ROOT / "to_human" / "trajectory.csv"
OUTPUT_FILE = ROOT / "to_human" / "dashboard.html"

STATUS_EMOJI = {
    "candidate": "🔵",
    "active": "🟢",
    "waiting": "🟡",
    "closed": "⚪",
}
STATUS_COLOR = {
    "candidate": "#2563eb",
    "active": "#16a34a",
    "waiting": "#ca8a04",
    "closed": "#6b7280",
}
AUTOMATION_MODES = {"manual", "semi-auto", "full-auto"}


def _load_yaml(path: Path) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except yaml.YAMLError as exc:
        raise SystemExit(f"error: {path}: invalid YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"error: {path}: expected a YAML mapping")
    return payload


def _esc(value) -> str:
    return html.escape(str(value)) if value is not None else ""


def _none_or(value) -> str:
    return _esc(value) if value else "<em>none</em>"


def _card(title: str, body_html: str) -> str:
    return f'<div class="card"><h2>{_esc(title)}</h2>{body_html}</div>'


def _automation_mode(state: dict, policy: dict) -> str:
    mode = state.get("automation_mode", "inherit_policy")
    if mode == "inherit_policy":
        mode = policy.get("automation_mode", "manual")
    if mode not in AUTOMATION_MODES:
        mode = "manual"
    return mode


def _relations_summary(state: dict) -> str:
    relations = state.get("relations") or []
    if not relations:
        return "<em>none</em>"
    counts: dict[str, int] = {}
    for rel in relations:
        if isinstance(rel, dict):
            counts[rel.get("type", "?")] = counts.get(rel.get("type", "?"), 0) + 1
    items = "".join(
        f'<li><span class="rel">{_esc(t)}</span> × {n}</li>' for t, n in sorted(counts.items())
    )
    return f"<ul>{items}</ul>"


def _experiments_html(state: dict) -> str:
    experiments = state.get("objects", {}).get("experiments") or []
    if not experiments:
        return "<em>none</em>"
    items = "".join(
        f'<li><a href="experiments/{_esc(label)}/protocol.md">{_esc(label)}</a></li>'
        for label in experiments
    )
    return f"<ul>{items}</ul>"


def _trajectory_html() -> str:
    if not TRAJECTORY_FILE.is_file():
        return "<em>none</em>"
    with TRAJECTORY_FILE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return "<em>none</em>"
    recent = rows[-3:]
    items = "".join(
        "<li>"
        f"<strong>{_esc(r.get('experiment_id', ''))}</strong> "
        f"{_esc(r.get('metric', ''))} "
        f"({ _esc(r.get('delta', '')) })"
        "</li>"
        for r in recent
    )
    return f"<ul>{items}</ul>"


def build_dashboard() -> Path:
    state = _load_yaml(STATE_FILE)
    policy = _load_yaml(POLICY_FILE)

    status = state.get("status", "candidate")
    emoji = STATUS_EMOJI.get(status, "⚪")
    color = STATUS_COLOR.get(status, "#6b7280")
    question = state.get("research_question") or "none"
    mode = _automation_mode(state, policy)
    next_action = state.get("next_action") or {}
    waiting = state.get("waiting") or {}

    next_body = (
        f'<p><strong>Owner:</strong> {_none_or(next_action.get("owner"))}</p>'
        f'<p><strong>Action:</strong> {_none_or(next_action.get("text"))}</p>'
        f'<p><strong>Done when:</strong> {_none_or(next_action.get("done_when"))}</p>'
    )
    waiting_body = (
        f'<p><strong>Reason:</strong> {_none_or(waiting.get("reason"))}</p>'
        f'<p><strong>On:</strong> {_none_or(waiting.get("on"))}</p>'
        f'<p><strong>Unblock:</strong> {_none_or(waiting.get("unblock_action"))}</p>'
    )
    decision_body = (
        f'<p><strong>Active direction:</strong> {_none_or(state.get("active_direction"))}</p>'
        f'<p><strong>Active hypothesis:</strong> {_none_or(state.get("active_hypothesis"))}</p>'
        f'<p><a href="decisions.md">decisions.md</a></p>'
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research dashboard</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", sans-serif; margin: 0;
         background: #f8fafc; color: #0f172a; }}
  header {{ background: #fff; border-bottom: 1px solid #e2e8f0;
           padding: 1rem 1.5rem; }}
  h1 {{ font-size: 1.25rem; margin: 0 0 .4rem; font-weight: 600; }}
  .badge {{ display: inline-block; padding: .15rem .6rem; border-radius: 999px;
           color: #fff; background: {color}; font-size: .8rem; }}
  .meta {{ color: #64748b; font-size: .85rem; margin-top: .3rem; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
         gap: 1rem; padding: 1.25rem; }}
  .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: .6rem;
          padding: 1rem 1.1rem; }}
  .card h2 {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .05em;
             color: #64748b; margin: 0 0 .6rem; font-weight: 600; }}
  .card p {{ margin: .25rem 0; font-size: .9rem; }}
  ul {{ margin: .25rem 0; padding-left: 1.1rem; font-size: .9rem; }}
  a {{ color: #2563eb; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .links {{ padding: 0 1.25rem 1.5rem; font-size: .85rem; color: #64748b; }}
  .links a {{ margin-right: .9rem; }}
</style>
</head>
<body>
<header>
  <h1>{_esc(question)}</h1>
  <span class="badge">{emoji} {_esc(status)}</span>
  <div class="meta">Automation: {_esc(mode)}</div>
</header>
<main>
  {_card("Next action", next_body)}
  {_card("Waiting / need from human", waiting_body)}
  {_card("Direction & decisions", decision_body)}
  {_card("Relations", _relations_summary(state))}
  {_card("Recent experiments", _experiments_html(state))}
  {_card("Trajectory", _trajectory_html())}
</main>
<div class="links">
  Records:
  <a href="to_human/latest.md">latest.md</a>
  <a href="hypotheses.md">hypotheses.md</a>
  <a href="findings.md">findings.md</a>
  <a href="claims.md">claims.md</a>
  <a href="decisions.md">decisions.md</a>
  <a href="research-log.md">research-log.md</a>
  <a href="to_human/evolution.mmd">evolution.mmd</a>
  <a href="research-state.yaml">research-state.yaml</a>
</div>
</body>
</html>
"""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    return OUTPUT_FILE


if __name__ == "__main__":
    out = build_dashboard()
    print(f"wrote {out.relative_to(ROOT)}")
    sys.exit(0)
