from loading_screen import SplashApp
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit
from pdf_summariser_class import PDFSummarizer

class PDFSummarizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.summarizer = None

    def initUI(self):
        self.setWindowTitle('PDF Summarizer')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel('Select a PDF file or a folder to summarize:')
        layout.addWidget(self.label)

        self.file_button = QPushButton('Select PDF File')
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        self.folder_button = QPushButton('Select Folder')
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def select_file(self):
        if self.summarizer:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open PDF File', '', 'PDF Files (*.pdf)')
            if file_path:
                print(f"Selected file: {file_path}")  # Debug print
                summaries = list(self.summarizer.summarize_file_incrementally(file_path))
                corrected_summaries = [self.summarizer.correct_grammar(summary) for summary in summaries]
                final_text = "\n".join(corrected_summaries)
                self.result_text.setPlainText(final_text)
            else:
                print("No file selected.")  # Debug print

    def select_folder(self):
        if self.summarizer:
            folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
            if folder_path:
                output_file_path, _ = QFileDialog.getSaveFileName(self, 'Save Summary PDF', '', 'PDF Files (*.pdf)')
                if output_file_path:
                    header = "Summarized and Corrected Text"
                    self.summarizer.summarize_folder_to_pdf(folder_path, output_file_path, header)
                    self.result_text.setPlainText(f"Summary saved to {output_file_path}")
                else:
                    print("No output file selected.")  # Debug print
            else:
                print("No folder selected.")  # Debug print

class SummarizerProcess(QThread):
    summarizer_ready = pyqtSignal(object)

    def run(self):
        summarizer = PDFSummarizer()
        self.summarizer_ready.emit(summarizer)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF/Text Summarizer")
        self.setGeometry(100, 100, 800, 600)

        self.pdf_summarizer_app = PDFSummarizerApp()
        self.setCentralWidget(self.pdf_summarizer_app)

        self.summarizer_thread = SummarizerProcess()
        self.summarizer_thread.summarizer_ready.connect(self.on_summarizer_ready)
        self.summarizer_thread.start()

    def on_summarizer_ready(self, summarizer):
        self.pdf_summarizer_app.summarizer = summarizer

if __name__ == "__main__":
    splash_app = SplashApp(MainApp)
    splash_app.run()
