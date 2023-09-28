from elasticsearch import Elasticsearch, helpers
import csv

# Connect to the ES instanc
def connect_instance(host, port, username, password, timeout=120):
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
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        actions = []
        for row in reader:
            action = {
                "_index": index_name,
                "_source": {
                    "Passage": row["Passage"],
                    "Metadata": row["Metadata"],
                    "Embedding": [float(x) for x in row["Embedding"][1:-1].split(",")]  # Convert string representation of list to actual list
                }
            }
            actions.append(action)

        # Bulk index the data
        helpers.bulk(es_instance, actions)
        print("Successfully indexed data to ES instance")