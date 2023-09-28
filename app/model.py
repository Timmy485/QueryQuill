import csv
import json
from sentence_transformers import SentenceTransformer


def generate_embeddings_and_save(csv_input_path, csv_output_path, save_csv=True):
    # Load the model
    model = SentenceTransformer('paraphrase-distilroberta-base-v1')
    
    if save_csv:
        with open(csv_input_path, "r", encoding="utf-8") as csvfile, open(csv_output_path, "w", newline='', encoding="utf-8") as outfile:
            reader = csv.DictReader(csvfile)
            fieldnames = ["Passage", "Metadata", "Embedding"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                passage = row["Passage"]
                metadata = row["Metadata"]
                embedding = model.encode(passage, convert_to_tensor=True).tolist()
                
                writer.writerow({
                    "Passage": passage,
                    "Metadata": metadata,
                    "Embedding": embedding
                })
            print(f"Successfully generated {csv_output_path}")
    return model