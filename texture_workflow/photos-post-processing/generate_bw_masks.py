#!/usr/bin/env python3
"""
Generate black-white mask preview images from json annotations.

Default convention:
- image: xxx.jpg / xxx.png / ...
- mask json: xxx.json (same stem as image)

Output:
- grayscale PNG mask where white=foreground, black=background
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
from PIL import Image, ImageDraw

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate black-white masks from image/json pairs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Folder containing images and corresponding json files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output folder. Default: <input-dir>/bw_masks",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search images recursively.",
    )
    parser.add_argument(
        "--labels",
        type=str,
        default=None,
        help="Comma-separated labels to keep, e.g. person,car.",
    )
    parser.add_argument(
        "--invert-mask",
        action="store_true",
        help="Invert output mask (white background, black object).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Stop immediately on malformed json instead of skipping.",
    )
    return parser.parse_args()


def iter_images(input_dir: Path, recursive: bool) -> Iterable[Path]:
    if recursive:
        for p in input_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                yield p
    else:
        for p in input_dir.iterdir():
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                yield p


def _draw_polygon_mask(
    data: dict,
    size: tuple[int, int],
    keep_labels: Optional[set[str]] = None,
) -> Optional[np.ndarray]:
    width, height = size
    mask_img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask_img)

    # LabelMe-style format: data["shapes"] with polygon points.
    if isinstance(data.get("shapes"), list):
        drawn = 0
        for shape in data["shapes"]:
            label = str(shape.get("label", "")).strip()
            if keep_labels and label not in keep_labels:
                continue

            pts = shape.get("points")
            if not isinstance(pts, list) or len(pts) < 3:
                continue

            polygon = []
            for pt in pts:
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    polygon.append((float(pt[0]), float(pt[1])))

            if len(polygon) >= 3:
                draw.polygon(polygon, fill=255)
                drawn += 1

        if drawn > 0:
            return np.array(mask_img, dtype=np.uint8)

    # Generic format: data["objects"] with points/polygon.
    if isinstance(data.get("objects"), list):
        drawn = 0
        for obj in data["objects"]:
            label = str(obj.get("label", "")).strip()
            if keep_labels and label not in keep_labels:
                continue

            pts = obj.get("points") or obj.get("polygon")
            if not isinstance(pts, list) or len(pts) < 3:
                continue

            polygon = []
            for pt in pts:
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    polygon.append((float(pt[0]), float(pt[1])))

            if len(polygon) >= 3:
                draw.polygon(polygon, fill=255)
                drawn += 1

        if drawn > 0:
            return np.array(mask_img, dtype=np.uint8)

    return None


def _array_mask_from_json(data: dict, size: tuple[int, int]) -> Optional[np.ndarray]:
    width, height = size
    raw = data.get("mask")
    if raw is None:
        return None

    arr = np.array(raw)
    if arr.ndim != 2:
        return None
    if arr.shape != (height, width):
        return None

    return np.where(arr > 0, 255, 0).astype(np.uint8)


def build_mask(
    json_path: Path,
    image_size: tuple[int, int],
    keep_labels: Optional[set[str]],
    invert: bool,
) -> np.ndarray:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    mask = _draw_polygon_mask(data, image_size, keep_labels=keep_labels)
    if mask is None:
        mask = _array_mask_from_json(data, image_size)

    if mask is None:
        raise ValueError("No supported mask structure found in json")

    if invert:
        mask = 255 - mask

    return mask


def save_bw_mask(mask: np.ndarray, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask, mode="L").save(out_path)


def main() -> None:
    args = parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir or (input_dir / "bw_masks")
    keep_labels = None
    if args.labels:
        keep_labels = {s.strip() for s in args.labels.split(",") if s.strip()}

    if not input_dir.exists() or not input_dir.is_dir():
        raise NotADirectoryError(f"Input dir not found: {input_dir}")

    images = sorted(iter_images(input_dir, recursive=args.recursive))
    if not images:
        print("No images found.")
        return

    ok_count = 0
    skip_count = 0

    for img_path in images:
        json_path = img_path.with_suffix(".json")
        if not json_path.exists():
            print(f"[SKIP] no json: {img_path.name}")
            skip_count += 1
            continue

        try:
            with Image.open(img_path) as img:
                width, height = img.size

            mask = build_mask(
                json_path=json_path,
                image_size=(width, height),
                keep_labels=keep_labels,
                invert=args.invert_mask,
            )

            rel = img_path.relative_to(input_dir)
            out_name = rel.with_suffix("").as_posix() + "_mask.png"
            out_path = output_dir / out_name
            save_bw_mask(mask, out_path)

            print(f"[OK]   {img_path.name} -> {out_path}")
            ok_count += 1
        except Exception as e:  # noqa: BLE001
            if args.strict:
                raise
            print(f"[SKIP] {img_path.name}: {e}")
            skip_count += 1

    print(f"Done. success={ok_count}, skipped={skip_count}, output={output_dir}")


if __name__ == "__main__":
    main()
