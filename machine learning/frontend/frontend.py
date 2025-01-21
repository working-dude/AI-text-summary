# import sys
# from PyQt5.QtCore import Qt, QTimer
# from PyQt5.QtGui import QMovie
# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
# import os

# class MainApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PDF/Text Summarizer")
#         self.setGeometry(100, 100, 800, 600)

#         # Main app content
#         label = QLabel("Welcome to the Summarizer App!", self)
#         label.setAlignment(Qt.AlignCenter)
#         self.setCentralWidget(label)

# class SplashScreen(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint)  # Frameless window
#         self.setGeometry(100, 100, 500, 400)  # Adjust size as needed

#         # Layout for splash screen
#         layout = QVBoxLayout(self)

#         # Load and display GIF
#         img_path = os.path.join(os.path.dirname(sys.argv[0]), "giphy.webp")
#         movie = QMovie(img_path)
#         if not movie.isValid():
#             print("Error: Unable to load splash GIF.")
#             sys.exit(1)

#         gif_label = QLabel()
#         gif_label.setMovie(movie)
#         layout.addWidget(gif_label)

#         # Start the GIF animation
#         movie.start()

#         # Optional loading message
#         loading_label = QLabel("Loading... Please wait")
#         loading_label.setAlignment(Qt.AlignCenter)
#         layout.addWidget(loading_label)

# class AppWithSplashScreen:
#     def __init__(self):
#         self.app = QApplication(sys.argv)

#         # Create splash screen
#         self.splash = SplashScreen()
#         self.splash.show()

#         # Simulate loading process
#         QTimer.singleShot(5000, self.start_main_app)  # 5 seconds for splash screen

#     def start_main_app(self):
#         self.main_window = MainApp()
#         self.main_window.show()
#         self.splash.close()

#     def run(self):
#         sys.exit(self.app.exec_())

# if __name__ == "__main__":
#     AppWithSplashScreen().run()


import sys
from PyQt5.QtCore import Qt, QTimer,QEventLoop
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
import os

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF/Text Summarizer")
        self.setGeometry(100, 100, 800, 600)

        # Simulate initialization process
        self.initialize_ui()

    def initialize_ui(self):
        # Simulating some setup or loading tasks
        QTimer.singleShot(2000, self.show_content)  # Simulating a 2-second setup

    def show_content(self):
        label = QLabel("Welcome to the Summarizer App!", self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Frameless window
        self.setGeometry(100, 100, 500, 400)  # Adjust size as needed

        # Layout for splash screen
        layout = QVBoxLayout(self)

        # Load and display GIF
        img_path = os.path.join(os.path.dirname(sys.argv[0]), "giphy.webp")
        movie = QMovie(img_path)
        if not movie.isValid():
            print("Error: Unable to load splash GIF.")
            sys.exit(1)

        gif_label = QLabel()
        gif_label.setMovie(movie)
        gif_label.setScaledContents(True)
        layout.addWidget(gif_label)

        # Start the GIF animation
        movie.start()

        # Optional loading message
        loading_label = QLabel("Loading... Please wait")
        loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(loading_label)

class AppWithSplashScreen:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.splash = SplashScreen()
        self.splash.show()

        # Simulate main window loading
        self.main_window = MainApp()

        # Wait for the main window to be ready
        self.check_main_window_ready()

    def check_main_window_ready(self):
        # Event loop to wait until the main window is fully initialized
        loop = QEventLoop()

        # Connect signal to exit the event loop when the main window is ready
        QTimer.singleShot(2000, loop.quit)  # Replace with dynamic ready condition if applicable
        loop.exec_()

        # Once ready, show the main window and close the splash
        self.start_main_app()

    def start_main_app(self):
        self.main_window.show()
        self.splash.close()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    AppWithSplashScreen().run()
