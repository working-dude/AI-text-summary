import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox, QProgressBar, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QEventLoop
from PyQt5.QtGui import QFont
import pdfplumber
import docx
import os
from frontend import SplashScreen

class SummarizerThread(QThread):
    """
    A QThread to handle the summarization process in the background.
    """
    progress = pyqtSignal(str)  # Signal to send incremental updates
    progress_bar_update = pyqtSignal(int)  # Signal to update progress bar
    finished = pyqtSignal()  # Signal to indicate completion

    def __init__(self, summarizer, file_path=None, folder_path=None, summary_length='medium'):
        super().__init__()
        self.summarizer = summarizer
        self.file_path = file_path
        self.folder_path = folder_path
        self.summary_length = summary_length

    def run(self):
        """
        Runs the summarization process.
        """
        try:
            total_length = 0
            processed_length = 0  # Track the processed length
            if self.file_path:
                total_length = self.calculate_total_length(self.file_path)
                # Summarize a single file
                for summary in self.summarizer.summarize_file_incrementally(self.file_path, self.summary_length):
                    self.progress.emit(summary)
                    processed_length += len(summary)
                    self.progress_bar_update.emit(int((processed_length / total_length) * 100))
            elif self.folder_path:
                total_length = self.calculate_total_length_folder(self.folder_path)
                for file in os.listdir(self.folder_path):
                    file_path = os.path.join(self.folder_path, file)
                    for summary in self.summarizer.summarize_file_incrementally(file_path, self.summary_length):
                        self.progress.emit(summary)
                        processed_length += len(summary)
                        self.progress_bar_update.emit(int((processed_length / total_length) * 100))
            self.finished.emit()
            self.progress_bar_update.emit(100)  # Ensure progress bar is complete
        except Exception as e:
            self.progress.emit(f"Error: {e}")
            self.finished.emit()  # Ensure finished signal is emitted on error

    def calculate_total_length(self, file_path):
        """
        Calculates the total length of the file content.

        :param file_path: The path to the file.
        :return: The total length of the file content.
        """
        total_length = 0
        if file_path.endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    total_length += len(page.extract_text())
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                total_length += len(paragraph.text)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r') as file:
                total_length += len(file.read())
        return total_length

    def calculate_total_length_folder(self, folder_path):
        """
        Calculates the total length of all files in a folder.

        :param folder_path: The path to the folder.
        :return: The total length of all files in the folder.
        """
        total_length = 0
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            total_length += self.calculate_total_length(file_path)
        return total_length

class InitializationThread(QThread):
    """
    A QThread to handle the initialization of the PDFSummarizer.
    """
    initialization_complete = pyqtSignal(object)

    def run(self):
        """
        Runs the initialization process.
        """
        try:
            from pdf_summariser_class import PDFSummarizer
            summarizer = PDFSummarizer(model_name="model")
            self.initialization_complete.emit(summarizer)
        except Exception as e:
            print(f"Initialization error: {e}")
            self.initialization_complete.emit(None)

class PDFSummarizerApp(QWidget):
    """
    The main application window for the PDF Summarizer.
    """
    def __init__(self, summarizer):
        super().__init__()
        self.summarizer = summarizer
        self.summary_text = ""
        self.thread = None
        self.initUI()

    def initUI(self):
        """
        Initializes the UI components.
        """
        self.setWindowTitle('PDF2 Summarizer')
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Instruction label
        self.label = QLabel('Select a PDF file or a folder to summarize:')
        layout.addWidget(self.label)

        # File/Folder being summarized label
        self.current_file_label = QLabel('')
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.current_file_label.setFont(font)
        layout.addWidget(self.current_file_label)

        # Set stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f9;
            }
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTextEdit {
                font-size: 14px;
                color: #34495e;
                background-color: white;
                border: 1px solid #dcdcdc;
                padding: 10px;
            }
            QProgressBar {
                border-radius: 5px;
                background-color: #ecf0f1;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
            QComboBox {
                font-size: 14px;
                color: #34495e;
                background-color: white;
                border: 1px solid #dcdcdc;
                padding: 5px;
            }
        """)

        # Buttons for file and folder selection
        self.file_button = QPushButton('Select File (PDF, DOCX, TXT)')
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        self.folder_button = QPushButton('Select Folder')
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        # Dropdown for summary length selection
        self.summary_length_combo = QComboBox()
        self.summary_length_combo.addItems(['small', 'medium', 'large'])
        layout.addWidget(self.summary_length_combo)

        # Text area for displaying results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Save summary button
        self.save_button = QPushButton('Save Summary as PDF')
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.clicked.connect(self.save_summary)
        layout.addWidget(self.save_button)

        # Set layout
        self.setLayout(layout)

    def start_summarization_thread(self, file_path=None, folder_path=None):
        """
        Starts the summarization thread.

        :param file_path: The path to the file to summarize.
        :param folder_path: The path to the folder to summarize.
        """
        summary_length = self.summary_length_combo.currentText()
        if file_path:
            self.current_file_label.setText(f"Summarizing File: {file_path}")
            self.thread = SummarizerThread(self.summarizer, file_path=file_path, summary_length=summary_length)
        elif folder_path:
            self.current_file_label.setText(f"Summarizing Folder: {folder_path}")
            self.thread = SummarizerThread(self.summarizer, folder_path=folder_path, summary_length=summary_length)

        # Connect signals
        self.thread.progress.connect(self.update_text_incrementally)
        self.thread.progress_bar_update.connect(self.update_progress_bar)
        self.thread.finished.connect(self.summarization_finished)

        # Clear the previous result
        self.result_text.clear()
        self.summary_text = ""
        
        # Set up the progress bar
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        # Disable buttons
        self.file_button.setEnabled(False)
        self.folder_button.setEnabled(False)
        
        # Start the thread
        self.thread.start()

    def summarization_finished(self):
        """
        Handles the completion of the summarization process.
        """
        self.thread = None
        self.save_button.setEnabled(True)
        self.progress_bar.setValue(self.progress_bar.maximum())  # Set progress bar to complete
        QMessageBox.information(self, "Summarization Complete", "Summarization is complete.")
        
        # Re-enable buttons
        self.file_button.setEnabled(True)
        self.folder_button.setEnabled(True)

    def update_text_incrementally(self, chunk):
        """
        Updates the text area incrementally with summarized chunks.

        :param chunk: The summarized chunk of text.
        """
        self.summary_text += chunk + "\n"
        self.result_text.append(chunk)
        QApplication.processEvents()  # Ensure the UI updates in real-time

    def update_progress_bar(self, value):
        """
        Updates the progress bar.

        :param value: The value to update the progress bar with.
        """
        self.progress_bar.setValue(self.progress_bar.value() + value)

    def select_file(self):
        """
        Opens a file dialog to select a file for summarization.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'Supported Files (*.pdf *.docx *.txt)'
        )
        if file_path:
            self.save_button.setEnabled(False)
            self.start_summarization_thread(file_path=file_path)

    def select_folder(self):
        """
        Opens a file dialog to select a folder for summarization.
        """
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.save_button.setEnabled(False)
            self.start_summarization_thread(folder_path=folder_path)

    def save_summary(self):
        """
        Saves the summarized text as a PDF.
        """
        if self.summary_text:
            output_file_path, _ = QFileDialog.getSaveFileName(
                self, 'Save Summary PDF', '', 'PDF Files (*.pdf)'
            )
            if output_file_path:
                header = "Summarized and Corrected Text"
                try:
                    self.summarizer.create_beautiful_pdf(output_file_path, self.summary_text, header)
                    QMessageBox.information(self, "Success", f"Summary saved to {output_file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error saving PDF: {e}")
        else:
            QMessageBox.warning(self, "No Summary", "No summary available to save.")

def main():
    """
    The main entry point for the application.
    """
    app = QApplication(sys.argv)
    app.main_window = None  # Add this line to hold a reference to main_window

    # Create splash screen with fixed size
    splash = SplashScreen(800, 600)
    splash.show()
    app.processEvents()
    
    # Start the initialization thread during splash screen
    init_thread = InitializationThread()
    
    # Function to handle transition after initialization
    def on_initialization_complete(summarizer):
        if summarizer is not None:
            # Initialize main window with the loaded summarizer
            app.main_window = PDFSummarizerApp(summarizer)  # Store reference in app
            splash.close()
            app.main_window.show()
            # Center main window
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - app.main_window.width()) // 2
            y = (screen.height() - app.main_window.height()) // 2
            app.main_window.move(x, y)
        else:
            splash.close()
            QMessageBox.critical(None, "Initialization Error", "An error occurred during initialization.")
            sys.exit(1)  # Exit the application with an error code

    # Connect the signal and start the initialization thread
    init_thread.initialization_complete.connect(on_initialization_complete)
    init_thread.start()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
    