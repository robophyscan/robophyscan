# RealityScan Texturing Workflow Automation Script

This is a Python-based automation script designed to call `RealityScan.exe` from the command line and fully automate workflows such as 3D reconstruction, texture generation, model export, and texture reprojection.

## Requirements

- **Python Version**: Python 3.10 or later
- **Operating System**: Windows
- **Required Software**: A RealityScan installation that includes `RealityScan.exe`

## Core Features

1. **Environment Check (`env_check`)**: Automatically checks whether `RealityScan.exe` exists in the environment variables. If it is not found, the script can prompt for the path at runtime and temporarily add it.
2. **Fully Automated Texture Generation (`generate_workflow`)**: Starts from an input photo folder and automatically completes photo alignment, reconstruction region setup, normal calculation, model cleanup, UV unwrapping, texture calculation, and project saving.
3. **Model Export (`export_compare_mesh_workflow`)**: Automatically loads an existing project and exports a specified model file such as `.obj` for external mesh comparison or editing.
4. **Texture Reprojection (`reproject_texture_workflow`)**: Reprojects texture from the source model in the project onto an externally imported mesh and exports the new textured model.

## Quick Start

Place `function.py` in your working directory, then import and call the workflow functions you need from other Python scripts.

### 1. Basic environment setup

Before running any workflow, it is recommended to run the environment check first to make sure the program can locate `RealityScan.exe`:

```python
from function import env_check

# Check the environment variable. If the executable is not found,
# the script will prompt for the path automatically.
env_check()
```

### 2. Generate a texturing workflow

Generate a 3D model and textures directly from a photo folder, then save the result as a project file:

```python
from function import generate_workflow

generate_workflow(
    input_photo_dir=r"C:\path\to\your\photos",  # Input photo directory
    project_dir=r"C:\path\to\save\project",     # Project output path without extension
    headless_bool=True,                         # Run silently in the background
    quit_bool=True                              # Close RealityScan when finished
)
```

### 3. Export a model

Load an existing project file and export a specified model. By default, the exported model name is `"Model 3"`:

```python
from function import export_compare_mesh_workflow

export_compare_mesh_workflow(
    project_dir=r"C:\path\to\save\project",          # Project path without extension
    export_compare_mesh_dir=r"C:\path\to\export",    # Model export directory
    compare_mesh="my_exported_model",                # Exported file name
    model_name="Model 3"                             # Model name to export in RealityScan
)
```

### 4. Texture reprojection workflow

Import an externally edited mesh with updated topology, reproject the texture from the original high-poly model onto it, and then export the result:

```python
from function import reproject_texture_workflow

reproject_texture_workflow(
    project_dir=r"C:\path\to\save\project",
    to_be_reprojected_mesh_dir=r"C:\path\to\import", # Directory containing the mesh to reproject
    reprojected_mesh_dir=r"C:\path\to\export",       # Final output directory
    to_be_reprojected_mesh="my_clean_mesh",          # Imported mesh file name
    reprojected_mesh="my_final_textured_mesh",       # Exported file name
    reprojection_model="Model 3",                    # Source model that provides the texture
    to_be_reprojected_model="Model 4"                # Model name after import in RealityScan
)
```

## Notes

1. **Path Format**: On Windows, it is recommended to use raw strings such as `r"C:\folder\path"` for paths to avoid escape-character issues.
2. **Headless Mode**: All workflows use `headless_bool=True` by default. If you want to monitor progress through the UI while running, set it to `False`.
3. **File Extensions**: The script automatically handles the `.rsproj` project extension and the `.obj` model extension, so you do not need to include them in the input arguments.
