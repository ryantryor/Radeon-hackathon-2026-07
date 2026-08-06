# Radeon Kitchen Pick with SmolVLA

## 1. Application

The project studies a Physical AI manipulation task: a Franka Panda robot must
pick up a cube placed at randomized positions in a rustic-kitchen Genesis
simulation. The policy receives two RGB views, robot joint state, and the
language instruction `Pick up the cube.` It predicts joint-position actions in
a closed loop.

The intended application is a compact **failure-aware benchmark for cluttered
kitchen manipulation**. It diagnoses where a vision-language-action policy
breaks before a future real-robot deployment, then supplies targeted hard cases
without discarding broad replay data.

## 2. System Architecture

```text
Genesis scripted expert
        |
        v
LeRobot episode dataset
        |
        v
SmolVLA fine-tuning on AMD ROCm
        |
        v
Genesis closed-loop evaluation
        |
        +--> videos, success summaries, failure coordinates
```

The data generator records synchronized `observation.state`, `action`, two
image streams, task text, and cube placement metadata. The evaluator resets a
fixed scene, renders both cameras, predicts an action chunk, executes one or
more actions, and repeats until the episode ends.

## 3. Data

The main dataset contains 100 expert episodes, 13,500 frames at 30 FPS, and
two RGB cameras: an overhead camera and an eye-in-hand wrist camera. The
Franka state and action are both 9-dimensional joint-position vectors.

The repository includes:

- `scripts/02_gen_data_custom_scene.py` for deterministic expert generation.
- `scripts/06_make_mixed_dataset.py` for broad replay plus targeted episodes.
- `scripts/08_validate_dataset.py` for protocol checks.
- `analysis/` for copied evaluation summaries and failure plots.

Large datasets and model weights are intentionally not committed to Git.

## 4. Model and Training

The policy is SmolVLA initialized from a local SmolVLA checkpoint. The
successful baseline used 4,000 training steps, batch size 4, and frozen visual
encoder settings from the workshop recipe. A continued effective 8,000-step
control was also evaluated.

The training script records per-step JSON metrics and can write TensorBoard
events under `output/train/<run-name>/tensorboard`. Closed-loop success is
treated as the primary task metric because imitation loss alone does not
capture compounding control error or contact dynamics.

## 5. AMD Radeon and ROCm Usage

The project was developed on an AMD Radeon cloud GPU with a ROCm-enabled
PyTorch environment. GPU use covers SmolVLA fine-tuning and policy inference;
Genesis uses the available GPU rendering/physics backend when the cloud image
supports it. Offline Hugging Face and Transformers modes are enabled so local
model files are reused without network access.

The repository documents the local SmolVLM2 backbone path because evaluation
must work in the offline cloud environment. FFmpeg and TorchCodec are used for
video data and evidence clips.

## 6. Results

| Experiment | Episodes | Seed | Success |
|---|---:|---:|---:|
| Prompt mismatch: `Pick up the red cube.` | 20 | 99 | 7/20 = 35% |
| Baseline: `Pick up the cube.` | 20 | 99 | 11/20 = 55% |
| Effective 8,000-step control | 20 | 99 | 8/20 = 40% |
| Baseline second seed | 20 | 123 | 1/20 = 5% |
| Targeted-only fine-tune | 20 | 99 | 1/20 = 5% |

The baseline remains the submission checkpoint because it has the best
controlled seed-99 result. The seed-123 result is disclosed as evidence that
the current policy is not yet robust.

## 7. Technical Contributions

- Reproducible Genesis expert data generation in a custom kitchen scene.
- LeRobot-compatible synchronized state, action, image, and task fields.
- Offline local-backbone loading for SmolVLA on ROCm.
- Closed-loop evaluation with fixed scene, anchor, camera layout, and seed.
- Prompt, training-step, seed, and targeted-data controls.
- Failure-coordinate analysis and a mixed replay data pipeline.
- Camera ablation, random camera dropout, localized occlusion, action-delay and
  friction stress tests, plus fixed episode manifests for paired comparisons.
- A visual-consistency uncertainty probe that can slow down and replan when
  perturbed action predictions disagree.
- A robustness-matrix runner that emits a success/retention table and SVG
  envelope without requiring plotting packages.

## 8. Sim-to-Real Evaluation Protocol

The project separates nominal performance from transfer stress tests. Every
condition uses the same placement manifest, and the nominal result is the
denominator for robustness retention:

```text
retention = stressed success rate / nominal success rate
```

The stressors are deliberately interpretable: brightness and RGB noise probe
the visual sensor gap; camera dropout and local occlusion probe missing visual
evidence; action delay probes timing; friction sweeps probe contact dynamics.
The results are stored under `output/eval/robustness_matrix/` and summarized by
`scripts/10_summarize_robustness.py` with Wilson intervals.

## 9. Limitations and Next Experiments

The next high-value experiments are:

1. Run the paired 50-episode camera ablation and robustness matrix on the ROCm
   cloud runtime.
2. Generate targeted hard-case data, mix it with the original 100 episodes at
   2:1 replay-to-targeted ratio, and evaluate the candidate on both seeds.
3. Compare camera-dropout training against nominal training under the same
   manifest.
4. Calibrate the synthetic stressor ranges from real camera and controller
   measurements before any hardware claim.

These experiments are designed to improve evidence quality and technical depth
without hiding the negative controls.

## 9. Team

Chen Weiliang: environment setup, synthetic data generation, ROCm
configuration, SmolVLA training, closed-loop evaluation, failure analysis,
documentation, and demo preparation.
