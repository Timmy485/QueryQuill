# QueryQuill

This repository contains a Flask API that allows for passage retrieval based on user questions. It uses SentenceTransformers to encode questions and passages into embeddings, and Elasticsearch to efficiently search and retrieve relevant passages.

## Installation

### Using Docker

Docker provides a consistent and reproducible environment, making it easy to share and set up the application on any machine.

1. **Prerequisites**:
    - Ensure you have Docker installed on your system. If not, download and install from [here](https://www.docker.com/get-started).

2. **Clone the Repository**:
    ```
    git clone [https://github.com/Timmy485/QueryQuill.git]
    cd [repository-folder]
    ```

3. **Build the Docker Image**:
    ```
    docker build -t queryquill -f docker/Dockerfile .
    ```

4. **Run the Docker Container**:
    ```
    docker run -p 5000:5000 --env-file ./.env queryquill
    ```

After executing the above command, the Flask API should be running on `http://127.0.0.1:5000/`.


## API Endpoints

- **/ask**:
    - **Method**: POST
    - **Description**: Retrieves answers for a given question.
    - **Request Body**: JSON object containing `question`.
  
- **/upload**:
    - **Method**: POST
    - **Description**: Uploads text and JSON files and retrieves answers for a given question.
    - **Request Body**: Form data containing `txt_file`, `json_file`, and `question`.

- **/reset_index**:
    - **Method**: POST
    - **Description**: Resets the Elasticsearch index.

## Troubleshooting

If you encounter any issues while setting up or running the application, please check the following:

- Ensure that the environment variables are set correctly in the `.env` file.
- Check if the Elasticsearch instance is running and accessible.
- Ensure you have the necessary permissions to read and write to directories.
