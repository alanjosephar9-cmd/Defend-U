import spacy
import json
import os

nlp = spacy.load("en_core_web_sm")

data = []

if __name__ == "__main__":
    text_folder = "../data/extracted_text"
    
    if not os.path.exists(text_folder):
        print(f"Error: {text_folder} not found.")
    else:
        for file in os.listdir(text_folder):
            with open(os.path.join(text_folder, file), encoding="utf-8") as f:
                text = f.read()

            doc = nlp(text)

            for sent in doc.sents:
                s = sent.text.strip()
                if len(s) > 20:   # remove tiny useless lines
                    data.append({
                        "case": file,
                        "sentence": s
                    })

        with open("../data/sentences.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print("Sentence dataset created:", len(data), "sentences")
