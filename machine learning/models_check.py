import docx
import pdfplumber

from transformers import pipeline
# Load summarizer and save model locally
model="t5-small"
summarizer=pipeline("summarization", model=model)
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# def summarize_file(file):
#     file_type = file.name.split('.')[-1]
#     text = ""
#     # Handle PDF files
#     if file_type == 'pdf':
#         with pdfplumber.open(file) as pdf:
#             for page in pdf.pages:
#                 text += page.extract_text()
#     # Handle DOCX files
#     elif file_type == 'docx':
#         doc = docx.Document(file)
#         text = "\n".join([para.text for para in doc.paragraphs])
#     # Handle TXT files
#     elif file_type == 'txt':
#         text = file.read().decode("utf-8")
#     else:
#         return "Unsupported file format."
#     return text
# import re
text = ''
with pdfplumber.open("ronaldo.pdf") as pdf:
    all_text = ""
    for page in pdf.pages:
        # Extract text with "spread" layout to manage multi-column PDFs
        extracted_text = page.extract_text(x_tolerance=2, y_tolerance=3, layout=True)
        if extracted_text:
            # Replace multiple spaces with a single space, but keep newlines (\n)
            # extracted_text = re.sub(r'[ ]{2,}', ' ', extracted_text)  # Replaces multiple spaces with a single space
            all_text += extracted_text + '\n'  # Preserve line breaks between pages
    
    length = len(all_text)
    print("length ", length)
    words = all_text.split()
    print("words ", len(words))
    text = all_text

def summarize_text(text):
    words = text.split()
    max_chunk_size = 400  
    summarized_text = ""
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i+max_chunk_size])
        summary = summarizer(chunk)[0]['summary_text']
        summarized_text += summary + " "
    return summarized_text

# print(summarize_text(text))
res=summarize_text(text)
with open('summarised.txt','a') as file:
    file.write(res)

length = len(res)
print("length summ ", length)
words = res.split()
print("words summ ", len(words))
