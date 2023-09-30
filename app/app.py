import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from indexing import connect_instance, create_index, index_data_to_elasticsearch
from gen_ai import generate_direct_answer_with_palm
from model import generate_embeddings_and_save
from parsing import process_folder
from retrieval import search_similar_passages, save_results_to_csv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Initialize the SentenceTransformer model for embeddings
model = SentenceTransformer('paraphrase-distilroberta-base-v1')

# Retrieve environment variables for connecting to Elasticsearch
es_host = os.environ.get("ES_HOST")
es_port = int(os.environ.get("ES_PORT"))
es_username = os.environ.get("ES_USERNAME")
es_password = os.environ.get("ES_PASSWORD")

# Connect to the remote Elasticsearch instance
es = connect_instance(es_host, es_port, es_username, es_password)

# Configuration for file uploads
UPLOAD_FOLDER = '../docs/corpus'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure UPLOAD_FOLDER exists, if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print("created folder")


@app.route('/ask', methods=['POST'])
def ask():
    """
    API endpoint to retrieve answers for a given question.
    
    Returns:
        json: A JSON object containing the top relevant answers, metadata, and AI-generated answer.
    """
    # Extract the user question from the request
    question = request.json.get('question', '')

    # Convert the question into an embedding
    question_embedding = model.encode(question)

    # Search for relevant passages using the provided functions
    search_results = search_similar_passages(es, "passage_metadata_emb", question_embedding)

    # Extract the top passages and their metadata from the search results
    passages = [hit["_source"]["Passage"] for hit in search_results]
    metadata = [hit["_source"]["Metadata"] for hit in search_results]
    scores = [hit["_score"] for hit in search_results]
    
    # Generate AI-enhanced answer
    gen_ai_output = generate_direct_answer_with_palm(search_results, question, save_csv=False)

    return jsonify({'answer': passages, 'relevance_socres': scores,'metadata': metadata, 'gen_ai_output': gen_ai_output})


def save_file(file, extension):
    """
    Saves a file to the UPLOAD_FOLDER directory.
    
    Args:
        file (FileStorage): The file to save.
        extension (str): Expected file extension.
    
    Returns:
        str: Path to the saved file or None if the file type is incorrect.
    """
    if not file.filename.endswith(extension):
        return None
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath

@app.route('/upload', methods=['POST'])
def upload_and_query():
    """
    API endpoint to upload text and JSON files, and retrieve answers for a given question.
    
    Returns:
        json: A JSON object containing the top relevant answers, metadata, and AI-generated answer.
    """
    # Extract the user question and files from the request
    question = request.form.get('question', '')
    txt_file = request.files.get('txt_file', None)
    json_file = request.files.get('json_file', None)

    # Validate the presence of both files and the question
    if not txt_file or not json_file or not question:
        return jsonify({'error': 'Both .txt and .json files along with a query are required'}), 400
    
    # Save the files to the UPLOAD_FOLDER
    txt_filepath = save_file(txt_file, '.txt')
    json_filepath = save_file(json_file, '.json')

    # Validate the saved files
    if not txt_filepath or not json_filepath:
        return jsonify({'error': 'Invalid file types. Please provide a .txt and a .json file'}), 400
    
    # Process and index the data to Elasticsearch
    process_folder(UPLOAD_FOLDER, "../docs")
    generate_embeddings_and_save("../docs/passage_metadata.csv", "../docs/passage_metadata_emb.csv")
    index_data_to_elasticsearch(es, "../docs/passage_metadata_emb.csv", index_name="temp" )
    
    # Convert the question into an embedding
    question_embedding = model.encode(question)  

    # Search for relevant passages using the provided functions
    search_results = search_similar_passages(es, "temp", question_embedding)

    # Extract the top passages and their metadata from the search results
    passages = [hit["_source"]["Passage"] for hit in search_results]
    scores = [hit["_score"] for hit in search_results]
    metadata = [hit["_source"]["Metadata"] for hit in search_results]

    # Generate AI-enhanced answer
    gen_ai_output = generate_direct_answer_with_palm(search_results, question, save_csv=False)

    return jsonify({'answer': passages, 'relevance_socres': scores, 'metadata': metadata, 'gen_ai_output': gen_ai_output})


@app.route('/reset_index', methods=['POST'])
def reset_index():
    """
    API endpoint to reset the Elasticsearch index.
    
    Returns:
        json: A JSON object indicating success or failure.
    """
    try:
        # Delete and recreate the Elasticsearch index
        if es.indices.exists(index='temp'):
            es.indices.delete(index='temp')
        
        create_index(es, "temp")
        
        return jsonify({'success': 'Index reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to reset index. Error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
