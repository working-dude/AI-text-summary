from pdf_summariser_class import PDFSummarizer

# Initialize the summarizer with a different model
summarizer = PDFSummarizer(model_name="facebook/bart-large-cnn")

# Example usage: Summarize a PDF file incrementally
file_path = "Geometry _ Module (Only PDF) __ IOQM 2024.pdf"  # Update this path to your PDF file
summaries = list(summarizer.summarize_file_incrementally(file_path))

# Correct grammar for each summary
corrected_summaries = [summarizer.correct_grammar(summary) for summary in summaries]

# Combine corrected summaries into one text
final_text = "\n".join(corrected_summaries)

# Create the final beautified PDF
output_file_path = "output.pdf"
header = "Summarized and Corrected Text"
image_path = None  # Optional: Add image if needed
summarizer.create_beautiful_pdf(output_file_path, final_text, header, image_path)
