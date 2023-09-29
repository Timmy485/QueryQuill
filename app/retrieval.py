import csv

def search_similar_passages(es_instance, index_name, query_embedding, top_n=5):
    """
    Search for passages in the Elasticsearch index that are similar to the provided query embedding.
    
    Args:
    - es_instance (Elasticsearch): An instance of the Elasticsearch client.
    - index_name (str): The name of the Elasticsearch index to search in.
    - query_embedding (list): The embedding vector of the user's query.
    - top_n (int, optional): The number of top results to retrieve. Defaults to 3.
    
    Returns:
    - list: List of top search results.
    """
    
    # Construct the Elasticsearch query to compute cosine similarity
    query_body = {
        "size": top_n,
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'Embedding') + 1.0",
                    "params": {
                        "query_vector": query_embedding
                    }
                }
            }
        }
    }
    
    response = es_instance.search(index=index_name, body=query_body)
    return response['hits']['hits']


def search_relevant_passages(es, index_name, query_embedding):
    """
    Wrapper function to search for relevant passages.
    
    Args:
    - es (Elasticsearch): An instance of the Elasticsearch client.
    - index_name (str): The name of the Elasticsearch index to search in.
    - query_embedding (list): The embedding vector of the user's query.
    
    Returns:
    - list: List of search results.
    """
    
    return search_similar_passages(es, index_name, query_embedding)


def save_results_to_csv(query, search_results, csv_file_path="questions_answers.csv"):
    """
    Save the search results to a CSV file.
    
    Args:
    - query (str): The user's query.
    - search_results (list): List of search results.
    - csv_file_path (str, optional): Path to the CSV file where the results will be saved. Defaults to "questions_answers.csv".
    
    Returns:
    - None
    """
    
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write headers to the CSV
        writer.writerow(["Question", 
                         "Passage 1", "Relevance Score 1", "Passage 1 Metadata", 
                         "Passage 2", "Relevance Score 2", "Passage 2 Metadata", 
                         "Passage 3", "Relevance Score 3", "Passage 3 Metadata"])
        
        # Extract and write the search results to the CSV
        row = [query]
        for hit in search_results:
            row.extend([hit["_source"]["Passage"], hit["_score"], hit["_source"]["Metadata"]])
        writer.writerow(row)
