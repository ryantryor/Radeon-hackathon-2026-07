# Experiment Log

Project: AMD Radeon / Genesis + SmolVLA kitchen pick task

## Dataset

| Dataset | Episodes | Frames | FPS | Cameras | Generation success |
|---|---:|---:|---:|---|---:|
| local/franka-kitchen-wrist-live | 1 | 135 | 30 | up + wrist | 1/1 = 100% |
| local/franka-kitchen-wrist-100ep | 100 | 13,500 | 30 | up + wrist | 100/100 = 100% |

## Training Runs

| Run | Init checkpoint | Dataset | Steps in run | Effective steps | Batch | Workers | Final loss | Time | Peak VRAM | Output |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| smolvla_kitchen_wrist_smoke | /workspace/models/smolvla_base | local/franka-kitchen-wrist-live | 20 | 20 | 1 | 0 | 0.0524 | 8s | 2.07 GB | output/train/smolvla_kitchen_wrist_smoke/final |
| smolvla_kitchen_wrist | /workspace/models/smolvla_base | local/franka-kitchen-wrist-100ep | 4,000 | 4,000 | 4 | 4 | 0.0113 | 599s | 2.26 GB | output/train/smolvla_kitchen_wrist/final |
| smolvla_kitchen_wrist_8000 | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | 4,000 | 8,000 | 4 | 4 | 0.0165 | 616s | 2.26 GB | output/train/smolvla_kitchen_wrist_8000/final |

## Evaluation Runs

| Eval run | Checkpoint | Dataset | Prompt | Episodes | Seed | Success | Video dir | Notes |
|---|---|---|---|---:|---:|---:|---|---|
| kitchen_eval | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | Pick up the red cube. | 20 | 99 | 7/20 = 35% | output/eval/kitchen_eval/videos | Prompt mismatch vs training data |
| kitchen_eval_prompt_cube | output/train/smolvla_kitchen_wrist/final | local/franka-kitchen-wrist-100ep | Pick up the cube. | 20 | 99 | 11/20 = 55% | output/eval/kitchen_eval_prompt_cube/videos | Prompt aligned with dataset task |
| kitchen_eval_prompt_cube_8000 | output/train/smolvla_kitchen_wrist_8000/final | local/franka-kitchen-wrist-100ep | Pick up the cube. | 20 | 99 | 8/20 = 40% | output/eval/kitchen_eval_prompt_cube_8000/videos | Same aligned prompt; effective 8,000 training steps |

## Current Takeaways

- Prompt alignment improved success from 35% to 55% on the same checkpoint, seed, scene, and dataset.
- Remaining failures cluster around harder cube placements and closed-loop drift.
- Continuing from 4,000 to an effective 8,000 steps reduced this evaluation from 55% to 40% under the current seed and 20-episode sample; more training is not automatically better.
- The next useful control is to repeat the 4,000-step and 8,000-step evaluations with another evaluation seed or increase the episode count before changing the model again.
