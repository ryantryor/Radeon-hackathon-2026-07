# Radeon Kitchen Pick with SmolVLA

## 1. Application

The project studies a Physical AI manipulation task: a Franka Panda robot must
pick up a cube placed at randomized positions in a rustic-kitchen Genesis
simulation. The policy receives two RGB views, robot joint state, and the
language instruction `Pick up the cube.` It predicts joint-position actions in
a closed loop.

The intended application is a compact benchmark for training and diagnosing
vision-language-action policies before a future real-robot deployment.

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
- Camera ablation, fixed episode manifests, visual perturbations, and dataset
  protocol validation as reproducible next experiments.

## 8. Limitations and Next Experiments

The next high-value experiments are:

1. Compare `both`, `overhead_only`, and `wrist_only` camera feeds using the
   same 50-episode manifest.
2. Generate targeted hard-case data and mix it with the original 100 episodes
   at a documented replay ratio.
3. Evaluate every checkpoint on the identical manifest across at least three
   seeds or 50 episodes.
4. Add brightness and sensor-noise perturbations during training, then test
   nominal and perturbed evaluation separately.
5. Report the sim-to-real risks and calibration plan before any hardware test.

These experiments are designed to improve evidence quality and technical depth
without hiding the negative controls.

## 9. Team

Chen Weiliang: environment setup, synthetic data generation, ROCm
configuration, SmolVLA training, closed-loop evaluation, failure analysis,
documentation, and demo preparation.
