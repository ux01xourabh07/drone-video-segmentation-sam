import sys
import os
from PyQt6.QtWidgets import QApplication
from src.ui import MainWindow

def main():
    # Ensure correct working directory
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
