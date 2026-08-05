# Radeon Kitchen Pick with SmolVLA

> AMD AI DevMaster Hackathon 2026, Physical AI track
> Team: Chen Weiliang / 陈伟亮

Repository: https://github.com/ryantryor/Radeon-hackathon-2026-07/tree/main/radeon-kitchen-smolvla

## Project Summary / 项目简介

This project fine-tunes a vision-language-action policy for a Franka Panda robot to pick up a cube in a randomized rustic-kitchen Genesis simulation. The workflow is expert synthetic data generation, LeRobot dataset packaging, SmolVLA fine-tuning, then closed-loop Genesis evaluation on AMD Radeon ROCm cloud hardware.

本项目在 AMD Radeon ROCm 云服务器上，用 Genesis 生成机器人专家抓取轨迹，再用 LeRobot 数据格式微调 SmolVLA，让 Franka 机械臂根据顶视相机、手腕相机、当前关节状态和语言指令完成方块抓取。最终指标不是训练 loss，而是闭环仿真中真实抓起并保持方块的成功率。

Pipeline / 技术链路:

    Genesis expert data -> LeRobot dataset -> SmolVLA fine-tuning -> Genesis closed-loop evaluation

Current best submission checkpoint / 当前提交模型:

- Checkpoint: output/train/smolvla_kitchen_wrist/final
- Dataset: local/franka-kitchen-wrist-100ep
- Prompt: Pick up the cube.
- Best controlled result: 11/20 = 55% on seed 99
- Robustness note: the same checkpoint scored 1/20 = 5% on seed 123, so the result is promising but not yet robust across random placements.

## Key Results / 核心指标

| Experiment | Checkpoint | Prompt | Episodes | Seed | Success | Lesson |
|---|---|---|---:|---:|---:|---|
| Prompt mismatch | 4,000-step baseline | Pick up the red cube. | 20 | 99 | 7/20 = 35% | Language instruction changes the action policy. |
| Current best | 4,000-step baseline | Pick up the cube. | 20 | 99 | 11/20 = 55% | Keep this as the submission checkpoint. |
| More steps control | Effective 8,000-step baseline | Pick up the cube. | 20 | 99 | 8/20 = 40% | Lower or similar loss does not guarantee better closed-loop control. |
| Second seed | 4,000-step baseline | Pick up the cube. | 20 | 123 | 1/20 = 5% | Evaluation variance is high and must be disclosed. |
| Targeted-only fine-tune | 4,000-step targeted data run | Pick up the cube. | 20 | 99 | 1/20 = 5% | Hard-case-only data likely caused distribution shift or forgetting. |

The analysis artifacts are in analysis/:

- analysis/eval_comparison.md
- analysis/eval_episode_records.csv
- analysis/failure_coordinate_scatter.svg
- analysis/raw_eval/*.json

## Development Process / 开发过程

### 1. Environment setup / 环境配置

- GPU: AMD Radeon cloud GPU
- ROCm / PyTorch: ROCm-enabled PyTorch environment
- Simulation: Genesis
- Dataset format: LeRobot
- Policy: SmolVLA, about 450M total parameters with roughly 100M trainable parameters during fine-tuning
- Video tooling: FFmpeg and TorchCodec for LeRobot video data

Key engineering fixes:

- Installed and started SSH service on the cloud instance when the image did not expose SSH by default.
- Forced Hugging Face and Transformers offline mode so the server uses local model files instead of downloading from the internet.
- Patched evaluation config to reuse the local SmolVLM2 backbone path. Without this, evaluation tried to reach Hugging Face and failed on the offline cloud server.
- Used escaped task arguments in shell commands so Pick up the cube. is passed as one prompt instead of being split by PowerShell or bash quoting.

### 2. Synthetic data / 合成数据

We generated a 100-episode rustic-kitchen dataset with a scripted expert controller. Each episode records two RGB cameras, robot state, expert action, task text, and cube placement metadata.

| Dataset | Episodes | Frames | FPS | Cameras | Generation success |
|---|---:|---:|---:|---|---:|
| local/franka-kitchen-wrist-100ep | 100 | 13,500 | 30 | overhead up + wrist camera | 100/100 = 100% |

Why this matters / 意义:

- Synthetic data lets us collect many labeled robot trajectories without a physical robot.
- LeRobot standardization keeps observation, action, video, and task fields aligned with SmolVLA training.
- Cube coordinate metadata makes failure analysis possible after closed-loop evaluation.

### 3. Training / 模型训练

The best model is the 4,000-step SmolVLA fine-tune from the local base checkpoint. The effective 8,000-step control continued from that checkpoint for another 4,000 steps, but closed-loop success dropped from 55% to 40% on seed 99.

Important lesson / 重要知识点: imitation loss measures how well the model matches expert actions in the dataset. A robot policy must also survive closed-loop compounding error, contact dynamics, and camera feedback. Therefore loss is useful for monitoring training, but success rate is the real task metric.

### 4. Closed-loop evaluation / 闭环评估

Evaluation keeps the scene, anchor, camera layout, dataset stats, action dimension, and task prompt controlled. The robot repeatedly observes, predicts an action chunk, executes, and observes again. This tests whether the learned policy can recover from its own small mistakes.

Recommended evaluation command:

    source /workspace/rdna/bin/activate
    cd /workspace/Robot_synthetic_data_generation_workshop
    export HF_HUB_OFFLINE=1
    export TRANSFORMERS_OFFLINE=1
    python scripts/03_eval.py \
      --policy-type smolvla \
      --checkpoint output/train/smolvla_kitchen_wrist/final \
      --dataset-id local/franka-kitchen-wrist-100ep \
      --task=Pick\ up\ the\ cube. \
      --camera-layout up_wrist \
      --n-episodes 20 \
      --seed 99 \
      --record-video \
      --run-name kitchen_eval_prompt_cube

### 5. Failure analysis / 失败分析

The failure coordinate scatter plot shows where each model succeeds or fails in robot-local cube coordinates. Two findings guide the next iteration:

- The current best checkpoint succeeds on many seed-99 placements, but still fails at several lateral and far-reach positions.
- Targeted-only fine-tuning collapsed to 5% on the same seed. This suggests hard-case data should be mixed with replay from the original broad dataset instead of replacing the original distribution.

Next training plan / 下一步训练计划:

1. Keep the original 100 episodes as replay data.
2. Add targeted data around the repeated failure regions.
3. Train on a mixed dataset, for example original:targeted at 2:1 or 3:1.
4. Use a lower learning rate or fewer fine-tune steps.
5. Re-evaluate with seed 99 and seed 123 before claiming improvement.

## Code Sources and Original Contributions / 代码来源说明

Base project and workshop reference:

- AMD-DEV-CONTEST/Robot_synthetic_data_generation_workshop
- AMD-DEV-CONTEST/Radeon-hackathon-2026-07 starter repository

Open-source models:

- lerobot/smolvla_base
- HuggingFaceTB/SmolVLM2-500M-Video-Instruct

Model weights and generated datasets are not redistributed in this repository because they are large artifacts and keep their original licenses.

Our project-specific contributions / 本项目原创工作:

- Configured the AMD Radeon ROCm cloud runtime for Genesis, LeRobot, SmolVLA, video decoding, and SSH access.
- Generated and validated the rustic-kitchen wrist-camera dataset.
- Patched SmolVLA training/evaluation for local offline backbone loading.
- Ran controlled evaluations for prompt wording, training steps, second seed, and targeted-only fine-tuning.
- Added scripts/05_analyze_eval.py to produce reproducible evaluation tables and failure coordinate plots.
- Documented the failure analysis and proposed targeted + replay mixed data strategy.

## Team / 团队分工

- Team name: Chen Weiliang / 陈伟亮
- Member: Chen Weiliang / 陈伟亮
- Contribution: environment setup, data generation, model training, closed-loop evaluation, failure analysis, README, and demo-video planning.

## Installation and Running / 安装与运行

These commands assume the official AMD cloud image or an equivalent ROCm environment.

1. Prepare environment:

    sudo apt-get update
    sudo apt-get install -y openssh-server ffmpeg
    sudo service ssh start
    source /workspace/rdna/bin/activate
    cd /workspace/Robot_synthetic_data_generation_workshop
    export HF_HUB_OFFLINE=1
    export TRANSFORMERS_OFFLINE=1

2. Generate data:

    python scripts/02_gen_data_custom_scene.py \
      --scene rustic_kitchen \
      --anchor floor_origin \
      --camera-layout up_wrist \
      --n-episodes 100 \
      --seed 42 \
      --repo-id local/franka-kitchen-wrist-100ep

3. Train baseline model:

    python scripts/02_train_vla.py \
      --dataset-id local/franka-kitchen-wrist-100ep \
      --pretrained /workspace/models/smolvla_base \
      --n-steps 4000 \
      --batch-size 4 \
      --num-workers 4 \
      --save-every 0 \
      --run-name smolvla_kitchen_wrist

4. Evaluate current best checkpoint:

    python scripts/03_eval.py \
      --policy-type smolvla \
      --checkpoint output/train/smolvla_kitchen_wrist/final \
      --dataset-id local/franka-kitchen-wrist-100ep \
      --task=Pick\ up\ the\ cube. \
      --camera-layout up_wrist \
      --n-episodes 20 \
      --seed 99 \
      --record-video \
      --run-name kitchen_eval_prompt_cube

5. Reproduce analysis:

    python scripts/05_analyze_eval.py \
      --eval analysis/raw_eval/baseline_4000_prompt_red_seed99.json analysis/raw_eval/baseline_4000_prompt_cube_seed99.json analysis/raw_eval/baseline_8000_prompt_cube_seed99.json analysis/raw_eval/baseline_4000_prompt_cube_seed123.json analysis/raw_eval/targeted_4000_prompt_cube_seed99.json \
      --label baseline_4000_prompt_red_seed99 baseline_4000_prompt_cube_seed99 baseline_8000_prompt_cube_seed99 baseline_4000_prompt_cube_seed123 targeted_4000_prompt_cube_seed99 \
      --out-dir analysis

## Reproducible Extension Experiments

The following commands implement the remaining high-value experiments. All
models should use the same episode manifest so that camera and training
comparisons are paired rather than based on different random placements.

1. Create a 50-episode evaluation manifest:

       python scripts/07_make_eval_manifest.py \
         --n-episodes 50 \
         --seed 99 \
         --out analysis/eval_manifest_seed99_50.json

2. Run the camera ablation on the custom kitchen scene:

       for mode in both overhead_only wrist_only; do
         python scripts/04_eval_custom_scene.py \
           --policy-type smolvla \
           --checkpoint output/train/smolvla_kitchen_wrist/final \
           --dataset-id local/franka-kitchen-wrist-100ep \
           --task="Pick up the cube." \
           --scene rustic_kitchen \
           --anchor floor_origin \
           --camera-layout up_wrist \
           --camera-ablation "$mode" \
           --episode-manifest analysis/eval_manifest_seed99_50.json \
           --n-episodes 50 \
           --seed 99 \
           --run-name "camera_ablation_${mode}"
       done

`both` is the two-camera control. `overhead_only` and `wrist_only` keep the
LeRobot input schema unchanged and replace the unused camera with neutral
pixels, so the comparison isolates visual information rather than changing
the model architecture.

3. Generate a domain-randomized training dataset:

       python scripts/02_gen_data_custom_scene.py \
         --scene rustic_kitchen \
         --anchor floor_origin \
         --camera-layout up_wrist \
         --n-episodes 100 \
         --seed 42 \
         --domain-randomization \
         --repo-id local/franka-kitchen-wrist-dr-100ep

The current reproducible profile randomizes per-episode brightness in
`[0.85, 1.15]` and adds RGB Gaussian sensor noise with standard deviation 4.
The nominal dataset path remains unchanged when `--domain-randomization` is
omitted.

4. Validate source datasets and build mixed replay:

       python scripts/08_validate_dataset.py \
         --dataset-id local/franka-kitchen-wrist-100ep \
         --output output/data/validation_baseline.json

       python scripts/08_validate_dataset.py \
         --dataset-id local/franka-kitchen-wrist-targeted \
         --output output/data/validation_targeted.json

       python scripts/07_make_targeted_manifest.py \
         --eval analysis/raw_eval/baseline_4000_prompt_cube_seed99.json \
         --n-episodes 40 \
         --seed 2026 \
         --out analysis/targeted_manifest_from_failures.json

       python scripts/02_gen_data_custom_scene.py \
         --scene rustic_kitchen \
         --anchor floor_origin \
         --camera-layout up_wrist \
         --n-episodes 40 \
         --seed 2026 \
         --cube-placement-manifest analysis/targeted_manifest_from_failures.json \
         --repo-id local/franka-kitchen-wrist-targeted-v2

       python scripts/06_make_mixed_dataset.py \
         --original-id local/franka-kitchen-wrist-100ep \
         --targeted-id local/franka-kitchen-wrist-targeted-v2 \
         --output-id local/franka-kitchen-wrist-mixed-replay \
         --original-per-targeted 2

The mixed-dataset tool copies complete episodes, checks camera/state/action
schema equality, recomputes statistics, and writes
`output/data/mixed_replay/mix_summary.json`.

5. Train a conservative mixed-replay candidate and keep TensorBoard logs:

       python scripts/02_train_vla.py \
         --dataset-id local/franka-kitchen-wrist-mixed-replay \
         --pretrained /workspace/models/smolvla_base \
         --n-steps 2000 \
         --lr 0.00005 \
         --batch-size 4 \
         --num-workers 4 \
         --run-name smolvla_kitchen_mixed_replay

       tensorboard --logdir output/train/smolvla_kitchen_mixed_replay/tensorboard

The learning rate and step count above are an explicit candidate experiment,
not values stated by the tutorial. They should be accepted or rejected by
closed-loop success, not by training loss alone.

6. Evaluate the candidate on the paired manifest with nominal and perturbed
   observations:

       python scripts/04_eval_custom_scene.py \
         --policy-type smolvla \
         --checkpoint output/train/smolvla_kitchen_mixed_replay/final \
         --dataset-id local/franka-kitchen-wrist-mixed-replay \
         --task="Pick up the cube." \
         --scene rustic_kitchen \
         --anchor floor_origin \
         --camera-layout up_wrist \
         --episode-manifest analysis/eval_manifest_seed99_50.json \
         --n-episodes 50 \
         --seed 99 \
         --run-name mixed_replay_nominal

       python scripts/04_eval_custom_scene.py \
         --policy-type smolvla \
         --checkpoint output/train/smolvla_kitchen_mixed_replay/final \
         --dataset-id local/franka-kitchen-wrist-mixed-replay \
         --task="Pick up the cube." \
         --scene rustic_kitchen \
         --anchor floor_origin \
         --camera-layout up_wrist \
         --domain-randomization \
         --episode-manifest analysis/eval_manifest_seed99_50.json \
         --n-episodes 50 \
         --seed 99 \
         --run-name mixed_replay_perturbed

The separate nominal and perturbed runs make the effect of visual
randomization visible. Cube friction remains an independent evaluation
parameter through `--cube-friction`.

## Submission Evidence

- Technical report: `submission/TECHNICAL_REPORT.md`
- Sim-to-real risk analysis: `docs/sim_to_real.md`
- Training metrics: `output/train/<run-name>/train_metrics.json`
- Training summary: `output/train/<run-name>/train_summary.json`
- TensorBoard events: `output/train/<run-name>/tensorboard/`
- Evaluation comparison: `analysis/eval_comparison.md`
- Aggregate evaluation summary with Wilson intervals: `analysis/eval_summary.json`
- Failure plot: `analysis/failure_coordinate_scatter.svg`

## Demo Video / 演示视频

- Public video URL: TBD after YouTube or Bilibili upload.
- Local preview: demo/radeon_kitchen_smolvla_demo_preview.mp4 if copied from the workspace root.
- Final local render: videos/radeon_kitchen_smolvla_final_demo.mp4 (100 seconds, 1080p).
- Script: videos/demo_script.md
- Submission target: public 1080p+ video, no longer than 3 minutes.
- Required structure: problem, demo, method, metrics, limitations, next steps.
- Final frame should show the GitHub URL and team name.
- Final submission checklist: submission/SUBMISSION_CHECKLIST.md

## Limitations and Next Improvements / 局限与下一步

- The current best model is not robust across seeds yet.
- Evaluation should be expanded to 50+ episodes and multiple seeds.
- Targeted data should be mixed with replay data to avoid distribution shift.
- Domain randomization should cover lighting, textures, cube color and size, camera noise, friction, occlusion, and background clutter.
- A real-robot transfer plan should account for camera calibration, latency, contact friction, and actuator limits.

## License

This project code is released under the MIT License. Third-party datasets, models, and dependencies retain their original licenses.
