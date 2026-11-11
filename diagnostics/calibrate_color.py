from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from skimage import color, measure, morphology

from colorcard import COLORCHECKER_SRGB


SCREENSHOT = Path(__file__).parent / "screenshots" / "alvr_colorcard_standard.png"


def srgb_to_linear(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64) / 255.0
    return np.where(
        values <= 0.04045,
        values / 12.92,
        ((values + 0.055) / 1.055) ** 2.4,
    )


def load_samples() -> tuple[np.ndarray, np.ndarray]:
    image = np.asarray(Image.open(SCREENSHOT).convert("RGB"))
    image = image[:, : image.shape[1] // 2]

    bright_mask = morphology.remove_small_objects(
        color.rgb2gray(image) > 20 / 255,
        min_size=15000,
    )
    bright_regions = [
        region
        for region in measure.regionprops(
            measure.label(bright_mask),
            intensity_image=image,
        )
        if region.centroid[0] < 1500
    ]

    dark_mask = morphology.remove_small_objects(
        color.rgb2gray(image) > 16 / 255,
        min_size=15000,
    )
    dark_regions = measure.regionprops(
        measure.label(dark_mask),
        intensity_image=image,
    )
    purple_region = [
        region
        for region in dark_regions
        if 580 < region.centroid[0] < 630
        and 1420 < region.centroid[1] < 1490
    ][0]

    regions = bright_regions + [purple_region]
    if len(regions) != 24:
        raise RuntimeError(f"Expected 24 color patches, found {len(regions)}")

    samples = []
    for region in regions:
        interior = morphology.binary_erosion(region.image, morphology.disk(6))
        samples.append(np.median(image[region.slice][interior], axis=0))

    # Mapping from detected-region index to reference-card index. The card is
    # rotated in the screenshot, so this order cannot be inferred from y/x alone.
    mapping = {
        16: 18,
        9: 12,
        4: 6,
        0: 0,
        18: 19,
        11: 13,
        5: 7,
        1: 1,
        20: 20,
        13: 14,
        7: 8,
        2: 2,
        21: 21,
        14: 15,
        23: 9,
        3: 3,
        22: 22,
        15: 16,
        10: 10,
        6: 4,
        19: 23,
        17: 17,
        12: 11,
        8: 5,
    }
    if set(mapping) != set(range(24)):
        raise RuntimeError("Sample mapping does not cover all 24 patches")

    ordered_samples = np.empty_like(np.asarray(samples))
    for sample_index, reference_index in mapping.items():
        ordered_samples[reference_index] = samples[sample_index]

    references = np.asarray(COLORCHECKER_SRGB, dtype=np.float64)
    return ordered_samples, references


def fit_color_correction(
    samples: np.ndarray,
    references: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sample_linear = srgb_to_linear(samples)
    reference_linear = srgb_to_linear(references)

    # The headset approximately applies a square to linear RGB. Invert that
    # first, then fit the remaining channel cross-talk.
    inverse_display = np.linalg.lstsq(
        np.sqrt(sample_linear),
        reference_linear,
        rcond=None,
    )[0].T

    # The shader applies the matrix before gamma. Fit the matrix that makes
    # sqrt(matrix @ source) approximate inverse_display @ sqrt(source).
    target_before_gamma = inverse_display @ np.sqrt(reference_linear).T
    matrix = np.linalg.lstsq(
        reference_linear,
        (target_before_gamma**2).T,
        rcond=None,
    )[0].T

    return inverse_display, matrix, reference_linear


def print_matrix(name: str, matrix: np.ndarray) -> None:
    print(name)
    for row in matrix:
        print(" ".join(f"{value: .8f}" for value in row))


def main() -> None:
    samples, references = load_samples()
    inverse_display, matrix, reference_linear = fit_color_correction(
        samples,
        references,
    )

    print_matrix("Inverse display matrix", inverse_display)
    print_matrix("Shader color matrix", matrix)

    display = np.linalg.inv(inverse_display)
    corrected = np.sqrt(np.clip(matrix @ reference_linear.T, 0, 1))
    final = np.power(np.clip(display @ corrected, 0, None), 2).T
    residual = final - reference_linear
    print(f"Simulation RMSE: {np.sqrt(np.mean(residual**2)):.8f}")
    print(f"Simulation max abs residual: {np.abs(residual).max():.8f}")


if __name__ == "__main__":
    main()
