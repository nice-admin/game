from PIL import Image
import os

# Set the target size
target_size = (60, 60)

# Get the current directory
current_directory = os.getcwd()
print(f"Scanning folder: {current_directory}")

# Track if any files were processed
found_png = False

# Loop through all files in the directory
for filename in os.listdir(current_directory):
    if filename.lower().endswith(".png"):
        found_png = True
        filepath = os.path.join(current_directory, filename)
        print(f"Processing file: {filename}")
        try:
            with Image.open(filepath) as img:
                resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                resized_img.save(filepath)  # Overwrite the original file
                print(f"Resized {filename} to 100x100 pixels.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if not found_png:
    print("No PNG files found in this folder.")
