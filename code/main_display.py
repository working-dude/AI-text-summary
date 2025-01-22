import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox
)
from pdf_summariser_class import PDFSummarizer

class PDFSummarizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.summarizer = PDFSummarizer()

    def initUI(self):
        self.setWindowTitle('PDF Summarizer')
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Instruction label
        self.label = QLabel('Select a PDF file or a folder to summarize:')
        layout.addWidget(self.label)

        # Buttons for file and folder selection
        self.file_button = QPushButton('Select File (PDF, DOCX, TXT)')
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        self.folder_button = QPushButton('Select Folder')
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        # Text area for displaying results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Save summary button
        self.save_button = QPushButton('Save Summary as PDF')
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.clicked.connect(self.save_summary)
        layout.addWidget(self.save_button)

        # Set layout
        self.setLayout(layout)

        # Placeholder for summarized text
        self.summary_text = ""

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'Supported Files (*.pdf *.docx *.txt)'
        )
        if file_path:
            self.result_text.clear()
            self.result_text.append(f"Summarizing file: {file_path}...\n")
            QApplication.processEvents()  # Allow UI to update during processing

            # Summarize the file
            try:
                summaries = list(self.summarizer.summarize_file_incrementally(file_path))
                corrected_summaries = [self.summarizer.correct_grammar(summary) for summary in summaries]
                self.summary_text = "\n\n".join(corrected_summaries)
                self.result_text.setPlainText(self.summary_text)

                # Enable save button after summarization
                self.save_button.setEnabled(True)
            except Exception as e:
                self.result_text.append(f"Error summarizing file: {e}")

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.result_text.clear()
            self.result_text.append(f"Summarizing folder: {folder_path}...\n")
            QApplication.processEvents()

            # Summarize the folder
            try:
                summaries = self.summarizer.summarize_folder(folder_path)
                combined_text = "\n\n".join([
                    f"{filename}:\n{'\n'.join(summaries[filename])}" for filename in summaries
                ])
                corrected_text = self.summarizer.correct_grammar(combined_text)
                self.summary_text = corrected_text
                self.result_text.setPlainText(self.summary_text)

                # Enable save button after summarization
                self.save_button.setEnabled(True)
            except Exception as e:
                self.result_text.append(f"Error summarizing folder: {e}")

    def save_summary(self):
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
    app = QApplication(sys.argv)
    ex = PDFSummarizerApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
