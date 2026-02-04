# 🚁 Drone Video Segmentation System (v3.0)

## Project Overview
This project is an advanced, real-time video analysis tool designed to process aerial drone footage. It leverages Meta's **Segment Anything Model (SAM)** to intelligently identify and isolate man-made structures (buildings) and infrastructure from raw video feeds.

Unlike standard object detectors that simply draw bounding boxes, this system generates **pixel-perfect segmentation masks**, effectively "seeing" the exact shape and footprint of every building in the frame.

## 🌟 Key Capabilities

### 1. Universal Hardware Acceleration
The system is built to run on **any hardware**, automatically adapting its power to what is available:
-   **NVIDIA GPUs**: Uses **CUDA** for maximum speed.
-   **AMD GPUs**: Uses **DirectML** to unlock hardware acceleration on Radeon cards.
-   **CPU**: Uses optimized fallback settings to ensure the app runs smoothly even without a dedicated graphics card.

### 2. Intelligent Model Switching
To balance speed and accuracy, the system dynamically selects the best AI brain for the job:
-   **High-Performance Mode**: When a GPU is detected, it loads the **ViT-H (Huge)** model (2.5GB). This provides the highest possible segmentation quality.
-   **Efficiency Mode**: When running on CPU, it switches to the **ViT-B (Base)** model (375MB) and downscales processing to ensure real-time responsiveness.

### 3. Geometric Logic Layer
Raw AI output can be noisy. This project uses a custom "Geometric Intelligence" layer that filters the AI's results based on real-world physics:
-   **Solidity Checks**: Discards "ghost" shapes that aren't solid objects.
-   **Aspect Ratio Filtering**: Distinguishes between long roads and blocky buildings.
-   **Spatial Aggregation**: Merges fragmented window/roof detections into single, solid building footprints.

## 🎮 User Experience
The application features a modern, dark-themed GUI (PyQt6) designed for simplicity:
-   **Live Canvas**: Watch the AI segment the video in real-time.
-   **Device Control**: A dropdown menu gives you full control—force the system to use your specific GPU or stick to CPU.
-   **Status Feedback**: Real-time updates on which hardware and model are currently active.

## 🛠️ Technical Specifications
-   **Core Engine**: PyTorch + Segment Anything (SAM).
-   **Resolution**: Smart downscaling (Max 512px) for optimized inference speed.
-   **Framework**: PyQt6 (Frontend) + OpenCV (Image Processing).
-   **Compatibility**: Windows (Primary), Linux.

---
*Generated for SAM Drone Segmentation Project*
