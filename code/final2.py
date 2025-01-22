# To create an executable for your Python script that includes the model from the same folder, you can use `PyInstaller`. Here are the steps to do this:

# 1. **Install PyInstaller**:
#     ```sh
#     pip install pyinstaller
#     ```

# 2. **Prepare your project folder**:
#     Ensure your project folder contains:
#     - `final2.py` (your script)
#     - `model` (your model directory)

# 3. **Create a `.spec` file**:
#     You can create a `.spec` file to customize the build process. Here is an example `final2.spec` file:
#     ```python
#     # final2.spec
#     # -*- mode: python ; coding: utf-8 -*-

#     block_cipher = None

#     a = Analysis(
#          ['final2.py'],
#          pathex=['.'],
#          binaries=[],
#          datas=[('model', 'model')],
#          hiddenimports=[],
#          hookspath=[],
#          runtime_hooks=[],
#          excludes=[],
#          win_no_prefer_redirects=False,
#          win_private_assemblies=False,
#          cipher=block_cipher,
#     )
#     pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
#     exe = EXE(
#          pyz,
#          a.scripts,
#          [],
#          exclude_binaries=True,
#          name='final2',
#          debug=False,
#          bootloader_ignore_signals=False,
#          strip=False,
#          upx=True,
#          upx_exclude=[],
#          runtime_tmpdir=None,
#          console=True,
#     )
#     coll = COLLECT(
#          exe,
#          a.binaries,
#          a.zipfiles,
#          a.datas,
#          strip=False,
#          upx=True,
#          upx_exclude=[],
#          name='final2',
#     )
#     ```

# 4. **Build the executable**:
#     Run the following command in your terminal:
#     ```sh
#     pyinstaller final2.spec
#     ```

# 5. **Locate the executable**:
#     After the build process completes, you will find the executable in the `dist/final2` directory.

# 6. **Run the executable**:
#     You can now run the `final2.exe` file from the `dist/final2` directory. Ensure that the `model` directory is in the same directory as the executable.

# This process will package your script and the model directory into a standalone executable that can be run on Windows.

import pdfplumber
import docx
import sys
import os
from transformers import pipeline
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QTextEdit, QMessageBox

# Determine the path where the executable or script is running
if getattr(sys, 'frozen', False):
    # If the script is running as an executable
    base_dir = os.path.dirname(sys.executable)
else:
    # If the script is running as a regular Python script
    base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_dir, "model")
summarizer = pipeline("summarization", model=model_path)

def summarize_text(text):
    # Split the text into words and chunk it to avoid exceeding the model's token limit
    words = text.split()
    max_chunk_size = 200  # Token limit for the model
    summarized_text = ""

    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i+max_chunk_size])
        try:
            summary = summarizer(chunk)[0]['summary_text']
            summarized_text += summary + " "
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            continue

    return summarized_text.strip()

def summarize_file(file_path):
    file_type = file_path.split('.')[-1].lower()
    text = ""

    try:
        # Handle PDF files
        if file_type == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

        # Handle DOCX files
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])

        # Handle TXT files
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        else:
            return "Unsupported file format."

    except Exception as e:
        print(f"Error reading file: {e}")
        return f"Error reading file: {e}"

    if not text.strip():
        return "The document is empty or could not be read."
    
    return summarize_text(text)

def on_click():
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(window, "Open File", "", 
                                               "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)", 
                                               options=options)
    if file_path:
        file_type = os.path.splitext(file_path)[1].lower()
        label.setText(f"File Type: {file_type}")
        
        summary = summarize_file(file_path)
        if summary:
            summary_text_edit.setPlainText(summary)
        else:
            QMessageBox.warning(window, "Error", "Failed to summarize the file.")

# Initialize the PyQt5 application
app = QApplication([])
window = QMainWindow()
window.setWindowTitle("Text Summarizer")

central_widget = QWidget()
layout = QVBoxLayout(central_widget)

# Button to upload file
button = QPushButton("Upload File")
button.clicked.connect(on_click)
layout.addWidget(button)

# Label to display the file type
label = QLabel("File Type: ")
layout.addWidget(label)

# Text area to display the summary
summary_text_edit = QTextEdit()
summary_text_edit.setReadOnly(True)
layout.addWidget(summary_text_edit)

window.setCentralWidget(central_widget)
window.setGeometry(100, 100, 700, 700)

# Show the window and run the application
window.show()
app.exec_()
