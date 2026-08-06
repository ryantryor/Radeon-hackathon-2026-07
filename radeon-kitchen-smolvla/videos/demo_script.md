# Demo Video Script

Target duration: 2 minutes 50 seconds (must be no longer than 3 minutes).

## 0:00-0:15 - Task

Show a successful pick from the current best seed-99 evaluation, followed by
the rustic kitchen scene and several cube placements.

Narration:

> This project studies a vision-language-action policy for a Franka Panda
> robot. The task is simple to describe: pick up the cube. The challenge is
> making the action remain stable when the policy observes its own mistakes in
> a closed loop.

## 0:15-0:45 - Pipeline

Show the command line, Genesis expert data generation, and the two camera
streams.

Narration:

> We generate scripted expert trajectories in Genesis, store synchronized
> state, action, image, and task fields in LeRobot format, fine-tune SmolVLA
> on an AMD Radeon ROCm environment, and evaluate the learned policy back in
> the same simulated kitchen.

On-screen labels:

- Genesis expert data
- LeRobot dataset
- SmolVLA fine-tuning
- Closed-loop Genesis evaluation

## 0:45-1:20 - Technical Evidence

Show the training log, TensorBoard event directory, and
`analysis/failure_coordinate_scatter.svg`.

Narration:

> The primary metric is closed-loop success, not imitation loss. We ran
> controlled comparisons for prompt wording, effective training steps, a
> second evaluation seed, and targeted-only fine-tuning. The failure plot
> records where the cube was placed and whether the policy completed a
> sustained lift.

## 1:20-1:55 - Results

Show one success video, one failure video, and the experiment table.

Narration:

> The current fallback checkpoint is the original 4,000-step fine-tune. With
> the dataset-aligned instruction, it succeeded in 11 of 20 seed-99 episodes,
> or 55 percent. A prompt mismatch scored 35 percent. Continuing to an
> effective 8,000 steps scored 40 percent, while targeted-only fine-tuning
> scored 5 percent. The same baseline also scored 5 percent on seed 123, so
> robustness remains an open problem.

## 1:55-2:25 - Failure-aware robustness experiments

Show the fixed manifest, the three camera-ablation labels, the mixed replay
command, and the robustness envelope output.

Narration:

> The next experiments isolate causes instead of hiding variance. We generate
> targeted placements from observed failure coordinates, mix them with broad
> replay data at two to one, and evaluate the same placement manifest under
> full-view, overhead-only, wrist-only, camera dropout, occlusion, timing
> delay, and friction changes. The paired camera study gives 42 percent with
> both views, 10 percent with only overhead, and 2 percent with only the wrist
> camera. The mixed replay candidate scored 20 percent on the same 50
> placements, so we keep the original baseline instead of hiding a negative
> result.

## 2:25-2:42 - Sim-to-Real envelope

Show `robustness_envelope.svg`, then `docs/sim_to_real.md`.

Narration:

> The envelope reports stressed success divided by nominal success. It makes
> the transfer boundary visible: nominal performance is 50 percent, camera
> dropout and local occlusion fall to 20 percent, and action delay or low
> friction reach 40 percent. These are still simulation results. Real transfer
> requires camera calibration, contact
> identification, controller latency matching, and guarded low-speed tests.

## 2:42-2:55 - Closing

Show the repository URL, team name, and artifact paths.

Narration:

> The deliverable is a reproducible AMD ROCm workflow from synthetic expert
> data to closed-loop VLA evaluation, with negative controls, failure-aware
> data replay, a measured robustness envelope, and a concrete path toward
> real-robot calibration.

Final frame:

- GitHub: `https://github.com/ryantryor/Radeon-hackathon-2026-07/tree/main/radeon-kitchen-smolvla`
- Team: Chen Weiliang
- Track: Physical AI Challenge

## Editing Checklist

- Open with a real successful pick.
- Include both overhead and wrist views.
- Include at least one failure clip.
- Show the current metrics without hiding the seed-123 result.
- Show the failure coordinate plot.
- Show the fixed-manifest and mixed-replay commands.
- Keep the final video at or below 3 minutes.
- Show nominal and stressed success as separate numbers; never label a planned
  experiment as a completed result.
- Add Chinese subtitles during editing if a bilingual cut is required.
