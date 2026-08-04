# Radeon Kitchen Pick with SmolVLA

> Submission for AMD AI DevMaster Hackathon 2026, Physical AI track.
> Team: Chen Weiliang

Project repository: https://github.com/ryantryor/Radeon-hackathon-2026-07/tree/main/radeon-kitchen-smolvla

## Project Summary

This project teaches a vision-language-action policy to pick up a cube in a randomized rustic-kitchen simulation. We generate expert demonstrations with Genesis on an AMD Radeon GPU, store them in the LeRobot format, fine-tune SmolVLA, and evaluate the policy in a closed loop.

The pipeline is:

`Genesis expert data -> LeRobot dataset -> SmolVLA fine-tuning -> Genesis closed-loop evaluation`

Key result on the same 20 evaluation episodes, scene, camera layout, and seed:

| Condition | Success |
|---|---:|
| 4,000-step checkpoint, mismatched prompt | 7/20 = 35% |
| 4,000-step checkpoint, dataset-aligned prompt | **11/20 = 55%** |
| Effective 8,000-step checkpoint, dataset-aligned prompt | 8/20 = 40% |

The aligned-prompt 4,000-step model is the current best checkpoint. The prompt comparison is an important finding: language conditioning is part of the policy interface, not just presentation text. The 8,000-step control also shows that more optimization steps do not automatically improve closed-loop behavior under a small dataset and a fixed evaluation sample.

## 项目简介

本项目在 AMD Radeon GPU 上使用 Genesis 生成专家抓取数据，再用 LeRobot 数据格式微调 SmolVLA，最后在带有随机方块位置的 rustic kitchen 场景中进行闭环评估。任务是让 Franka 机械臂根据相机图像和语言指令抓取方块。

核心链路是：

`Genesis 专家数据 -> LeRobot 数据集 -> SmolVLA 微调 -> Genesis 闭环评估`

我们生成了 100 个 episode、13,500 帧、30 FPS 的双相机数据集，使用 `up` 和 wrist-mounted 相机。当前最佳结果是 4,000 步模型配合训练数据一致的指令，在固定 20 集评估中成功 11 集，即 55%。

## Development Process / 开发过程

### 1. Environment

- GPU: AMD Radeon GPU with ROCm 7.2.1
- PyTorch: 2.9.1+rocm7.2.1
- Genesis: 1.3.1
- LeRobot: 0.4.4
- Transformers: 4.57.6
- Policy: SmolVLA, 450M total parameters, about 100M trainable parameters

### 2. Synthetic data

We use `scripts/02_gen_data_custom_scene.py` to generate a randomized cube-pick dataset in the rustic kitchen scene. Expert actions are produced by the scripted controller, while the dataset records images, robot state, action, task text, and episode metadata.

Dataset facts:

- Repository id: `local/franka-kitchen-wrist-100ep`
- Episodes: 100
- Frames: 13,500
- Cameras: overhead `up` plus eye-in-hand `wrist`
- Generation success: 100/100

### 3. Training

The 4,000-step run starts from the local SmolVLA base checkpoint. The effective 8,000-step control continues from the 4,000-step checkpoint for another 4,000 steps. Training loss decreases substantially, but closed-loop success is the metric that matters for the physical task.

### 4. Evaluation and controls

The evaluation uses the same `rustic_kitchen`, `floor_origin`, `up_wrist` camera layout, 20 episodes, and seed 99. We changed one factor at a time:

1. Prompt mismatch versus dataset-aligned prompt.
2. 4,000 effective steps versus 8,000 effective steps.

All results and output paths are recorded in `experiment_log.md`.

### 5. Problems and solutions

- ROCm model loading required a local SmolVLM backbone path.
- AV1/LeRobot video decoding required FFmpeg and a CPU-only TorchCodec build.
- Genesis mesh warnings were handled by using the provided collision mesh and visual mesh separately.
- Windows PowerShell quoting split the natural-language task argument during one evaluation attempt; the final runs use escaped spaces and verify the task text in the log.

### 6. Next improvements

- Increase the number of evaluation episodes and repeat with a second seed to estimate variance.
- Add more cube poses and harder occlusion cases to the demonstrations.
- Compare wrist-only, overhead-only, and two-camera policies.
- Add systematic domain randomization for lighting, textures, camera noise, and object appearance.
- Investigate why imitation loss and closed-loop success can diverge.

## Code Sources and Original Contributions / 代码来源说明

Base source: [AMD-DEV-CONTEST/Robot_synthetic_data_generation_workshop](https://github.com/AMD-DEV-CONTEST/Robot_synthetic_data_generation_workshop) and its workshop dependencies.

Open-source model: [Hugging Face SmolVLA](https://huggingface.co/lerobot/smolvla_base) and the SmolVLM2 backbone. These are used according to their respective licenses; the model weights are not redistributed in this repository.

Our project-specific work:

- Configured and verified the ROCm environment on an AMD Radeon cloud GPU.
- Generated and validated a local 100-episode rustic-kitchen dataset.
- Added local backbone loading for the training and custom-scene evaluation scripts.
- Ran controlled prompt and training-step comparisons.
- Recorded training metrics, evaluation summaries, and per-episode videos.
- Documented reproducible commands and the interpretation of failures.

## Team / 团队分工

- Team: Chen Weiliang
- Member(s): Chen Weiliang
- Contributions: data generation, ROCm environment setup, SmolVLA training, Genesis evaluation, experiment analysis, and submission documentation.

## Installation and Running / 安装与运行

The commands below assume an AMD ROCm environment and the repository root as the working directory.

```bash
python scripts/00_download_kitchen.py --mesh-only

python scripts/02_gen_data_custom_scene.py \
  --scene rustic_kitchen --anchor floor_origin \
  --camera-layout up_wrist --n-episodes 100 --seed 42 \
  --repo-id local/franka-kitchen-wrist-100ep

python scripts/02_train_vla.py \
  --dataset-id local/franka-kitchen-wrist-100ep \
  --pretrained /path/to/models/smolvla_base \
  --n-steps 4000 --batch-size 4 --num-workers 4 \
  --run-name smolvla_kitchen_wrist

python scripts/04_eval_custom_scene.py \
  --checkpoint output/train/smolvla_kitchen_wrist/final \
  --dataset-id local/franka-kitchen-wrist-100ep \
  --task="Pick up the cube." \
  --scene rustic_kitchen --anchor floor_origin \
  --camera-layout up_wrist --n-episodes 20 --seed 99 \
  --record-video
```

The model checkpoint, training summary, evaluation summary, and videos are written under `output/`. Do not upload the generated dataset or the 1.2 GB model weights directly to GitHub. Provide generation commands and an external artifact link when publishing the final submission.

## Demo Video / 演示视频

- Public video URL: `[待上传 YouTube 或 Bilibili 链接]`
- Local video evidence: `output/eval/kitchen_eval_prompt_cube/videos/`
- Suggested structure: 0:00 problem, 0:30 demo, 1:30 technical method, 2:00 metrics, 2:30 limitations and next steps.
- Keep the final video within 3 minutes, use bilingual subtitles, and show the GitHub URL in the final frame.

## License

This project code is released under the MIT License. Third-party components and model weights retain their original licenses.
