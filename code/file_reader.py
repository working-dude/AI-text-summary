import time
import os
# calculating time to read a pdf using pdfplumber to extract text from PDF files


def find_model_folders(base_folder):
    model_folders = []
    for root, dirs, files in os.walk(base_folder):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if 'model.safetensors' in os.listdir(dir_path):
                model_folders.append(dir_path)
    return model_folders


start_time = time.time()
base_folder = "."
model_folders = find_model_folders(base_folder)
print("Model folders found:")
for folder in model_folders:
    print(folder)
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")