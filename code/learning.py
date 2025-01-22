# # import multiprocessing as mp
# # import time
# # import math

# # def square(x):
# #     return math.sqrt(pow(x, 2))

# # if __name__ == "__main__":
# #     for i in range(1, 6):
# #         start = time.time()
# #         with mp.Pool(processes=i) as pool:
# #             results = pool.map(square, range(50000000))
# #         end = time.time()
# #         print(f"Time taken with {i} processeor: {end - start:.2f} seconds")
# #         # print(results)

# # def generate_numbers(n):
# #     for i in range(n+1):
# #         if i % 2 == 0:
# #             yield i
# #         else:
# #             yield i * 3

# # # Debugging the generator can be more complex due to the stateful nature
# # for number in generate_numbers(5):
# #     print(number)

# import torch
# from transformers import pipeline, AutoTokenizer
# import pdfplumber
# import docx
# from concurrent.futures import ThreadPoolExecutor

# # Define model and device
# model_name = "sshleifer/distilbart-xsum-12-6"
# device = 0 if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_built() else -1)
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# summarizer = pipeline("summarization", model=model_name, device=device)

       

# def summarize_text_incrementally_generator(text):
#     """Generates summarized chunks incrementally."""
#     max_input_length = 1024  # Model's token limit
#     words = text.split()
#     print(f"Total words: {len(words)}")
#     max_chunk_size = len(words) // 4  # Increase chunk size for better performance
#     # Split text into chunks of max_chunk_size words
#     chunks = [" ".join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
#     print(f"Total chunks: {len(chunks)}")

#     # Merge chunks with less than 50 tokens with the previous chunk
#     i = len(chunks) - 1
#     while i > 0:
#         inputs = tokenizer(chunks[i], return_tensors="pt", truncation=False)
#         input_ids = inputs["input_ids"]
#         token_count = input_ids.shape[1]
#         if token_count < 50:
#             if i > 0:
#                 chunks[i - 1] += " " + chunks.pop(i)
#         i -= 1

#     for i in range(len(chunks)):
#         print(f"Processing chunk {i + 1} of {len(chunks[i])}")
#         inputs = tokenizer(chunks[i], return_tensors="pt", truncation=False)
#         input_ids = inputs["input_ids"]
#         token_count = input_ids.shape[1]
#         print(f"Chunk size: {token_count} tokens")

# with pdfplumber.open("ml.pdf") as pdf:
#                 for page in pdf.pages:
#                     text = ""
#                     for i, page in enumerate(pdf.pages):
#                         page_text = page.extract_text()
#                         if page_text:
#                             text += page_text
#                         if (i + 1) % 3 == 0:
#                             summarize_text_incrementally_generator(text)
#                             text = ""
#                     if text:  # Summarize any remaining text
#                          summarize_text_incrementally_generator(text)

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
        print(f"Processing chunk: {chunk}")
        max_input_length = 1024  # Maximum input length for the model
        if len(chunk.split()) > max_input_length:
            sub_chunks = [" ".join(chunk.split()[i:i+max_input_length]) for i in range(0, len(chunk.split()), max_input_length)]
            summaries = [summarizer(sub_chunk)[0]['summary_text'] for sub_chunk in sub_chunks]
            return " ".join(summaries)
        else:
            print(f"Splitting chunk into {len(chunk)} sub-chunks.")
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
    print(f"Reading file: {file_path}")
    try:
        # Handle PDF files
        if file_type == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    print(f"Processing page {page.page_number}...")
                    print(page_text)
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

if __name__ == "__main__":
    file_path = "ml.pdf"
    summarize_file_incrementally(file_path)
    count=0
    for summary in summarize_file_incrementally(file_path):
        count+=1
    print(count)