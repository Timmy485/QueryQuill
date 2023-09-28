import os
import json
import streamlit as st
from indexing import connect_instance, create_index, index_data_to_elasticsearch
from gen_ai import generate_direct_answer_with_llama
from retrieval import search_relevant_passages, search_similar_passages, save_results_to_csv
from sentence_transformers import SentenceTransformer
import pandas as pd


st. set_page_config(page_title="Query Quill", )
st.markdown(
    """
    <style>
    .appview-container .main .block-container {
        padding-top: 2rem;
        margin: 0;
    }
    .css-usj992 {
    background-color: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "<h1 style='text-align: center; padding: 10px;'>Query Quill</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h5 style='text-align: center; padding: 2px;'>Unveil Insights From Docs</h5>",
    unsafe_allow_html=True
)

# Sidebar Navigation with header background color
st.sidebar.markdown(
    "<h3 style= padding: 10px;'>Navigation</h3>",
    unsafe_allow_html=True
)
# Use a dropdown menu for feature selection
selected_feature = st.sidebar.selectbox("Select a Feature", (
    "Query Existing Documents",
    "Upload & Analyze Custom Document",
    
))
# Main Content with light background color
st.markdown(
    "<div style='background-color: #f9f9f9; padding: 0px;'>",
    unsafe_allow_html=True
)


path = os.path.dirname(__file__)
json_path = path+'/config.json'
try:
    with open(json_path, 'r') as config_file:
        config_data = json.load(config_file)
    es_host = config_data.get('es_host')
    es_username = config_data.get('es_username') 
    es_password = config_data.get('es_password')
except FileNotFoundError:
    # If the config.json file is not found, try reading from Streamlit Secrets
    try:
        es_host = st.secrets["es_host"]
    except st.secrets.SecretsFileNotFound:
        st.error(
            "Please provide the API key either in a 'config.json' file or as a Streamlit Secret.")
        st.stop()

es = connect_instance(es_host, 9243, es_username, es_password)
model = SentenceTransformer('paraphrase-distilroberta-base-v1')

if selected_feature == "Query Existing Documents":
    #input prompt
    prompt = st.chat_input("Query your file")
    if prompt:
        #create prompt embeddings
        query_embedding = model.encode(prompt)

        # Search for relevant passages
        index_name = "passage_metadata_emb"  #name of your index
        search_results = search_relevant_passages(es, index_name, query_embedding)
        passages = [hit["_source"]["Passage"] for hit in search_results]
        
        # Display relevant results in Streamlit
        df = pd.DataFrame(columns=["Passage", "Relevance Score"])
        row_data = {
        "Passage": [hit["_source"]["Passage"] for hit in search_results],
        "Relevance Score": [hit["_score"] for hit in search_results],
        }
        df = pd.DataFrame(row_data)
        st.table(df)

        st.write("Generative AI Result:")
        gen_ai_output = generate_direct_answer_with_llama(search_results, prompt, save_csv=False)
        st.write(gen_ai_output)

elif selected_feature == "Upload & Analyze Custom Document":
    # Create a Streamlit file uploader widget
    uploaded_file = st.file_uploader(
        "Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])


    # Check if a file has been uploaded
    if uploaded_file is not None:
        prompt = st.chat_input("Query your file")
        if prompt:
            pass