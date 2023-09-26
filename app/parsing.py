import os
import csv
import json

def process_folder(folder_path):
    """
    Process a folder containing pairs of .txt and .json files. Extract passages from the .txt files, 
    metadata from the .json files, and write pairings to a CSV file.
    
    Args:
    - folder_path (str): Path to the folder containing the files.
    
    Returns:
    - str: Path to the generated CSV file.
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
        refined_paragraphs = []
        for section in sections_list:
            paragraphs_in_section = section.split("__paragraph__")[1:]  # Ignoring text before the first __paragraph__ marker
            refined_paragraphs.extend([p.strip() for p in paragraphs_in_section if p.strip()])
        combined_passage_refined = " ".join(refined_paragraphs)

        # Splitting the combined passage into chunks of 5 sentences each
        sentences_refined = combined_passage_refined.split('. ')
        chunks_of_five_sentences_refined = []
        temp_chunk_refined = []
        for sentence in sentences_refined:
            temp_chunk_refined.append(sentence)
            if len(temp_chunk_refined) == 5:
                chunks_of_five_sentences_refined.append(". ".join(temp_chunk_refined) + ".")
                temp_chunk_refined = []

        # Adding any remaining sentences to the last chunk        
        if temp_chunk_refined:
            chunks_of_five_sentences_refined.append(". ".join(temp_chunk_refined) + ".")
        
        # Extract metadata from .json file
        with open(os.path.join(folder_path, json_file), "r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        
        # Create pairings of passages and metadata
        for passage in chunks_of_five_sentences_refined:
            all_pairings.append({"Passage": passage, "Metadata": json.dumps(metadata)})
    
    # Write all_pairings to a CSV file
    csv_filename = os.path.join(folder_path, "passage_metadata.csv")
    with open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["Passage", "Metadata"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pairing in all_pairings:
            writer.writerow(pairing)
    
    return csv_filename