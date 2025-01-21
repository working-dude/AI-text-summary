# import streamlit as st # type: ignore
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def pdf_read(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

def vector_store(text_chunks):
    embeddings = model.encode(text_chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    faiss.write_index(index, "faiss_index")

def summarize_pdf(pdf_doc):
    raw_text = pdf_read(pdf_doc)
    text_chunks = get_chunks(raw_text)
    vector_store(text_chunks)
    summary = " ".join(text_chunks[:5])  # Example: taking the first 5 chunks as summary
    return summary.replace("\n", " ")

def upload_pdf_and_process(pdf_doc=None):
    if pdf_doc:
        print("Processing PDF...")
        summary = summarize_pdf(pdf_doc)
        print("Summary:")
        print(summary)
        with open("summary.txt", "w") as f:
            f.write(summary)

# Example usage
upload_pdf_and_process("ml.pdf")