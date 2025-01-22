import sys
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
import os

class MainApp(QMainWindow):
    """
    The main application window for the PDF/Text Summarizer.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF/Text Summarizer")
        self.setGeometry(100, 100, 800, 600)

        # Simulate initialization process
        self.initialize_ui()

    def initialize_ui(self):
        """
        Simulates some setup or loading tasks.
        """
        QTimer.singleShot(15000, self.show_content)  # Simulating a 15-second setup

    def show_content(self):
        """
        Displays the main content of the application.
        """
        label = QLabel("Welcome to the Summarizer App!", self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

class SplashScreen(QWidget):
    """
    The splash screen displayed during the initialization of the main application.
    """
    def __init__(self, width, height):
        super().__init__()
        # Set up window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set size to match main window
        self.setFixedSize(width, height)
        
        # Center on screen
        self.center_on_screen()
        
        # Main layout with zero margins and spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container widget with background
        container = QWidget()
        container.setObjectName("background")
        container.setStyleSheet("""
            QWidget#background {
                background-color: rgba(255, 255, 255, 0.95);
            }
        """)
        
        # Container layout with zero margins and spacing
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Loading animation without fixed size
        gif_label = QLabel()
        if getattr(sys, 'frozen', False):
            gif_path = os.path.join(sys._MEIPASS, "Assests", "ae.gif")
        else:
            gif_path = os.path.join(os.path.dirname(__file__), "Assests", "ae.gif")
        movie = QMovie(gif_path)
        if movie.isValid():
            gif_label.setMovie(movie)
            movie.start()
        else:
            gif_label.setText("Loading...")
            gif_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        
        gif_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(gif_label)

        # Loading text
        loading_label = QLabel("Initializing PDF Summarizer...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold;
            margin: 20px 0;
        """)
        container_layout.addWidget(loading_label)

        layout.addWidget(container)

    def center_on_screen(self):
        """
        Centers the splash screen on the screen.
        """
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

class AppWithSplashScreen:
    """
    The application class that manages the splash screen and the main window.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.splash = SplashScreen(800, 600)
        self.splash.show()

        # Simulate main window loading
        self.main_window = MainApp()

        # Wait for the main window to be ready
        self.check_main_window_ready()

    def check_main_window_ready(self):
        """
        Waits until the main window is fully initialized.
        """
        loop = QEventLoop()
        QTimer.singleShot(15000, loop.quit)  # Replace with dynamic ready condition if applicable
        loop.exec_()
        self.start_main_app()

    def start_main_app(self):
        """
        Starts the main application.
        """
        self.main_window.show()
        self.splash.close()

    def run(self):
        """
        Runs the application event loop.
        """
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    AppWithSplashScreen().run()
