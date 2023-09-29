import os
import csv
import json

def process_folder(folder_path, out_folder):
    """
    Process a folder containing pairs of .txt and .json files. Extract passages from the .txt files, 
    metadata from the .json files, and write pairings to a CSV file.
    
    Args:
        folder_path (str): Path to the folder containing the files.
        out_folder (str): Path to the output folder for saving the generated CSV.

    Returns:
        None
    """
    
    all_pairings = []
    
    # Get all .txt and .json files in the folder
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('_Technical.txt')]
    json_files = [f.replace('_Technical.txt', '_Metadata.json') for f in txt_files]

    for txt_file, json_file in zip(txt_files, json_files):
        
        # Extract passages from .txt file
        with open(os.path.join(folder_path, txt_file), "r", encoding="utf-8") as file:
            content = file.read()
        sections_list = [s.strip() for s in content.split("__section__") if s.strip()]
        
        # Split sections into paragraphs
        refined_paragraphs = []
        for section in sections_list:
            paragraphs = section.split("__paragraph__")[1:]
            refined_paragraphs.extend([p.strip() for p in paragraphs if p.strip()])
        
        # Combine paragraphs and split into sentences
        combined_passage = " ".join(refined_paragraphs)
        sentences = combined_passage.split('. ')
        
        # Create chunks of five sentences each
        chunks_of_five_sentences = [". ".join(sentences[i:i+5]) + "." for i in range(0, len(sentences), 5)]
        
        # Extract metadata from .json file
        with open(os.path.join(folder_path, json_file), "r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        
        # Create pairings of passages and metadata
        for passage in chunks_of_five_sentences:
            all_pairings.append({"Passage": passage, "Metadata": json.dumps(metadata)})
    
    # Write all_pairings to a CSV file
    csv_filename = os.path.join(out_folder, "passage_metadata.csv")
    with open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["Passage", "Metadata"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pairing in all_pairings:
            writer.writerow(pairing)

    print(f"Successfully generated {csv_filename}")

