#!/usr/bin/env python3
"""
Remove black pixels from a single image by making them transparent.

Example:
    python remove_black_pixels.py --input image.jpg
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove black pixels from one image and export transparent PNG."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input image path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output PNG path. Default: <input_stem>_no_black.png",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=0,
        help="Treat pixels with R,G,B <= threshold as black. Default: 0 (pure black only).",
    )
    return parser.parse_args()


def remove_black(input_path: Path, output_path: Path, threshold: int) -> None:
    if threshold < 0 or threshold > 255:
        raise ValueError("threshold must be between 0 and 255")

    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)

    rgb = arr[:, :, :3]
    black_mask = (
        (rgb[:, :, 0] <= threshold)
        & (rgb[:, :, 1] <= threshold)
        & (rgb[:, :, 2] <= threshold)
    )

    # Set alpha=0 for black pixels, keep others unchanged.
    arr[black_mask, 3] = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr, mode="RGBA").save(output_path)

    removed = int(np.count_nonzero(black_mask))
    total = int(black_mask.size)
    print(f"Done. removed={removed}, total={total}, output={output_path}")


def main() -> None:
    args = parse_args()

    input_path = args.input
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    output_path = args.output
    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_no_black.png")

    remove_black(
        input_path=input_path, output_path=output_path, threshold=args.threshold
    )


if __name__ == "__main__":
    main()
