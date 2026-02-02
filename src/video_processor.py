
import cv2
import os
import numpy as np
import gc
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

class VideoProcessorThread(QThread):
    # Live Preview Signal: Emits QImage to display immediately
    frame_processed = pyqtSignal(QImage) 
    status_update = pyqtSignal(str) # New: For granular updates
    error_occurred = pyqtSignal(str) 

    def __init__(self, video_path, sam_controller):
        super().__init__()
        self.video_path = video_path
        self.sam_controller = sam_controller
        self.is_running = True

    def run(self):
        try:
            if not os.path.exists(self.video_path):
                raise FileNotFoundError(f"Video not found: {self.video_path}")

            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise ValueError("Could not open video.")

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Smart Resize for Speed (Lower is faster on CPU)
            MAX_DIM = 640 
            scale = 1.0
            if max(height, width) > MAX_DIM:
                scale = MAX_DIM / max(height, width)
                out_w = int(width * scale) 
                out_h = int(height * scale)
            else:
                out_w = width
                out_h = height
            
            frame_idx = 0
            
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Report Status
                self.status_update.emit(f"Segmenting Frame {frame_idx + 1}...")
                
                # Resize Input Frame
                if scale != 1.0:
                    frame = cv2.resize(frame, (out_w, out_h), interpolation=cv2.INTER_AREA)
                
                # SAM Processing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                try:
                    masks = self.sam_controller.mask_generator.generate(frame_rgb)
                except RuntimeError as e:
                    print(f"Skipping frame {frame_idx} due to OOM")
                    continue
                
                # --- Building Extraction ---
                building_accum = np.zeros((out_h, out_w), dtype=bool)
                img_area = out_h * out_w
                
                for m in masks:
                    area = m['area']
                    if area / img_area < 0.0005: continue
                    category = self.sam_controller.classify_mask_geometry(m['segmentation'], area)
                    if category == "Building":
                        building_accum = np.logical_or(building_accum, m['segmentation'])
                
                kernel_size = int(max(out_h, out_w) * 0.005)
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                building_uint8 = (building_accum.astype(np.uint8) * 255)
                building_closed = cv2.morphologyEx(building_uint8, cv2.MORPH_CLOSE, kernel)
                
                # Composite
                overlay = np.zeros_like(frame)
                overlay[:, :, 2] = building_closed # Red channel
                
                mask_bool = building_closed > 0
                frame[mask_bool] = cv2.addWeighted(frame[mask_bool], 0.6, overlay[mask_bool], 0.4, 0)
                
                # Convert to QImage for UI Display
                # Frame is in BGR (from cv2.read), but we processed logic using frame_rgb
                # But 'frame' variable is still BGR. overlay is BGR (Red in channel 2).
                # Wait, overlay[:,:,2] is Red in BGR. Correct.
                
                # QImage expects RGB usually.
                frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_display.shape
                bytes_per_line = frame_display.strides[0]
                q_img = QImage(frame_display.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
                
                self.frame_processed.emit(q_img)
                
                frame_idx += 1
                if frame_idx % 5 == 0:
                    gc.collect()

            cap.release()
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        self.is_running = False
