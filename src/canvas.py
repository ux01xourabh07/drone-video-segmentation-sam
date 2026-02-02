from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class ImageCanvas(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background-color: #1e1e1e; border: 2px solid #333;")
        self._original_pixmap = None
        
    def set_image(self, image_path):
        """Loads and displays the image, scaled to fit the canvas."""
        self._original_pixmap = QPixmap(image_path)
        self._update_display()

    def _update_display(self):
        if self._original_pixmap and not self._original_pixmap.isNull():
            # Scale to fit current size, keeping aspect ratio
            scaled = self._original_pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)
        else:
            self.setText("No Image")

    def resizeEvent(self, event):
        """Handle resize to keep image scaled correctly (if layout changes)."""
        super().resizeEvent(event)
        self._update_display()
