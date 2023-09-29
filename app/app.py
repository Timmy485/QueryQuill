import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from indexing import connect_instance, create_index, index_data_to_elasticsearch
from gen_ai import generate_direct_answer_with_llama
from model import generate_embeddings_and_save
from parsing import process_folder
from retrieval import search_relevant_passages, search_similar_passages, save_results_to_csv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Initialize the SentenceTransformer model
model = SentenceTransformer('paraphrase-distilroberta-base-v1')  # Replace with your chosen model name

# Load environment variables
es_host = os.environ.get("ES_HOST")
es_port = int(os.environ.get("ES_PORT"))
es_username = os.environ.get("ES_USERNAME")
es_password = os.environ.get("ES_PASSWORD")

# Connect to the remote Elasticsearch instance
es = connect_instance(es_host, es_port, es_username, es_password)


UPLOAD_FOLDER = '../docs/corpus'  # Directory to save uploaded files. 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Check if UPLOAD_FOLDER exists, and if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/ask', methods=['POST'])
def ask():
    # # Extract the user question from the request
    # question = request.json.get('question', '')

    # # Convert the question into an embedding
    # question_embedding = model.encode(question)

    # # Search for relevant passages using the provided functions
    # search_results = search_relevant_passages(es, "passage_metadata_emb", question_embedding)

    # # Extract the top passages and their metadata from the search results
    # passages = [hit["_source"]["Passage"] for hit in search_results]
    # metadata = [hit["_source"]["Metadata"] for hit in search_results]
    
    # #produce gen_ai result
    # gen_ai_output = generate_direct_answer_with_llama(search_results, question, save_csv=False)

    # return jsonify({'answer': passages, 'metadata': metadata, 'gen_ai_output': gen_ai_output})
    return jsonify({'status': 'success'}), 200




def save_file(file, extension):
    if not file.filename.endswith(extension):
        return None
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath

@app.route('/upload', methods=['POST'])
def upload_and_query():
    # Extract the user question from the request
    question = request.form.get('question', '')
    txt_file = request.files.get('txt_file', None)
    json_file = request.files.get('json_file', None)

    # Check if both files and the question are present
    if not txt_file or not json_file or not question:
        return jsonify({'error': 'Both .txt and .json files along with a query are required'}), 400
    
    # Save the files
    txt_filepath = save_file(txt_file, '.txt')
    json_filepath = save_file(json_file, '.json')

    if not txt_filepath or not json_filepath:
        return jsonify({'error': 'Invalid file types. Please provide a .txt and a .json file'}), 400
    
    # Process the files, extract data, and index to Elasticsearch
    process_folder(UPLOAD_FOLDER, "../docs")
    generate_embeddings_and_save("../docs/passage_metadata.csv", "../docs/passage_metadata_emb.csv")
    index_data_to_elasticsearch(es, "../docs/passage_metadata_emb.csv", index_name="temp" )
    
    
    # Convert the question into an embedding
    question_embedding = model.encode(question)  

    # Search for relevant passages using the provided functions
    search_results = search_relevant_passages(es, "temp", question_embedding)

    # Extract the top passages and their metadata from the search results
    passages = [hit["_source"]["Passage"] for hit in search_results]
    metadata = [hit["_source"]["Metadata"] for hit in search_results]

    # Produce gen_ai result
    gen_ai_output = generate_direct_answer_with_llama(search_results, question, save_csv=False)

    return jsonify({'answer': passages, 'metadata': metadata, 'gen_ai_output': gen_ai_output})



@app.route('/reset_index', methods=['POST'])
def reset_index():
    try:
        # Delete the index if it exists
        if es.indices.exists(index='temp'):
            es.indices.delete(index='temp')
        
        # Recreate the index
        create_index(es, "temp")
        
        return jsonify({'success': 'Index reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to reset index. Error: {str(e)}'}), 500



if __name__ == "__main__":
    app.run(debug=True)