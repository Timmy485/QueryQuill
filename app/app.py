import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from indexing import connect_instance, create_index, index_data_to_elasticsearch
from gen_ai import generate_direct_answer_with_llama
from retrieval import search_relevant_passages, search_similar_passages, save_results_to_csv
from flask import Flask, request, jsonify

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


@app.route('/ask', methods=['POST'])
def ask():
    # Extract the user question from the request
    question = request.json.get('question', '')

    # Convert the question into an embedding
    question_embedding = model.encode(question)

    # Search for relevant passages using the provided functions
    search_results = search_relevant_passages(es, "passage_metadata_emb", question_embedding)

    # Extract the top passages and their metadata from the search results
    passages = [hit["_source"]["Passage"] for hit in search_results]
    metadata = [hit["_source"]["Metadata"] for hit in search_results]

    gen_ai_output = generate_direct_answer_with_llama(search_results, question, save_csv=False)

    return jsonify({'answer': passages, 'metadata': metadata})

if __name__ == "__main__":
    app.run(debug=True)