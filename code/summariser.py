from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QTextEdit
import os
from transformers import pipeline
import PyPDF2
import docx

# Load summarizer and save model locally
pipe = pipeline("summarization", model="Falconsai/text_summarization", cache_dir="./model")
pipe.save_pretrained("./model")
summarizer = pipeline("summarization", model="./model")

# Step 2: Define the on_click function
def on_click():
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(window, "Open File", "", "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)", options=options)
    if file_path:
        file_type = os.path.splitext(file_path)[1]
        label.setText(f"File Type: {file_type}")
        
        with open(file_path, 'rb') as file:
            summary = summarize_file(file)
            # summary_label.setText(f"Summary: {summary}")
            summary_text_edit.setPlainText(summary)  

# Step 3: Define the summarization function
def summarize_file(file):
    file_type = file.name.split('.')[-1]
    if file_type == 'pdf':
        text = ""
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(3, min(10, len(pdf_reader.pages))):  # Pages are 0-indexed, so page 2 is index 1
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    elif file_type == 'docx':
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file_type == 'txt':
        text = file.read().decode("utf-8")
    else:
        return "Unsupported file format."

    words = text.split()
    # Summarize the text (if the text is too long, it needs to be split into chunks)
    if len(words) > 400:
        summarized_text = ""
        for i in range(0, len(words), 500):
            chunk = " ".join(words[i:i+500])
            summary = summarizer(chunk)[0]['summary_text']
            summarized_text += summary + " "
            print(i)
            print(len(words))
        return summarized_text.strip()
    else:
        summary = summarizer(text)[0]['summary_text']
        return summary

# Step 1: Create the GUI
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

summary_label = QLabel("Summary: ")
layout.addWidget(summary_label)

summary_text_edit = QTextEdit()
summary_text_edit.setReadOnly(True)
# summary_text_edit.setPlainText(summary)  
layout.addWidget(summary_text_edit)

window.setCentralWidget(central_widget)
window.setGeometry(100, 100, 700, 700)

window.show()
app.exec_()