# 🚁 Drone Video Segmentation SAM

**Real-time automated building segmentation for aerial drone video using Meta's Segment Anything Model (SAM).**

This tool provides a **Live Preview** desktop application that processes drone footage frame-by-frame, applying geometric intelligence to isolate buildings and infrastructure in real-time.

![Status](https://img.shields.io/badge/Status-Live%20Production-green)
![Tech](https://img.shields.io/badge/Tech-SAM%20|%20PyQt6%20|%20OpenCV-blue)
![Repo](https://img.shields.io/badge/GitHub-ux01xourabh07-black)

🔗 **Repository**: [https://github.com/ux01xourabh07/drone-video-segmentation-sam.git](https://github.com/ux01xourabh07/drone-video-segmentation-sam.git)

---

## 🚀 Key Features

*   **Live Video Stream**: processed results are displayed instantly on a "Live Canvas".
*   **Building-Only Focus**: Smart geometric filtering (`Solidity`, `Extent`) automatically isolates buildings from roads/vegetation.
*   **CPU Optimized**: Runs on standard hardware using smart resizing (640px) and the efficient ViT-B model.
*   **Visual Feedback**: Real-time status updates ("Segmenting Frame 25...") to monitor performance.

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ux01xourabh07/drone-video-segmentation-sam.git
cd drone-video-segmentation-sam
```

### 2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Mac/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Model Weights
You need the **SAM ViT-B** checkpoint (375MB).  
Download `sam_vit_b_01ec64.pth` from Meta's repository and place it in the `weights/` folder.
*   [Download Link (Official)](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth)

**Directory Structure:**
```
drone-video-segmentation-sam/
├── weights/
│   └── sam_vit_b_01ec64.pth
├── src/
├── main.py
└── ...
```

---

## 🎮 How to Run

1.  **Start the Application**:
    ```bash
    python main.py
    ```
2.  **Select Video**: Click **"Select Video Source"** and choose any `.mp4`, `.avi`, or `.mkv` drone file.
3.  **Start Stream**: Click **"Start Live View"**.
4.  **Observe**: The application will perform live inference. The bottom status bar shows the current frame being processed.

---

## 📦 Pushing Logic & Contribution

If you have made changes and want to push the code to the repository, follow these standard Git commands:

1.  **Initialize & Add Files**:
    ```bash
    git init
    git add .
    git commit -m "Update project features"
    ```

2.  **Link Remote Repository**:
    ```bash
    git branch -M main
    git remote add origin https://github.com/ux01xourabh07/drone-video-segmentation-sam.git
    ```

3.  **Push to GitHub**:
    ```bash
    git push -u origin main
    ```

---

**Developed by Sourabh** | Powered by [Segment Anything Model](https://segment-anything.com/)
