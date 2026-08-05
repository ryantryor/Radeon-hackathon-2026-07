"""Small, dependency-light helpers for reproducible visual perturbations."""
from __future__ import annotations

import numpy as np


def resolve_domain_randomization(
    enabled: bool,
    image_noise_std: float,
    brightness_range: tuple[float, float] | None,
) -> tuple[float, tuple[float, float] | None]:
    """Resolve CLI defaults while keeping the legacy no-augmentation path."""
    if enabled:
        if image_noise_std == 0.0:
            image_noise_std = 4.0
        if brightness_range is None:
            brightness_range = (0.85, 1.15)
    if image_noise_std < 0.0:
        raise ValueError("image noise standard deviation must be non-negative")
    if brightness_range is not None:
        lo, hi = brightness_range
        if lo <= 0.0 or lo >= hi:
            raise ValueError("brightness range must satisfy 0 < min < max")
        brightness_range = (float(lo), float(hi))
    return float(image_noise_std), brightness_range


def augment_image(
    image: np.ndarray,
    rng: np.random.Generator,
    noise_std: float = 0.0,
    brightness: float = 1.0,
) -> np.ndarray:
    """Apply deterministic illumination and sensor-noise perturbations."""
    arr = image.astype(np.float32) * float(brightness)
    if noise_std > 0.0:
        arr += rng.normal(0.0, noise_std, size=arr.shape)
    return np.clip(arr, 0.0, 255.0).astype(np.uint8)


def ablate_camera(
    image: np.ndarray,
    camera: str,
    ablation: str,
    fill_value: float = 127.5,
) -> np.ndarray:
    """Replace the camera that is not part of an ablation with neutral pixels."""
    if ablation not in ("both", "overhead_only", "wrist_only"):
        raise ValueError(f"unknown camera ablation: {ablation}")
    keep = (
        ablation == "both"
        or (ablation == "overhead_only" and camera == "overhead")
        or (ablation == "wrist_only" and camera == "wrist")
    )
    if keep:
        return image
    value = np.uint8(np.clip(round(fill_value), 0, 255))
    return np.full_like(image, value)
