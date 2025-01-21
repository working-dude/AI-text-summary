from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QTextEdit
import os

from transformers import pipeline
import PyPDF2
import docx
# Load summarizer and save model locally

pipe = pipeline("summarization", model="Falconsai/text_summarization", cache_dir="./model")
pipe.save_pretrained("./model")
summarizer = pipeline("summarization", model="./model")

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


def summarize_file(file):
    file_type = file.name.split('.')[-1]
    text = ""

    # Handle PDF files
    if file_type == 'pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:  # Avoid processing pages with no text
                text += page_text

    # Handle DOCX files
    elif file_type == 'docx':
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])

    # Handle TXT files
    elif file_type == 'txt':
        text = file.read().decode("utf-8")

    else:
        return "Unsupported file format."

    # Split the text into words and chunk it to avoid exceeding the model's token limit
    words = text.split()
    max_chunk_size = 512  # Token limit for the model

    # Summarize the text in chunks
    summarized_text = ""
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i+max_chunk_size])
        summary = summarizer(chunk)[0]['summary_text']
        summarized_text += summary + " "

    return summarized_text.strip()

# article='''
# The history of artificial intelligence (AI) began in antiquity, with myths, stories and rumors of artificial beings endowed with intelligence or consciousness by master craftsmen. The seeds of modern AI were planted by classical philosophers who attempted to describe the process of human thinking as
# the mechanical manipulation of symbols. This work culminated in the invention of the programmable digital computer in the 1940s, a machine based on the abstract essence of mathematical reasoning. This device and the ideas behind it inspired a handful of scientists to begin seriously discussing the possibility of building an electronic brain.
# '''
# print(len(article.split()))
# # Step 4: Test the summarization function
# summary=summarizer(article,min_length=len(article.split())//2)[0]['summary_text']
# print(summary)
# leng=summary.split()
# print(len(leng))


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
