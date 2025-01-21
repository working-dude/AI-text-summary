import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
import os

class SplashApp:
    def __init__(self, main_window_class, splash_gif_path="giphy.webp", splash_duration=2000):
        """
        A reusable Splash Screen application class.

        Args:
            main_window_class (class or callable): The class or function to instantiate for the main window.
            splash_gif_path (str): Path to the splash screen GIF.
            splash_duration (int): Duration of the splash screen in milliseconds.
        """
        self.app = QApplication(sys.argv)
        self.main_window_class = main_window_class
        self.splash_gif_path = splash_gif_path
        self.splash_duration = splash_duration

        # Create the splash screen
        self.splash = self.create_splash_screen()
        self.splash.show()

        # Simulate loading process
        QTimer.singleShot(self.splash_duration, self.start_main_window)

    def create_splash_screen(self):
        """Creates a fullscreen splash screen with a GIF animation."""
        splash = QWidget()
        splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        splash.showFullScreen()

        # Layout for splash screen
        layout = QVBoxLayout(splash)

        # Load and display GIF
        self.splash_gif_path = os.path.join(os.path.dirname(sys.argv[0]), self.splash_gif_path)
        movie = QMovie(self.splash_gif_path)
        if not movie.isValid():
            print("Error: Unable to load splash GIF.")
            sys.exit(1)

        gif_label = QLabel()
        gif_label.setMovie(movie)
        gif_label.setScaledContents(True)  # Enable scaling to fit the full screen
        layout.addWidget(gif_label)

        # Start the GIF animation
        movie.start()

        # Optional loading message
        # loading_label = QLabel("Loading... Please wait")
        # loading_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(loading_label)

        return splash

    def start_main_window(self):
        """Closes the splash screen and starts the main window."""
        self.splash.close()
        self.main_window = self.main_window_class()
        self.main_window.show()

    def run(self):
        """Executes the application."""
        sys.exit(self.app.exec_())


# # Example Usage
# if __name__ == "__main__":
#     # class MainApp(QMainWindow):
#     #     def __init__(self):
#     #         super().__init__()
#     #         self.setWindowTitle("PDF/Text Summarizer")
#     #         self.setGeometry(100, 100, 800, 600)

#     #         # Main window content
#     #         label = QLabel("Welcome to the Summarizer App!", self)
#     #         label.setAlignment(Qt.AlignCenter)
#     #         self.setCentralWidget(label)

#     # Initialize and run the application
#     splash_app = SplashApp(main_window_class="", splash_gif_path="giphy.webp", splash_duration=2000)
#     splash_app.run()

# class SplashApp:
#     def __init__(self, main_window, splash_gif_path="giphy.webp"):
#         """
#         A reusable Splash Screen application class.

#         Args:
#             main_window (QMainWindow): The main window instance to show after splash.
#             splash_gif_path (str): Path to the splash screen GIF.
#         """
#         self.app = QApplication(sys.argv)
#         self.main_window = main_window
#         self.splash_gif_path = splash_gif_path

#         # Create the splash screen
#         self.splash = self.create_splash_screen()
#         self.splash.show()

#         # Wait until the main window signals readiness
#         self.main_window.ready.connect(self.start_main_window)

#     def create_splash_screen(self):
#         """Creates a fullscreen splash screen with a GIF animation."""
#         splash = QWidget()
#         splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
#         splash.showFullScreen()

#         # Layout for splash screen
#         layout = QVBoxLayout(splash)

#         # Load and display GIF
#         self.splash_gif_path = os.path.join(os.path.dirname(sys.argv[0]), self.splash_gif_path)
#         movie = QMovie(self.splash_gif_path)
#         if not movie.isValid():
#             print("Error: Unable to load splash GIF.")
#             sys.exit(1)

#         gif_label = QLabel()
#         gif_label.setMovie(movie)
#         gif_label.setScaledContents(True)  # Enable scaling to fit the full screen
#         layout.addWidget(gif_label)

#         # Start the GIF animation
#         movie.start()

#         return splash

#     def start_main_window(self):
#         """Closes the splash screen and starts the main window."""
#         self.splash.close()
#         self.main_window.show()

#     def run(self):
#         """Executes the application."""
#         sys.exit(self.app.exec_())
