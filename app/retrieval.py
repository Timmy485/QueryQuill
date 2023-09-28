import csv

def search_similar_passages(es_instance, index_name, query_embedding, top_n=3):
    # Use the script_score method to compute the cosine similarity
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
    search_results = search_similar_passages(es, index_name, query_embedding)
    return search_results


# Function to save results to CSV
def save_results_to_csv(query, search_results, csv_file_path="questions_answers.csv"):
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", 
                         "Passage 1", "Relevance Score 1", "Passage 1 Metadata", 
                         "Passage 2", "Relevance Score 2", "Passage 2 Metadata", 
                         "Passage 3", "Relevance Score 3", "Passage 3 Metadata"])
        
        row = [query]
        for hit in search_results:
            row.extend([hit["_source"]["Passage"], hit["_score"], hit["_source"]["Metadata"]])
        writer.writerow(row)




