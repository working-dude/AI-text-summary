import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class NewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Second GUI")
        self.showMaximized()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label_image = QLabel(self)
        pixmap = QPixmap('brave_tAduad6WgX.png')
        self.label_image.setPixmap(pixmap)
        self.label_image.setScaledContents(True)
        self.label_image.setGeometry(0, 0, self.width(), self.height())
        self.label_image.lower()
        
        self.b1 = QPushButton("Second", self)
        self.b1.setFont(QFont("Arial", 20))
        self.b1.setStyleSheet("background: none;")
        self.layout.addWidget(self.b1, alignment=Qt.AlignCenter)
        
        self.label = QLabel("Initial Text", self)
        self.label.setStyleSheet("color: red; font-size: 20px; font-weight: bold; background: none;")
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        self.b1.clicked.connect(self.openNewWindow)

    def resizeEvent(self, event):
        self.label_image.setGeometry(0, 0, self.width(), self.height())
        if not self.label_image.pixmap().isNull():
            self.label_image.setPixmap(
                self.label_image.pixmap().scaled(
                    self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
            )
        super().resizeEvent(event)

    def openNewWindow(self):
        self.central_widget = NewWindow()
        self.setCentralWidget(self.central_widget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("First GUI")
        self.showMaximized()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label_image = QLabel(self)
        pixmap = QPixmap('brave_tAduad6WgX.png')
        self.label_image.setPixmap(pixmap)
        self.label_image.setScaledContents(True)
        self.label_image.setGeometry(0, 0, self.width(), self.height())
        self.label_image.lower()
        
        self.b1 = QPushButton("Start", self)
        self.b1.setFont(QFont("Arial", 20))
        self.b1.setStyleSheet("background: none;")
        self.layout.addWidget(self.b1, alignment=Qt.AlignCenter)
        
        self.label = QLabel("Initial Text", self)
        self.label.setStyleSheet("color: red; font-size: 20px; font-weight: bold; background: none;")
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        self.b1.clicked.connect(self.openNewWindow)

    def resizeEvent(self, event):
        self.label_image.setGeometry(0, 0, self.width(), self.height())
        if not self.label_image.pixmap().isNull():
            self.label_image.setPixmap(
                self.label_image.pixmap().scaled(
                    self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
            )
        super().resizeEvent(event)

    def openNewWindow(self):
        self.central_widget = NewWindow()
        self.setCentralWidget(self.central_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()