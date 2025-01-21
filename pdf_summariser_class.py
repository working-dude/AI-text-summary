import os
import torch
from transformers import pipeline
import pdfplumber
import docx
from concurrent.futures import ThreadPoolExecutor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from textwrap import wrap
import language_tool_python
import sys

class PDFSummarizer:
    def __init__(self, model_name="models"):
        try:
            # Define model and device (CUDA, CPU, or MPS for Apple Silicon)
            self.device = 0 if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_built() else -1)  # Use GPU if available, MPS for Apple M1/M2, else CPU

            # Log device information
            print(f"Using device: {'CUDA' if self.device == 0 else 'CPU'}")
            
            # Adjust model path if running from a PyInstaller bundle
            if getattr(sys, 'frozen', False):
                model_name = os.path.join(sys._MEIPASS, model_name)

            # Load the summarizer once, based on platform and device
            self.summarizer = pipeline("summarization", model=model_name, device=self.device)
            self.tool = language_tool_python.LanguageTool('en-US')  # For British English, use 'en-GB'
        except Exception as e:
            print(f"Error initializing PDFSummarizer: {e}")
            raise e  # Re-raise exception to be caught in InitializationThread

    def find_model_folders(self, base_folder):
        if getattr(sys, 'frozen', False):
            base_folder = os.path.join(sys._MEIPASS, base_folder)
        model_folders = []
        for root, dirs, files in os.walk(base_folder):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if 'model.safetensors' in os.listdir(dir_path):
                    model_folders.append(dir_path)
        return model_folders

    @staticmethod
    def list_available_models(base_folder="."):
        if getattr(sys, 'frozen', False):
            base_folder = os.path.join(sys._MEIPASS, base_folder)
        summarizer = PDFSummarizer()
        return summarizer.find_model_folders(base_folder)

    def summarize_chunk(self, chunk, summary_length='medium'):
        """Summarizes a single chunk of text."""
        try:
            length = len(chunk.split())
            max_input_length = 1024  # Maximum input length for the model

            if summary_length == 'small':
                min_summary_length = length // 5
                max_summary_length = length // 3
            elif summary_length == 'large':
                min_summary_length = length // 2
                max_summary_length = length
            else:  # medium
                min_summary_length = length // 3
                max_summary_length = length // 2

            print(f"min_summary_length: {min_summary_length}, max_summary_length: {max_summary_length}")
            chunk_words = chunk.split()
            if len(chunk_words) > max_input_length:
                sub_chunks = [" ".join(chunk_words[i:i + len(chunk_words) // 2]) for i in range(0, len(chunk_words), len(chunk_words) // 2)]
                summaries = [self.summarizer(sub_chunk, max_length=max_summary_length, min_length=min_summary_length)[0]['summary_text'] for sub_chunk in sub_chunks]
                print(f"Splitting chunk into {len(sub_chunks)} sub-chunks.")
                return " ".join(summaries)
            else:
                return self.summarizer(chunk, max_length=max_summary_length, min_length=min_summary_length)[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            return ""

    def summarize_text_incrementally_generator(self, text, summary_length='medium'):
        """Generates summarized chunks incrementally."""
        words = text.split()
        max_chunk_size = 400  # Adjust chunk size for performance
        print("words", len(words))
        # Split text into chunks of max_chunk_size words
        chunks = [" ".join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]

        # Process chunks using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda chunk: self.summarize_chunk(chunk, summary_length), chunks)
            for result in results:
                yield result  # Yield each summarized chunk as it's completed

    def summarize_file_incrementally(self, file_path, summary_length='medium'):
        """Generates summaries incrementally from a file (PDF, DOCX, TXT)."""
        file_type = file_path.split('.')[-1].lower()

        try:
            # Handle PDF files
            if file_type == 'pdf':
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            yield from self.summarize_text_incrementally_generator(page_text, summary_length)

            # Handle DOCX files
            elif file_type == 'docx':
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    para_text = para.text
                    if para_text:
                        yield from self.summarize_text_incrementally_generator(para_text, summary_length)

            # Handle TXT files
            elif file_type == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    while True:
                        chunk = f.read(2048)  # Read in chunks of 2048 characters
                        if not chunk:
                            break
                        yield from self.summarize_text_incrementally_generator(chunk, summary_length)

            else:
                yield "Unsupported file format."

        except Exception as e:
            print(f"Error reading file: {e}")
            yield f"Error reading file: {e}"

    def summarize_folder(self, folder_path):
        summaries = {}
        for filename in os.listdir(folder_path):
            print(f"Summarizing {filename}...")
            file_path = os.path.join(folder_path, filename)
            for summary in self.summarize_file_incrementally(file_path):
                print(summary)
                summaries[filename] = summaries.get(filename, []) + [summary]
        return summaries

    def summarize_folder_to_pdf(self, folder_path, output_file_path, header, image_path=None):
        summaries = self.summarize_folder(folder_path)
        combined_text = "\n".join(["\n".join(summaries[filename]) for filename in summaries])
        corrected_text = self.correct_grammar(combined_text)
        self.create_beautiful_pdf(output_file_path, corrected_text, header, image_path)

    def create_beautiful_pdf(self, file_path, text, header, image_path=None):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Add header
        c.setFont("Helvetica-Bold", 18)
        c.setFillColorRGB(0.2, 0.4, 0.8)  # Set color for the header
        c.drawString(1 * inch, height - 1 * inch, header)

        # Optionally add an image
        if image_path:
            c.drawImage(image_path, width - 3 * inch, height - 2 * inch, width=2 * inch, height=2 * inch)

        # Add content text
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0, 0, 0)  # Set text color
        y_position = height - 2 * inch  # Start below header and image
        max_width = 85  # Adjust for text wrapping

        for paragraph in text.split("\n\n"):  # Treat double newlines as paragraph breaks
            for line in wrap(paragraph, max_width):
                if y_position < 1 * inch:  # If reaching the bottom of the page
                    c.showPage()  # Add a new page
                    y_position = height - 1 * inch  # Reset position for new page
                    c.setFont("Helvetica", 12)  # Re-set font for the new page
                c.drawString(1 * inch, y_position, line)
                y_position -= 0.3 * inch  # Adjust line spacing

        # Add footer
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray color for footer
        c.drawString(1 * inch, 0.5 * inch, "Generated by AI Text Summarizer")
        c.save()
        # n = int(input("Do you want to download the file? 1 for yes, 0 for no: "))
        # if n == 1:
        #     c.save()
        # else:
        #     print("File not saved")

    def correct_grammar(self, text):
        """
        Corrects the grammar of a given text using LanguageTool.
        :param text: String to be corrected
        :return: Corrected string
        """
        corrected_text = self.tool.correct(text)
        return corrected_text



# if __name__ == "__main__":
#     folder_path = "ml.pdf"  # Update this path to your file
#     import time
#     start = time.time()
#     summaries = list(summarize_file_incrementally(folder_path))  # Generate summaries incrementally
#     end = time.time()
#     print(f"Time taken: {end - start:.2f} seconds")
#     # Correct grammar for each summary
#     start = time.time()
#     summaries = [correct_grammar(summary) for summary in summaries]
#     end = time.time()
#     # Combine corrected summaries into one text
#     text = "\n".join(summaries)
#     print(f"Time taken for grammar correction: {end - start:.2f} seconds")
#     # Create the final beautified PDF
#     # file_path = "output.pdf"
#     # header = "Summarized and Corrected Files"
#     # image_path = None  # Optional: Add image if needed
#     # create_beautiful_pdf(file_path, text, header, image_path)
