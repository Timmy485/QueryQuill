import csv
from sentence_transformers import SentenceTransformer

def generate_embeddings_and_save(csv_input_path, csv_output_path, save_csv=True):
    """
    Generate embeddings for passages from a CSV file and optionally save the embeddings to another CSV file.

    Args:
        csv_input_path (str): Path to the CSV file containing the passages and metadata.
        csv_output_path (str): Path to the CSV file where the passages, metadata, and embeddings will be saved.
        save_csv (bool, optional): Flag indicating if the embeddings should be saved to a CSV file. Defaults to True.

    Returns:
        SentenceTransformer: The SentenceTransformer model used for generating embeddings.
    """
    
    # Load the SentenceTransformer model
    model = SentenceTransformer('paraphrase-distilroberta-base-v1')
    
    # If save_csv is True, read the input CSV, generate embeddings, and write to the output CSV
    if save_csv:
        with open(csv_input_path, "r", encoding="utf-8") as csvfile, open(csv_output_path, "w", newline='', encoding="utf-8") as outfile:
            reader = csv.DictReader(csvfile)
            
            # Define the columns for the output CSV
            fieldnames = ["Passage", "Metadata", "Embedding"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                passage = row["Passage"]
                metadata = row["Metadata"]
                
                # Generate embedding for the passage
                embedding = model.encode(passage, convert_to_tensor=True).tolist()
                
                # Write the passage, metadata, and embedding to the output CSV
                writer.writerow({
                    "Passage": passage,
                    "Metadata": metadata,
                    "Embedding": embedding
                })
            
            print(f"Successfully generated {csv_output_path}")
    
    return model
