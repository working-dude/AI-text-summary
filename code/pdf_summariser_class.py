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
import sys

class PDFSummarizer:
    """
    A class to summarize text from PDF, DOCX, and TXT files using a pre-trained model.
    """

    def __init__(self, model_name="model"):
        """
        Initializes the PDFSummarizer with the specified model.

        :param model_name: The name or path of the model to use for summarization.
        """
        try:
            # Define model and device (CUDA, CPU, or MPS for Apple Silicon)
            self.device = 0 if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_built() else -1)
            print(f"Using device: {'CUDA' if self.device == 0 else 'CPU'}")

            # Adjust model path if running from a PyInstaller bundle
            base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base, model_name)

            # Load the summarizer
            self.summarizer = pipeline("summarization", model=model_path, device=self.device)
        except Exception as e:
            print(f"Error initializing PDFSummarizer: {e}")
            raise e

    def find_model_folders(self, base_folder):
        """
        Finds folders containing model files.

        :param base_folder: The base folder to search for model files.
        :return: A list of folders containing model files.
        """
        if getattr(sys, 'frozen', False):
            base_folder = os.path.dirname(sys.executable)
        
        model_folders = []
        for root, dirs, files in os.walk(base_folder):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if 'model.safetensors' in os.listdir(dir_path):
                    model_folders.append(dir_path)
        return model_folders

    @staticmethod
    def list_available_models(base_folder="."):
        """
        Lists available models in the specified base folder.

        :param base_folder: The base folder to search for models.
        :return: A list of available model folders.
        """
        if getattr(sys, 'frozen', False):
            base_folder = os.path.dirname(sys.executable)
        
        summarizer = PDFSummarizer()
        return summarizer.find_model_folders(base_folder)

    def summarize_chunk(self, chunk, summary_length='medium'):
        """
        Summarizes a single chunk of text.

        :param chunk: The text chunk to summarize.
        :param summary_length: The desired length of the summary ('small', 'medium', 'large').
        :return: The summarized text.
        """
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
        """
        Generates summarized chunks incrementally.

        :param text: The text to summarize.
        :param summary_length: The desired length of the summary ('small', 'medium', 'large').
        :yield: Summarized chunks of text.
        """
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
        """
        Generates summaries incrementally from a file (PDF, DOCX, TXT).

        :param file_path: The path to the file to summarize.
        :param summary_length: The desired length of the summary ('small', 'medium', 'large').
        :yield: Summarized chunks of text.
        """
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
        """
        Summarizes all files in a folder.

        :param folder_path: The path to the folder containing files to summarize.
        :return: A dictionary with filenames as keys and lists of summarized text as values.
        """
        summaries = {}
        for filename in os.listdir(folder_path):
            print(f"Summarizing {filename}...")
            file_path = os.path.join(folder_path, filename)
            for summary in self.summarize_file_incrementally(file_path):
                print(summary)
                summaries[filename] = summaries.get(filename, []) + [summary]
        return summaries

    def summarize_folder_to_pdf(self, folder_path, output_file_path, header, image_path=None):
        """
        Summarizes all files in a folder and saves the combined summary to a PDF.

        :param folder_path: The path to the folder containing files to summarize.
        :param output_file_path: The path to save the output PDF.
        :param header: The header text for the PDF.
        :param image_path: Optional path to an image to include in the PDF.
        """
        summaries = self.summarize_folder(folder_path)
        combined_text = "\n".join(["\n".join(summaries[filename]) for filename in summaries])
        corrected_text = self.correct_grammar(combined_text)
        self.create_beautiful_pdf(output_file_path, corrected_text, header, image_path)

    def create_beautiful_pdf(self, file_path, text, header, image_path=None):
        """
        Creates a PDF with the given text, header, and optional image.

        :param file_path: The path to save the PDF.
        :param text: The text content for the PDF.
        :param header: The header text for the PDF.
        :param image_path: Optional path to an image to include in the PDF.
        """
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

    def correct_grammar(self, text):
        """
        Corrects the grammar of a given text using LanguageTool.

        :param text: The text to be corrected.
        :return: The corrected text.
        """
        corrected_text = self.tool.correct(text)
        return corrected_text
