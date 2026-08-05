# Sim-to-Real Risk Analysis

This project is evaluated in Genesis, so the reported success rate is a
simulation result rather than a claim of real-robot performance. The following
risks are the main transfer gaps that would need to be measured and calibrated
before deploying the policy on a physical Franka arm.

## Visual Gap

- Camera intrinsics, exposure, white balance, lens distortion, and mounting
  height will differ from the rasterized Genesis cameras.
- Kitchen textures and object colors may be more varied in the real workspace.
- The wrist camera can be partially occluded by the gripper, cable, or the
  object itself.
- Image timing and transport latency can change the apparent object position.

The current mitigation is reproducible brightness scaling and pixel noise
during data generation and evaluation. This is intentionally a small,
controlled augmentation rather than a claim that the full visual gap has been
solved.

## Contact and Dynamics Gap

- Real friction, restitution, contact compliance, and gripper pad deformation
  are not identical to Genesis parameters.
- The cube may slide, rotate, or rebound differently during approach and
  closure.
- Robot joint backlash, gravity calibration, torque limits, and controller
  bandwidth affect the executed action.

The evaluation already exposes cube friction as an independent parameter. A
future calibrated sweep should report success over a friction interval instead
of using one nominal value.

## Control and Timing Gap

- The policy predicts action chunks, while the real robot executes through a
  lower-level controller with its own interpolation and delay.
- Observation-to-action latency can compound across closed-loop replanning.
- Safety limits may clip actions that are valid in simulation.

Before a hardware trial, the action rate, chunk horizon, smoothing limit,
joint limits, and emergency stop behavior should be matched to the real
controller. The first transfer test should use a low-height, low-speed
workspace and a soft object or guarded fixture.

## Calibration Plan

1. Measure the real camera intrinsics and extrinsics, then reproduce the
   camera pose in Genesis.
2. Calibrate the robot home pose and the table height in the same robot-local
   coordinate frame used by the dataset.
3. Identify cube mass, friction, and gripper contact behavior from short
   scripted trajectories.
4. Replay the same fixed placement manifest in simulation and on hardware.
5. Compare approach error, grasp closure, lift height, and release behavior.
6. Increase placement range and speed only after the guarded test is stable.

## What This Submission Claims

The defensible claim is: the pipeline demonstrates a reproducible,
closed-loop Genesis benchmark running on AMD ROCm, with explicit failure
analysis and documented transfer risks. It does not claim that a real Franka
will achieve the same success rate without calibration.
