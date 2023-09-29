import streamlit as st
import requests
import pandas as pd

def configure_ui():
    """Configure the UI elements and styles."""
    st.set_page_config(page_title="Query Quill")
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

def sidebar_navigation():
    """Set up the sidebar navigation."""
    st.sidebar.markdown(
        "<h3 style= padding: 10px;'>Navigation</h3>",
        unsafe_allow_html=True
    )
    return st.sidebar.selectbox(
        "Select a Feature", 
        ("Query Existing Documents", "Upload & Analyze Custom Document")
    )

# API endpoints
API_ENDPOINT = "http://127.0.0.1:5000/ask" 
RESET_INDEX_ENDPOINT = "http://127.0.0.1:5000/reset_index" 
UPLOAD_AND_QUERY_ENDPOINT = "http://127.0.0.1:5000/upload" 

# Reset the Elasticsearch index on app startup
requests.post(RESET_INDEX_ENDPOINT)
new_documents_uploaded = False

configure_ui()
selected_feature = sidebar_navigation()

if selected_feature == "Query Existing Documents":
    prompt = st.chat_input("Query your file")
    if prompt:
        response = requests.post(API_ENDPOINT, json={"question": prompt})
        data = response.json()

        # Extract and tabulate the results
        df = pd.DataFrame({
            "Passage": data.get("answer", []),
            "Relevance Scores": data.get("relevance scores", []),
            "Metadata": data.get("metadata", [])
        })
        st.write("### Top Results")
        st.table(df)

        # Display AI-generated answer
        st.write("### AI Enhanced Answer")
        st.write(data.get("gen_ai_output"))

elif selected_feature == "Upload & Analyze Custom Document":
    txt_file = st.file_uploader("Upload a .txt file", type="txt")
    json_file = st.file_uploader("Upload a .json file", type="json")

    if txt_file and json_file:
        if new_documents_uploaded:
            # Reset Elasticsearch index if new documents are uploaded
            requests.post(RESET_INDEX_ENDPOINT)
            new_documents_uploaded = False

        prompt = st.chat_input("Query your uploaded files")
        if prompt:
            response = requests.post(
                UPLOAD_AND_QUERY_ENDPOINT,
                files={"txt_file": txt_file, "json_file": json_file},
                data={"question": prompt}
            )
            results = response.json()

            # Extract and tabulate the results
            df = pd.DataFrame({
                "Passage": results.get("answer", []),
                "Relevance Scores": results.get("relevance scores", []),
                "Metadata": results.get("metadata", [])
            })
            st.write("### Top Results")
            st.table(df)

            # Display AI-generated answer
            st.write("### AI Enhanced Answer")
            st.write(results.get("gen_ai_output"))

            new_documents_uploaded = True
