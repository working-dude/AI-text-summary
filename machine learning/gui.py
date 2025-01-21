from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget
import os

def on_click():
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(window, "Open File", "", "All Files (*);;Python Files (*.py)", options=options)
    if file_path:
        file_type = os.path.splitext(file_path)[1]
        label.setText(f"File Type: {file_type}")

app = QApplication([])
window = QMainWindow()
window.setWindowTitle("PyQt5 GUI")

central_widget = QWidget()
layout = QVBoxLayout(central_widget)

button = QPushButton("Upload File")
button.clicked.connect(on_click)
layout.addWidget(button)

label = QLabel("File Type: ")
layout.addWidget(label)

window.setCentralWidget(central_widget)
window.setGeometry(400, 400, 300, 200)

window.show()
app.exec_()
