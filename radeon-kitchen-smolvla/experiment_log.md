# Experiment Log

Project: AMD Radeon / Genesis + SmolVLA kitchen pick task
Current best checkpoint: output/train/smolvla_kitchen_wrist/final

## Dataset

| Dataset | Episodes | Frames | FPS | Cameras | Generation success |
|---|---:|---:|---:|---|---:|
| local/franka-kitchen-wrist-live | 1 | 135 | 30 | up + wrist | 1/1 = 100% |
| local/franka-kitchen-wrist-100ep | 100 | 13,500 | 30 | up + wrist | 100/100 = 100% |
| local/franka-kitchen-wrist-targeted | targeted hard-case supplement | generated successfully | 30 | up + wrist | 40/40 = 100% |

## Training Runs

| Run | Init checkpoint | Dataset | Steps in run | Effective steps | Batch | Workers | Final loss | Time | Peak VRAM | Output |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| smolvla_kitchen_wrist_smoke | /workspace/models/smolvla_base | local/franka-kitchen-wrist-live | 20 | 20 | 1 | 0 | 0.0524 | 8s | 2.07 GB | output/train/smolvla_kitchen_wrist_smoke/final |
| smolvla_kitchen_wrist | /workspace/models/smolvla_base | local/franka-kitchen-wrist-100ep | 4,000 | 4,000 | 4 | 4 | 0.0113 | 599s | 2.26 GB | output/train/smolvla_kitchen_wrist/final |
| smolvla_kitchen_wrist_8000 | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | 4,000 | 8,000 | 4 | 4 | 0.0165 | 616s | 2.26 GB | output/train/smolvla_kitchen_wrist_8000/final |
| smolvla_kitchen_wrist_targeted_4000 | /workspace/models/smolvla_base or baseline local init | local/franka-kitchen-wrist-targeted | 4,000 | targeted control | 4 | 4 | recorded in remote train output | completed | about 2.3 GB | output/train/smolvla_kitchen_wrist_targeted_4000/final |

## Evaluation Runs

| Eval run | Checkpoint | Dataset | Prompt | Episodes | Seed | Success | Video dir | Notes |
|---|---|---|---|---:|---:|---:|---|---|
| kitchen_eval | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | Pick up the red cube. | 20 | 99 | 7/20 = 35% | output/eval/kitchen_eval/videos | Prompt mismatch vs training task |
| kitchen_eval_prompt_cube | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | Pick up the cube. | 20 | 99 | 11/20 = 55% | output/eval/kitchen_eval_prompt_cube/videos | Current best controlled result |
| kitchen_eval_prompt_cube_8000 | output/train/smolvla_kitchen_wrist_8000/final | local/franka-kitchen-wrist-100ep | Pick up the cube. | 20 | 99 | 8/20 = 40% | output/eval/kitchen_eval_prompt_cube_8000/videos | More steps did not help this closed-loop sample |
| kitchen_eval_prompt_cube_baseline_seed123 | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | Pick up the cube. | 20 | 123 | 1/20 = 5% | output/eval/kitchen_eval_prompt_cube_baseline_seed123/videos | Second seed; exposes high placement variance |
| kitchen_eval_prompt_cube_targeted_4000 | output/train/smolvla_kitchen_wrist_targeted_4000/final | local/franka-kitchen-wrist-targeted | Pick up the cube. | 20 | 99 | 1/20 = 5% | output/eval/kitchen_eval_prompt_cube_targeted_4000/videos | Targeted-only fine-tune collapsed; do not submit this checkpoint |

## Analysis Artifacts

| Artifact | Purpose |
|---|---|
| analysis/raw_eval/*.json | Local copies of all evaluation summaries |
| analysis/eval_episode_records.csv | One row per evaluated episode with cube coordinates and success flag |
| analysis/eval_comparison.md | Experiment comparison and interpretation |
| analysis/failure_coordinate_scatter.svg | Scatter plot of success/failure by cube coordinate |

## Current Takeaways

- Keep the original 4,000-step baseline as the current submission checkpoint because it is the best controlled seed-99 result.
- The prompt comparison improved success from 35% to 55%, showing that language conditioning affects the action policy.
- The effective 8,000-step control dropped from 55% to 40%, showing that more training steps and loss tracking alone are not reliable optimization targets.
- The second seed dropped to 5%, so the project should disclose high evaluation variance and avoid overstating robustness.
- The targeted-only fine-tune also dropped to 5%, which suggests hard-case data should be mixed with replay from the original broad dataset rather than replacing it.

## Next Experiment

Build a mixed replay dataset: retain the original 100 episodes, add targeted hard-case episodes around repeated failure coordinates, train with a lower learning rate or fewer steps, then evaluate on seed 99, seed 123, and preferably 50+ total episodes.

## Reproducibility Status (2026-08-05)

Completed in the repository:

- Added deterministic brightness and RGB sensor-noise perturbations to data
  generation and custom-scene evaluation.
- Added `both`, `overhead_only`, and `wrist_only` camera ablation modes.
- Added fixed evaluation manifests for paired 50-episode comparisons.
- Added failure-coordinate targeted placement manifests with deterministic
  jitter.
- Added a LeRobot mixed replay dataset builder with schema checks.
- Added a LeRobot dataset protocol validator.
- Added optional TensorBoard event logging to the training script.
- Added Wilson confidence intervals to generated evaluation summaries.
- Added `docs/sim_to_real.md` and `submission/TECHNICAL_REPORT.md`.

Still requiring the ROCm cloud runtime:

1. Generate the 50-episode manifest and run the three camera conditions.
2. Generate or validate the targeted dataset, build the mixed replay dataset,
   and train the conservative candidate.
3. Evaluate nominal and perturbed mixed-replay checkpoints on the same
   manifest and at least one second seed.
4. Copy the resulting JSON summaries, videos, TensorBoard screenshots, and
   final demo URL into the submission package.

The original 4,000-step checkpoint remains the submission fallback until a
new candidate beats it on a paired evaluation set without hiding the
seed-123 negative control.
