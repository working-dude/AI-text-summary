import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
import time
import torch
from transformers import pipeline
import pdfplumber
import docx
from concurrent.futures import ThreadPoolExecutor

# Define model and device (CUDA, CPU, or MPS for Apple Silicon)
model_name = "sshleifer/distilbart-xsum-12-6"
device = 0 if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_built() else -1)  # Use GPU if available, MPS for Apple M1/M2, else CPU

# Load the summarizer once, based on platform and device
summarizer = pipeline("summarization", model=model_name, device=device)

def summarize_chunk(chunk):
    """Summarizes a single chunk of text."""
    try:
        max_input_length = 1024  # Maximum input length for the model
        chunk_words = chunk.split()
        if len(chunk_words) > max_input_length:
            sub_chunks = [" ".join(chunk_words[i:i+max_input_length]) for i in range(0, len(chunk_words), max_input_length)]
            summaries = [summarizer(sub_chunk,min_length=100, max_length=300)[0]['summary_text'] for sub_chunk in sub_chunks]
            return " ".join(summaries)
        else:
            return summarizer(chunk,min_length=100, max_length=300)[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing chunk: {e}")
        return ""

def summarize_text_incrementally_generator(text):
    """Generates summarized chunks incrementally."""
    words = text.split()
    max_chunk_size = 400  # Adjust chunk size for performance
    # print("words", len(words))
    # Split text into chunks of max_chunk_size words
    chunks = [" ".join(words[i:i+max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
    print("chunks", len(chunks))
    for chunk in chunks:
        print(len(chunk))
    # Process chunks using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        results = executor.map(summarize_chunk, chunks)
        for result in results:
            yield result  # Yield each summarized chunk as it's completed

def summarize_file_incrementally(file_path):
    """Generates summaries incrementally from a file (PDF, DOCX, TXT)."""
    file_type = file_path.split('.')[-1].lower()

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
            for para in doc.paragraphs:
                para_text = para.text
                if para_text:
                    yield from summarize_text_incrementally_generator(para_text)

        # Handle TXT files
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                while True:
                    chunk = f.read(2048)  # Read in chunks of 2048 characters
                    if not chunk:
                        break
                    yield from summarize_text_incrementally_generator(chunk)

        else:
            yield "Unsupported file format."

    except Exception as e:
        print(f"Error reading file: {e}")
        yield f"Error reading file: {e}"

if __name__ == "__main__":
    file_path = "output.txt"
    start_time = time.time()
    for summary in summarize_file_incrementally(file_path):
        print(summary)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")