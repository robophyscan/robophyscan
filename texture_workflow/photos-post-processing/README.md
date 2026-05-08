# photos-post-processing

A collection of small scripts for batch-processing annotated images:

- generate black-and-white mask preview images from matching `*.json` annotations
- remove backgrounds using annotation masks and export transparent PNGs
- make black pixels transparent in a single image

## Environment and Installation

- Python >= 3.9

Install dependencies:

```bash
pip install -r requirements.txt
```

## Input File Conventions

By default, files are matched by the same base name:

- image: `xxx.jpg` / `xxx.png` / ...
- annotation: `xxx.json` (same file name as the image, different extension)

Supported annotation formats (the script automatically detects one of them):

- LabelMe-style: `{"shapes": [{"label": "...", "points": [[x,y], ...]}]}`
- Generic object list: `{"objects": [{"label": "...", "points": [[x,y], ...]}]}` or `{"objects": [{"polygon": [[x,y], ...]}]}`
- Direct array mask: `{"mask": [[0,1,1,...], ...]}` (must match the image size; non-zero values are treated as foreground)

## Scripts

### 1) Generate black-and-white mask previews

File: [generate_bw_masks.py](file:///g:/university/innovation/scan/zhang-repo/texture_workflow/photos-post-processing/generate_bw_masks.py)

Converts annotations into grayscale PNG masks, where white is foreground and black is background.

```bash
python generate_bw_masks.py --input-dir path/to/data
```

Common options:

- `--output-dir`: output directory (default: `<input-dir>/bw_masks`)
- `--recursive`: search images recursively
- `--labels person,car`: keep only polygons with the specified labels
- `--invert-mask`: invert the output mask
- `--strict`: exit immediately on invalid JSON instead of skipping it

Output naming:

- keeps the same relative path under the input directory and appends `_mask.png` to the file name

### 2) Remove background using annotations (export transparent PNG)

File: [remove_background.py](file:///g:/university/innovation/scan/zhang-repo/texture_workflow/photos-post-processing/remove_background.py)

Generates a mask from the JSON annotation, converts the image to RGBA, uses the mask as the alpha channel, and exports a transparent-background PNG.

```bash
python remove_background.py --input-dir path/to/data
```

Common options:

- `--output-dir`: output directory (default: `<input-dir>/no_bg`)
- `--recursive`: search images recursively
- `--labels person,car`: keep only polygons with the specified labels
- `--invert-mask`: invert the mask if the JSON marks background instead of foreground
- `--strict`: exit immediately on invalid JSON instead of skipping it

Output naming:

- keeps the same relative path under the input directory and appends `_nobg.png` to the file name

### 3) Remove black from a single image (make black pixels transparent)

File: [remove_black_pixels.py](file:///g:/university/innovation/scan/zhang-repo/texture_workflow/photos-post-processing/remove_black_pixels.py)

Treats pixels with `R,G,B <= threshold` as black and sets their alpha value to `0`.

```bash
python remove_black_pixels.py --input path/to/image.jpg
```

Common options:

- `--output`: output PNG path (default: `<input_stem>_no_black.png`)
- `--threshold`: threshold value (default: `0`, only pure black; for example, `10` is more aggressive)

## FAQ

- Why are some images marked as `[SKIP]`?
  - Usually because the matching `*.json` file is missing, the JSON does not contain a recognizable mask structure, or the polygon has too few points.
- Why does the mask array size not match?
  - The 2D array in `{"mask": ...}` must be `(height, width)` and must match the image dimensions exactly.
