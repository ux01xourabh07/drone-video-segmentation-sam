
import os
import torch
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, QApplication, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap 
from src.backend import SamController
from src.video_processor import VideoProcessorThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Video Live Segmentation")
        self.setFixedSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #2b2b2b; 
                color: #ffffff; 
                font-family: 'Segoe UI', Arial;
            }
            QLabel { 
                font-size: 14px; 
            }
            QPushButton { 
                background-color: #0078D7; 
                color: white; 
                border: none;
                border-radius: 4px; 
                padding: 10px 20px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #198CDD; 
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)

        # Backend
        self.backend = None
        
        # Dynamic Weight Selection
        # Default to Auto check for initial path
        device = SamController.get_device("auto")
        is_gpu = str(device) == "cuda" or (hasattr(device, 'type') and device.type == 'privateuseone')
        
        if is_gpu:
            self.checkpoint_path = os.path.join("weights", "sam_vit_h_4b8939.pth")
        else:
            self.checkpoint_path = os.path.join("weights", "sam_vit_b_01ec64.pth") 
        
        # State
        self.video_path = None
        self.video_thread = None
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. Header
        self.lbl_title = QLabel("Drone Live Segmentation Stream")
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(self.lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 2. Live Preview Canvas
        self.canvas = QLabel("No Signal")
        self.canvas.setStyleSheet("background-color: #000; border: 2px solid #555;")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setFixedSize(800, 500)
        layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3. Controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_select = QPushButton("Select Video Source")
        self.btn_select.clicked.connect(self.select_video)
        self.btn_select.setFixedWidth(200)
        
        self.btn_start = QPushButton("Start Live View")
        self.btn_start.clicked.connect(self.start_stream)
        self.btn_start.setFixedWidth(200)
        self.btn_start.setEnabled(False)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_stream)
        self.btn_stop.setFixedWidth(100)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #D70000;")

        # Device Selection
        self.combo_device = QComboBox()
        self.combo_device.addItems(["Auto-Detect", "NVIDIA (CUDA)", "AMD (DirectML)", "CPU Only"])
        self.combo_device.setFixedWidth(150)
        self.combo_device.setStyleSheet("padding: 5px;")
        
        btn_layout.addWidget(self.combo_device)
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)
        
        # Status
        self.lbl_status = QLabel("System Idle.")
        layout.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lazy_init_backend()

    def lazy_init_backend(self):
        if not os.path.exists(self.checkpoint_path):
             pass

    def ensure_backend_loaded(self):
        if not self.backend:
            # Update path based on selection
            selection = self.combo_device.currentText()
            if "CPU" in selection:
                 self.checkpoint_path = os.path.join("weights", "sam_vit_b_01ec64.pth")
            else:
                 # For Auto (with GPU), CUDA, or DirectML, try High Weight
                 self.checkpoint_path = os.path.join("weights", "sam_vit_h_4b8939.pth")

            self.lbl_status.setText(f"Initializing SAM ({os.path.basename(self.checkpoint_path)})...")
            QApplication.processEvents()
            try:
                # Map UI selection to preference string
                selection = self.combo_device.currentText()
                pref = "auto"
                if "CUDA" in selection: pref = "cuda"
                elif "DirectML" in selection: pref = "directml"
                elif "CPU" in selection: pref = "cpu"
                
                self.backend = SamController(self.checkpoint_path, device_preference=pref)
                self.lbl_status.setText("Engine Ready.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load model: {str(e)}")
                return False
        return True

    def select_video(self):
        initial_dir = os.path.join(os.getcwd(), "input_videos")
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)
            
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", initial_dir, "Videos (*.mp4 *.avi *.mkv *.wmv)")
        if path:
            self.video_path = path
            self.lbl_status.setText(f"Source: {os.path.basename(path)}")
            self.btn_start.setEnabled(True)

    def start_stream(self):
        if not self.ensure_backend_loaded(): return
        if not self.video_path: return
        
        self.lbl_status.setText("Streaming...")
        self.btn_select.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        # Start Thread
        # Note: We don't pass output_dir anymore
        self.video_thread = VideoProcessorThread(self.video_path, self.backend)
        self.video_thread.frame_processed.connect(self.update_frame)
        self.video_thread.status_update.connect(self.update_status) # New connection
        self.video_thread.error_occurred.connect(self.stream_error)
        self.video_thread.finished.connect(self.stream_finished)
        self.video_thread.start()

    def update_status(self, msg):
        self.lbl_status.setText(msg)

    def stop_stream(self):
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()
        
    def update_frame(self, q_image):
        if not q_image.isNull():
            # Scale to fit canvas
            pixmap = QPixmap.fromImage(q_image)
            self.canvas.setPixmap(pixmap.scaled(
                self.canvas.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))

    def stream_finished(self):
        self.lbl_status.setText("Stream Ended.")
        self.reset_ui()
        self.canvas.clear()
        self.canvas.setText("End of Signal")

    def stream_error(self, msg):
        self.lbl_status.setText("Stream Error.")
        QMessageBox.critical(self, "Stream Error", msg)
        self.reset_ui()
        
    def reset_ui(self):
        self.btn_select.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
