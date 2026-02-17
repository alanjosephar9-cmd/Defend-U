import pytesseract
from PIL import Image
import os
import sys

# Set default tesseract path for Windows if not in PATH
# Common default installation paths
possible_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\AppData\Local\Tesseract-OCR\tesseract.exe"
]

for path in possible_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

def extract_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except pytesseract.TesseractNotFoundError:
        return "Error: Tesseract OCR is not installed or not found in PATH. Please install Tesseract."
    except Exception as e:
        return f"Error reading image: {str(e)}"
