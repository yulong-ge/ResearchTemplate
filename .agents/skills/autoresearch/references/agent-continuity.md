# Agent Continuity: Optional Continuous Execution

Continuous research execution can be useful for hours-long unattended work, but it is optional. This reference covers how to set up the wall-clock loop on each platform when the user explicitly wants autonomous continuation.

## Optional Setup

The wall-clock loop is an operational aid. It fires every 20 minutes and simply tells the agent: "keep working, check if anything's wrong."

This is completely separate from the research inner/outer loops. The wall-clock loop is a fixed-interval prompt injection. The research loops run at experiment speed (minutes to hours per cycle). They will not sync and don't need to.

## Claude Code: /loop

If autonomous continuation is requested, run this:

```
/loop 20m Continue autoresearch. Read research/state.yaml and research/findings.md. Check: is the current experiment done? Are there errors? Is progress stalling? If everything is on track, keep working. If something is wrong, step back and fix it. Never idle.
```

### What Happens on Each Tick

The `/loop` message fires every 20 minutes. When it fires:

1. **Read state** — `research/state.yaml` and `research/findings.md` to remember where you are and what you've learned
2. **Check health** — is the current experiment running? Did it error? Is training diverging?
3. **If on track** → continue whatever you were doing (don't restart or re-plan)
4. **If stuck or broken** → step back, diagnose the issue, fix it, then continue
5. **If idle** → pick the next hypothesis or the next synthesis task

The tick is a nudge, not a phase boundary. If the previous tick's work isn't done, just keep going.

### When Experiments Run Longer Than 20 Minutes

This is normal and expected. On the next tick:
- Check if the experiment finished
- If still running: monitor for errors, do lightweight work (update notes, search papers)
- Don't restart or duplicate the experiment

### Context Recovery

Your primary memory between ticks is `research/state.yaml` and `research/findings.md`. Keep them updated after every experiment and reflection. If you lose context, read both files plus `research/research-log.md` to reconstruct where you are.

## OpenClaw: Cron Job

If autonomous continuation is requested, use the `cron.add` tool to create a recurring job bound to the current chat session:

```json
{
  "name": "autoresearch-loop",
  "schedule": { "kind": "every", "everyMs": 1200000 },
  "sessionTarget": "current",
  "payload": {
    "kind": "agentTurn",
    "message": "Continue autoresearch. Read research/state.yaml and research/findings.md. Check: is the current experiment done? Are there errors? Is progress stalling? If everything is on track, keep working. If something is wrong, step back and fix it. Never idle."
  }
}
```

Key details:
- `sessionTarget: "current"` binds the cron to the current chat session (resolved to `session:<sessionKey>` at creation time), so it maintains conversation context across ticks
- `everyMs: 1200000` = 20 minutes
- Verify with `cron.list` that the job is created and enabled
- To check run history later: `cron.runs` with the job ID

### Context Between Cron Ticks

OpenClaw cron invocations may start fresh each time. Your workspace files are your memory:

- `research/state.yaml` — where you are, what's active
- `research/findings.md` — what you've learned (read this every time!)
- `research/research-log.md` — what happened chronologically

Keep these updated after every action so the next cron tick can pick up seamlessly.

### Progress Reports

OpenClaw can't `open` HTML files locally like Claude Code can. When you have something to report:

1. Generate a PDF progress summary (use Python with reportlab, matplotlib, or similar)
2. Include: research question, key results, optimization trajectory plot, current understanding, next steps
3. Send it to the user via Telegram, WhatsApp, or Slack — whichever channel they use
4. When you get an exciting result or interesting plot, send it right away — don't wait for a full report

## Research State as Ground Truth

Both platforms share the same ground truth: the workspace files.

| File | Purpose | Update Frequency |
|---|---|---|
| `research/state.yaml` | Machine-readable state | After every experiment and reflection |
| `research/research-log.md` | Decision timeline | After every significant action |
| `research/findings.md` | Narrative understanding + project memory | After every outer loop |
| `experiments/*/results/` | Raw experimental data | After every experiment |

The wall-clock loop (`/loop` or cron) is just the trigger. The workspace files are the memory. Keep them current whenever you choose to run unattended.
