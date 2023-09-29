from elasticsearch import Elasticsearch, helpers
import csv

def connect_instance(host, port, username, password, timeout=120):
    """
    Connect to an Elasticsearch instance.

    Args:
        host (str): The host of the Elasticsearch instance.
        port (int): The port number on which Elasticsearch is running.
        username (str): The username for Elasticsearch authentication.
        password (str): The password for Elasticsearch authentication.
        timeout (int, optional): The timeout for connecting. Defaults to 120.

    Returns:
        Elasticsearch: An Elasticsearch connection object if successful, otherwise None.
    """
    try:
        es = Elasticsearch(    
            hosts=[{
                'host': host,
                'port': port, 
                'scheme': 'https',
            }],
            http_auth=(username, password), 
            timeout=timeout
        )
        print("Connected to ES instance")
        return es
    except ConnectionError as e:
        print(f"Failed to connect to ES instance: {str(e)}")
        return None

def create_index(es_instance, index_name="passage_metadata_emb"):
    """
    Create an Elasticsearch index with specified mappings.

    Args:
        es_instance (Elasticsearch): The Elasticsearch connection object.
        index_name (str, optional): The name of the index to create. Defaults to "passage_metadata_emb".
    """
    mapping = {
        "mappings": {
            "properties": {
                "Passage": {"type": "text"},
                "Metadata": {"type": "text"},
                "Embedding": {"type": "dense_vector", "dims": 768}
            }
        }
    }
    
    es_instance.indices.create(index=index_name, body=mapping)

def index_data_to_elasticsearch(es_instance, csv_file_path, index_name="passage_metadata_emb"):
    """
    Index data from a CSV file to an Elasticsearch index.

    Args:
        es_instance (Elasticsearch): The Elasticsearch connection object.
        csv_file_path (str): Path to the CSV file containing the data.
        index_name (str, optional): The name of the index to which data will be indexed. Defaults to "passage_metadata_emb".
    """
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        actions = []
        for row in reader:
            action = {
                "_index": index_name,
                "_source": {
                    "Passage": row["Passage"],
                    "Metadata": row["Metadata"],
                    # Convert string representation of list to actual list of floats
                    "Embedding": [float(x) for x in row["Embedding"][1:-1].split(",")]  
                }
            }
            actions.append(action)

        # Bulk index the data to Elasticsearch
        helpers.bulk(es_instance, actions)
        print("Successfully indexed data to ES instance")
