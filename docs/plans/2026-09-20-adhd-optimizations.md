# ADHD-Optimized Research Template Upgrade Plan

Created: 2026-09-20
Status: Ready for implementation

## User feedback incorporated

- ✅ Remove experiment ID mapping; use semantic labels only
- ✅ Merge resume checklist into latest.md
- ✅ Skip estimate_minutes requirement
- ✅ Keep Mermaid static (no JavaScript enhancements)

## Accepted optimizations

### Priority 1: Immediate (Foundation)

#### 1.1 Visual dashboard (dashboard.html)
- **Location**: `rtmpl/templates/batchcom-research/to_human/dashboard.html`
- **Builder**: `rtmpl/templates/batchcom-research/src/dashboard_builder.py`
- **Content**:
  - Single-page HTML with inline CSS
  - Top: Research question + status badge
  - Center: Simplified evolution tree (last 3-5 steps + current branch)
  - Right panel: Action cards (next action, waiting, decisions)
  - Bottom: Last 3 experiments (one-line protocol + status)
  - Color coding: green (active), yellow (waiting), gray (closed), blue (candidate)
  - All links jump to specific Markdown sections
- **Auto-generation**: Agent regenerates after every record update
- **No external dependencies**: Pure HTML + inline styles

#### 1.2 Semantic experiment labels only
- **Remove**: `E<id>` references everywhere
- **Use**: `<topic>-<seq>` format (e.g., `batch-size-01`, `lr-schedule-02`)
- **Update**:
  - `research-state.yaml`: Change `experiments: []` from ID list to label list
  - `experiments/`: Rename directories to semantic labels
  - `protocol.md`: Replace `E<id>` with semantic label
  - All relation references use semantic labels
- **Validation**: `rtmpl check` ensures label uniqueness and format

#### 1.3 Resume checklist in latest.md
- **Location**: Add section to `rtmpl/templates/batchcom-research/to_human/latest.md`
- **New section** (after "Waiting / need from human"):
  ```markdown
  ## Resume checklist
  
  - [ ] Read current question and status above
  - [ ] Check evolution diagram: `evolution.mmd`
  - [ ] Review latest findings: `findings.md`
  - [ ] Confirm next action is clear
  - [ ] Note any waiting blockers
  ```
- **Auto-generation**: Agent updates checkboxes based on state

### Priority 2: Short-term (Consistency & Navigation)

#### 2.1 Automatic consistency checking
- **Add**: `rtmpl check --consistency` subcommand
- **Checks**:
  - All objects in `research-state.yaml` exist in target files
  - All relations have valid source and target objects
  - Links in `to_human/latest.md` point to existing files/sections
  - Semantic experiment labels match directory names
  - No orphaned experiment directories
- **Output**: Actionable fix suggestions (not just errors)
- **Hook**: Agent runs after every update

#### 2.2 Simplified automation mode
- **Replace**: `loop_control.inner` + `loop_control.outer` with single `automation_mode`
- **Options**:
  - `manual`: Every Inner and Outer Loop requires human confirmation
  - `semi-auto`: Inner Loop auto within approved scope, Outer Loop needs confirmation
  - `full-auto`: Both loops auto (for repetitive validation only)
- **Files to update**:
  - `research/policy.yaml`: Replace `loop_control` with `automation_mode`
  - `research-state.yaml`: Remove `loop_control`, add `automation_mode` if overriding policy
  - `docs/research-workflow.md`: Update documentation
- **Display**: Show current mode in `to_human/latest.md` and `dashboard.html`

### Priority 3: Medium-term (Interruption & Recovery)

#### 3.1 Pause/resume mechanism
- **Add**: `rtmpl pause` command
- **Captures**:
  - Current timestamp
  - Active file being viewed
  - Cursor position (if available)
  - Current task in progress
  - Next intended action
  - Unwritten thoughts/notes
- **Output**: `to_human/paused-context.md`
- **Resume**: Agent reads paused-context.md first when resuming
- **Auto-clear**: Deleted after successful resume

#### 3.2 Fill-in-the-blank templates
- **Update all seed templates** with guided prompts:
  - `hypotheses.md`: "If <condition>, then <observable result>, because <mechanism>"
  - `protocol.md`: Pre-filled example protocol (user replaces, not starts from blank)
  - `decisions.md`: "Options: A (<pros/cons>) vs B (<pros/cons>). Decision: <choice> because <one-line reason>"
  - `claims.md`: "Claim: <statement>. Scope: <limits>. Evidence: <refs>. Weakened if: <conditions>"
- **Benefit**: Reduces blank-page paralysis

#### 3.3 Enhanced evolution diagram (keep static)
- **Current**: `to_human/evolution.mmd`
- **Enhancement**: Better structure for manual inspection
  - Clear branch labels
  - Color-coded relations: support (green), challenge (red), authorize (blue)
  - Collapsible sections (manual collapse with comments)
  - Hover text in Mermaid tooltips
- **No JavaScript**: Keep as static Mermaid

### Priority 4: Long-term (Polish & Ergonomics)

#### 4.1 Quick decision template
- **Update**: `decisions.md` with structured format

#### 4.2 Enhanced rtmpl CLI
- **New commands**:
  - `rtmpl check --consistency`: Run all consistency checks
  - `rtmpl pause`: Capture interruption context
  - `rtmpl resume`: Show paused context and resume checklist
  - `rtmpl graph`: Render evolution.mmd to terminal or image
  - `rtmpl summary`: Show dashboard.html in terminal or open in browser

## Additional optimizations

### 5.1 Reduce cognitive load in research-state.yaml
Keep as pure index: only IDs, labels, relations, status. No prose.

### 5.2 Status badge system
Emoji indicators: 🔵 candidate, 🟢 active, 🟡 waiting, ⚪ closed

### 5.3 Link validation
Check all internal Markdown links resolve

### 5.4 Experiment naming convention
Enforce `experiments/<topic>-<seq>/` format

### 5.5 rtmpl doctor command
Health check: seed files exist, no TODOs, schema valid

### 5.6 Simplified relation types
4 core types: `tests`, `produces`, `supports`/`challenges`, `authorizes`

## Implementation sequence

1. **Phase 1**: 1.1, 1.2, 1.3
2. **Phase 2**: 2.1, 2.2, 5.1-5.6
3. **Phase 3**: 3.1, 3.2, 3.3
4. **Phase 4**: 4.1, 4.2

## Files to modify

### New files
- `src/dashboard_builder.py`
- `to_human/dashboard.html` (generated)
- `to_human/paused-context.md` (generated on pause)

### Updated files
- `AGENTS.md`: Document semantic labels, automation modes
- `to_human/latest.md`: Add resume checklist
- `research-state.yaml`: automation_mode
- `research/policy.yaml`: automation_mode
- `docs/research-workflow.md`: Loop docs
- `experiments/_template/protocol.md`: Fill-in examples
- `hypotheses.md`, `decisions.md`, `claims.md`: Structured templates
- `src/rtmpl/commands/`: New commands

## Testing checklist

- [ ] Create new project
- [ ] Verify dashboard.html
- [ ] Create experiment with semantic label
- [ ] Run `rtmpl check --consistency`
- [ ] Test pause/resume
- [ ] Verify links resolve
- [ ] Switch automation modes
- [ ] Run `rtmpl doctor`
- [ ] Migrate `repa` project
- [ ] Run `uv run pytest`

## Notes for implementation

- Follow ADR pattern
- Small commits, test each phase
- Use `uv run` for Python
- Version bump to 0.5.0
- Test against `repa` project
