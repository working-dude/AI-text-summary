import os
import sys
import torch
from transformers import pipeline
import pdfplumber
import docx
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QTextEdit, QSplashScreen
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QMovie, QPixmap

# Define model and device (CUDA, CPU, or MPS for Apple Silicon)
model_name = "facebook/bart-large-cnn"
device = 0 if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_built() else -1)  # Use GPU if available, MPS for Apple M1/M2, else CPU

# Load the summarizer once, based on platform and device
summarizer = None  # This will be initialized later

def load_model():
    """Load the summarizer model in a separate thread to avoid blocking the UI."""
    global summarizer
    summarizer = pipeline("summarization", model=model_name, device=device)

def summarize_chunk(chunk):
    """Summarizes a single chunk of text."""
    try:
        return summarizer(chunk)[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing chunk: {e}")
        return ""

def summarize_text_incrementally_generator(text):
    """Generates summarized chunks incrementally."""
    words = text.split()
    max_chunk_size = 500  # Adjust chunk size for performance

    # Split text into chunks of max_chunk_size words
    chunks = [" ".join(words[i:i+max_chunk_size]) for i in range(0, len(words), max_chunk_size)]

    # Process chunks using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        results = executor.map(summarize_chunk, chunks)
        for result in results:
            yield result  # Yield each summarized chunk as it's completed

def summarize_file_incrementally(file_path):
    """Generates summaries incrementally from a file (PDF, DOCX, TXT)."""
    file_type = file_path.split('.')[-1].lower()
    text = ""

    try:
        # Handle PDF files
        if file_type == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        yield from summarize_text_incrementally_generator(page_text)

        # Handle DOCX files
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            yield from summarize_text_incrementally_generator(text)

        # Handle TXT files
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            yield from summarize_text_incrementally_generator(text)

        else:
            yield "Unsupported file format."

    except Exception as e:
        print(f"Error reading file: {e}")
        yield f"Error reading file: {e}"

class SummarizeThread(QThread):
    """Thread to handle file summarization incrementally."""
    update_text = pyqtSignal(str)  # Signal to update the text in the window
    finished = pyqtSignal()  # Signal to indicate the summarization is finished

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """Executes the summarization and emits results chunk by chunk."""
        for chunk_summary in summarize_file_incrementally(self.file_path):
            self.update_text.emit(chunk_summary)  # Emit signal to update the GUI
        self.finished.emit()  # Emit finished signal when done

class SummarizeMultipleFilesThread(QThread):
    """Thread to handle multiple file summarizations incrementally."""
    update_text = pyqtSignal(str)  # Signal to update the text in the window
    finished = pyqtSignal()  # Signal to indicate the summarization is finished

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        """Executes the summarization for multiple files and emits results chunk by chunk."""
        for file_path in self.file_paths:
            for chunk_summary in summarize_file_incrementally(file_path):
                self.update_text.emit(chunk_summary)  # Emit signal to update the GUI
        self.finished.emit()  # Emit finished signal when done

def update_summary_text(chunk_summary):
    """Appends the incremental summary to the QTextEdit."""
    current_text = window.summary_text_edit.toPlainText()  # Get current text
    window.summary_text_edit.setPlainText(current_text + chunk_summary + "\n")  # Append new chunk

class IncrementalFileSummarizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Incremental File Summarizer")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Button to upload a file and start incremental summarization
        button_incremental = QPushButton("Upload File (Incremental Summary)")
        button_incremental.clicked.connect(self.on_click_incremental)
        layout.addWidget(button_incremental)

        # Button to upload multiple files and start incremental summarization
        button_multiple_files = QPushButton("Upload Multiple Files (Incremental Summary)")
        button_multiple_files.clicked.connect(self.on_click_multiple_files)
        layout.addWidget(button_multiple_files)

        # Label to display file processing status
        self.label = QLabel("Summary:")
        layout.addWidget(self.label)

        # Text edit box to display summaries incrementally
        self.summary_text_edit = QTextEdit()
        self.summary_text_edit.setReadOnly(True)
        layout.addWidget(self.summary_text_edit)

        # Set up the window layout and geometry
        self.setCentralWidget(central_widget)

    def on_click_incremental(self):
        """Handles file upload and starts incremental summarization."""
        # options = QFileDialog.Options()
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)", options=options)
        file_path = "ronaldo.pdf"
        if file_path:
            self.label.setText(f"Summarizing {file_path}...")
            self.summary_text_edit.clear()  # Clear the text edit box before starting

            # Start summarizing in a separate thread to avoid blocking the UI
            self.summarize_thread = SummarizeThread(file_path)
            self.summarize_thread.update_text.connect(update_summary_text)  # Connect signal to update function
            self.summarize_thread.finished.connect(self.on_summarization_finished)  # Connect finished signal to slot
            self.summarize_thread.start()

    def on_click_multiple_files(self):
        """Handles multiple file uploads and starts incremental summarization."""
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open Files", "", "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)", options=options)
        # file_paths = ["ronaldo.pdf", "ml.pdf"]
        if file_paths:
            self.label.setText(f"Summarizing {len(file_paths)} files...")
            self.summary_text_edit.clear()  # Clear the text edit box before starting

            # Start summarizing in a separate thread to avoid blocking the UI
            self.summarize_thread = SummarizeMultipleFilesThread(file_paths)
            self.summarize_thread.update_text.connect(update_summary_text)  # Connect signal to update function
            self.summarize_thread.finished.connect(self.on_summarization_finished)  # Connect finished signal to slot
            self.summarize_thread.start()

    def on_summarization_finished(self):
        """Slot to handle the end of summarization."""
        print("Summarization complete!")

class splasher:
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


def show_splash_screen(app):
    splash_pix = splasher()  # Create an empty QPixmap
    # splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)  # Create a transparent splash screen
    # splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
    # splash.setAttribute(Qt.WA_TranslucentBackground)=
    splash_pix.show()

    # Simulate loading process
    QTimer.singleShot(3000, splash_pix.close)  # Close splash screen after 3 seconds

if __name__ == "__main__":
    app = QApplication(sys.argv)
    show_splash_screen(app)

    # Main window will be shown after splash screen finishes
    window = IncrementalFileSummarizer()
    
    app.exec_()
