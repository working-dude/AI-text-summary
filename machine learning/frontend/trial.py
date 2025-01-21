from loading_screen import SplashApp
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtCore import Qt

class MainApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("PDF/Text Summarizer")
            self.setGeometry(100, 100, 800, 600)

            # Main window content
            label = QLabel("jaldi kaa the Summarizer App!", self)
            label.setAlignment(Qt.AlignCenter)
            self.setCentralWidget(label)
        
if __name__ == "__main__":
    splash_app = SplashApp(MainApp)
    splash_app.run()