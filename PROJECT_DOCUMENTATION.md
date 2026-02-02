# 🚁 Drone Road & Building Segmentation: Technical Master Documentation

> **Version**: 2.0 (Production Ready)  
> **Core Model**: Meta Segment Anything (SAM)  
> **Architecture**: Hybrid (Foundation Model + Heuristic Intelligence)  
> **Platform**: Desktop (PyQt6 / Python)

---

## 1. Project Overview

This project is a high-precision, automated desktop tool designed for analyzing **Aerial Drone Imagery**. It solves the problem of "Mask Fragmentation" common in foundation models by adding a layer of **Geometric Intelligence** on top of SAM.

Instead of just "segmenting anything," this tool:
1.  **Sees** the image using SAM (ViT-H/ViT-B).
2.  **Understands** shape properties (Solidity, Extent, Aspect Ratio).
3.  **Aggregates** fragmented pieces (windows, tiles) into unified real-world objects (Buildings, Roads).

It is optimized for **CPU-safe execution** on standard hardware, automatically handling memory constraints that usually crash SAM on consumer desktops.

---

## 2. File-by-File Technical Breakdown

### 📂 `src/backend.py` (The Brain)
This is the core engine of the application. It handles the AI inference and the post-processing logic.

*   **Class: `SamController`**
    *   `__init__`:
        *   **Smart Loading**: Inspects `weights/` directory. Even if you ask for the huge `vit_h` model, it checks if `vit_b` (Base) is available and recommends/switches to it for speed and memory safety.
        *   **Parameter Tuning**: Initializes `SamAutomaticMaskGenerator` with custom parameters (e.g., `points_per_side=16`) to balance speed vs. accuracy.
    *   `process_image(image_path)`:
        *   **Auto-Resize**: Downscales 4K drone images to 1024px to prevent RAM OOM (Out of Memory) crashes.
        *   **Inference**: Generates raw masks using SAM.
        *   **Pipeline**:
            1.  **Filter**: Removes tiny noise (<0.05% area).
            2.  **Classify**: Runs geometry checks on every mask.
            3.  **Accumulate**: Merges hundreds of Building masks into one "Building Layer".
            4.  **Close Gaps**: Uses `cv2.morphologyEx` to seal windows and holes in roofs.
    *   `classify_mask_geometry(mask, area)`:
        *   Calculates **Solidity** (Area / Convex Hull).
        *   Calculates **Extent** (Rectangularity).
        *   Calculates **Aspect Ratio**.
        *   **Rule**: `Solidity > 0.85 & Extent > 0.6` = 🟥 **Building**.
        *   **Rule**: `Solidity < 0.7 OR Aspect Ratio > 3.5` = 🟨 **Road**.

### 📂 `src/ui.py` (The Face)
A unified, dark-themed GUI built with PyQt6.

*   **Class: `MainWindow`**
    *   **Styling**: Applies a CSS sheet for the Charcoal (`#2b2b2b`) theme.
    *   **Layout**: Enforces a strict center-aligned layout (Title -> Canvas -> Buttons -> Status).
    *   **Logic**:
        *   `lazy_init_backend()`: Prevents the app from freezing on startup by loading the heavy AI model only when needed.
        *   `convert_image()`: Locks the UI, runs the backend in the main thread (for simplicity/stability), and updates the canvas with the result.

### 📂 `src/canvas.py` (The Viewer)
A custom image display widget.

*   **Class: `ImageCanvas`**
    *   Inherits `QLabel`.
    *   **Aspect Ratio Scaling**: Ensures that whether you load a square tile or a panoramic drone shot, it fits perfectly within the GUI without distortion.
    *   **Cleanliness**: Stripped of all interaction logic (drawing/clicking) to strictly follow the "Automated Only" requirement.

### 📂 `main.py` (The Entry Point)
*   **Responsibility**:
    *   initializes the `QApplication`.
    *   Instantiates `MainWindow`.
    *   Starts the event loop.

### 📂 `weights/` (The Muscle)
*   Stores the `.pth` checkpoint files.
*   **Recommended**: `sam_vit_b_01ec64.pth` (375MB) - Best balance for CPU.
*   **Supported**: `sam_vit_h_4b8939.pth` (2.5GB) - Highest accuracy, requires 16GB+ RAM.

---

## 3. Algorithm: "The Reconstruction Pipeline"

The standard SAM output for a building looks like a puzzle: 10 separate masks for windows, 1 for the roof, 4 for the walls. We fixed this using **Spatial Aggregation**:

1.  **Geometric Filtering**: We first ask "Does this puzzle piece *look* like part of a building?" (Is it solid? Is it rectangular?).
2.  **Layer Accumulation**: Instead of drawing boundaries immediately, we throw all "Building-like" pieces onto a blank digital canvas (Accumulator).
3.  **Morphological Closing**: We virtually "smear" the accumulator. If two building pieces are close (like a window and a wall), the smearing connects them.
4.  **Final Extraction**: The connected blob is now identified as **One Building**.

---

## 4. Installation & Requirements

### Dependencies (`requirements.txt`)
*   `segment-anything`: Meta's library.
*   `torch`, `torchvision`: The tensor engine.
*   `opencv-python` (`cv2`): For image resizing and morphological operations.
*   `PyQt6`: For the user interface.

### Setup Guide
1.  **Environment**: `python -m venv env` -> `env/Scripts/activate`
2.  **Install**: `pip install -r requirements.txt`
3.  **Weights**: Place `sam_vit_b_01ec64.pth` in `weights/`.
4.  **Run**: `python main.py`

---

## 5. Future Roadmap

*   **GPU Acceleration**: Adding a toggle to force CUDA if multiple GPUs are detected.
*   **Hybrid Detection**: Replacing the heuristic geometric classifier with a lightweight **YOLOv8** model to detect "Cars" vs "Buildings" before asking SAM to segment them.
*   **Georeferencing**: Reading GeoTIFF metadata to map the pixel masks to real-world GPS coordinates.

---

**End of Technical Documentation**
