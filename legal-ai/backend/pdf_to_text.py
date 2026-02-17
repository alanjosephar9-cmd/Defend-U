import fitz
import os

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if __name__ == "__main__":
    pdf_folder = "../data/raw_pdfs"
    out_folder = "../data/extracted_text"

    os.makedirs(out_folder, exist_ok=True)

    if not os.path.exists(pdf_folder):
        print(f"Error: {pdf_folder} not found.")
    else:
        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                print("Reading:", file)
                text = extract_text(os.path.join(pdf_folder, file))
                with open(f"{out_folder}/{file.replace('.pdf','.txt')}", "w", encoding="utf-8") as f:
                    f.write(text)

        print("PDF extraction completed")
