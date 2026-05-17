# Skill Routing: Current Research Workspace

The `autoresearch` skill orchestrates research work. Domain skills handle specialized tasks. Use this reference to pick among the skills that are actually installed in this workspace.

## Routing Principle

When a task becomes domain-specific, identify the closest installed skill and read its `SKILL.md` before acting. Prefer the most specific skill that matches the current bottleneck.

## Installed Skill Map

### Research Planning and Direction

| Task | Skill |
|---|---|
| Evaluate whether a research direction is worth pursuing | `idea-evaluator` |
| Generate or refine research ideas | `brainstorming-research-ideas` |
| Explore more novel directions systematically | `creative-thinking-for-research` |
| Orchestrate the full research loop | `autoresearch` |

### Research Memory and Provenance

| Task | Skill |
|---|---|
| Compile a structured research artifact | `ara-compiler` |
| Record provenance after a meaningful work unit | `ara-research-manager` |
| Audit whether a claim is epistemically well-supported | `ara-rigor-reviewer` |

### Mechanistic Interpretability

| Task | Skill |
|---|---|
| Analyze transformer circuits and internal mechanisms | `transformer-lens-interpretability` |
| Train sparse autoencoders for feature discovery | `sparse-autoencoder-training` |
| Run intervention-based causal analysis | `pyvene-interventions` |
| Run remote activation patching and intervention workflows | `nnsight-remote-interpretability` |

### Image Generation and Diffusion

| Task | Skill |
|---|---|
| Work on Stable Diffusion generation or adaptation workflows | `stable-diffusion-image-generation` |

### Training, Adaptation, and Scaling

| Task | Skill |
|---|---|
| Parameter-efficient fine-tuning workflows | `peft-fine-tuning` |
| Multi-GPU or distributed training with a lightweight abstraction | `huggingface-accelerate` |

### Evaluation and Experiment Tracking

| Task | Skill |
|---|---|
| Standard model evaluation and benchmark harness usage | `evaluating-llms-harness` |
| Track experiments, metrics, artifacts, and dashboards in W&B | `weights-and-biases` |
| Inspect training curves and scalar logs locally | `tensorboard` |
| Track experiments with SwanLab | `experiment-tracking-swanlab` |

### Research Writing and Figures

| Task | Skill |
|---|---|
| Write or refine ML/AI paper sections | `ml-paper-writing` |
| Design or critique technical paper figures | `figure-designer` |
| Generate publication-quality plots | `academic-plotting` |

## Common Workflows

### "I am starting a new research direction"

1. Read `research/state.yaml`, `research/findings.md`, and `research/current-task.md`
2. Use `brainstorming-research-ideas` or `creative-thinking-for-research` to generate or refine candidate ideas
3. If one candidate idea now needs a structured go/no-go judgment, launch a fresh subagent and use `idea-evaluator` there so the evaluation stays isolated from the active working context
4. Record the chosen direction in `research/state.yaml` and `research/exploration-tree.yaml`

### "I need to run an interpretability experiment"

1. Choose among `transformer-lens-interpretability`, `sparse-autoencoder-training`, `pyvene-interventions`, and `nnsight-remote-interpretability`
2. Write a confirmatory protocol in `experiments/protocols/` if the experiment is meant to support or reject a claim
3. Save outputs under `experiments/results/<experiment-id>/`
4. Update `experiments/logs/`, `research/findings.md`, and `research/research-log.md`

### "I need to train or adapt a model"

1. Use `stable-diffusion-image-generation` for diffusion workflows when relevant
2. Use `peft-fine-tuning` for adapter-style or low-rank adaptation
3. Use `huggingface-accelerate` for scalable local multi-GPU execution
4. Track runs with `weights-and-biases`, `tensorboard`, or `experiment-tracking-swanlab`

### "I need to assess whether a result is solid enough to keep"

1. Update `research/findings.md` with the current interpretation
2. If the claim matters, use `ara-rigor-reviewer`
3. After a meaningful synthesis step, use `ara-research-manager`

## Adding More Skills Later

This workspace intentionally installs only a focused subset of skills.

If future projects need capabilities that are not currently installed, browse the AI Research Skills repository and add the missing skills through `npx skills` rather than inventing ad hoc local replacements:

- `https://github.com/Orchestra-Research/AI-research-SKILLs`

Prefer installing only the skills that match the actual project bottlenecks so the workspace stays focused and easy for agents to route.
