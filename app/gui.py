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
        "<h5 style='text-align: center; padding: 2px; margin-bottom: 20px;'>Unveil Insights From Docs</h5>",
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

configure_ui()
selected_feature = sidebar_navigation()


# API endpoints
API_ENDPOINT = "http://127.0.0.1:5000/ask" 
RESET_INDEX_ENDPOINT = "http://127.0.0.1:5000/reset_index" 
UPLOAD_AND_QUERY_ENDPOINT = "http://127.0.0.1:5000/upload" 

# Reset the Elasticsearch index on app startup
try:
    response = requests.post(RESET_INDEX_ENDPOINT)
    response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
except requests.RequestException as e:
    st.error("Failed to reset the Elasticsearch index. Please ensure the backend service is running.")
    quit()

new_documents_uploaded = False




if selected_feature == "Query Existing Documents":
    prompt = st.chat_input("Query your file")
    if prompt:
        try:
            response = requests.post(API_ENDPOINT, json={"question": prompt})
            response.raise_for_status()  # This raises an HTTPError for bad responses
            data = response.json()

            # Extract and tabulate the results
            df = pd.DataFrame({
                "Passage": data.get("answer", []),
                # "Relevance Scores": data.get("relevance_scores", []),
                "Metadata": data.get("metadata", [])
            })
            st.write("### Top Results")
            st.table(df)

            # Display AI-generated answer
            st.write("### AI Enhanced Answer")
            st.write(data.get("gen_ai_output"))

        except requests.RequestException as e:
            st.error("Failed to fetch results from the API. Please ensure the backend service is running.")
            st.exception(e)


elif selected_feature == "Upload & Analyze Custom Document":
    txt_file = st.file_uploader("Upload a .txt file", type="txt")
    json_file = st.file_uploader("Upload a .json file", type="json")

    if txt_file and json_file:
        if new_documents_uploaded:
            try:
                # Reset Elasticsearch index if new documents are uploaded
                response = requests.post(RESET_INDEX_ENDPOINT)
                
                # Check for HTTP errors
                response.raise_for_status()
                
                new_documents_uploaded = False

            except requests.RequestException as e:
                # Handle the exception and display a message to the user
                st.error("Error: Could not reset the Elasticsearch index. Please ensure the backend service is running.")

        prompt = st.chat_input("Query your uploaded files")
        if prompt:
            try:
                response = requests.post(
                    UPLOAD_AND_QUERY_ENDPOINT,
                    files={"txt_file": txt_file, "json_file": json_file},
                    data={"question": prompt}
                )
                
                # Check for HTTP errors
                response.raise_for_status()

                results = response.json()

                # Extract and tabulate the results
                df = pd.DataFrame({
                    "Passage": results.get("answer", []),
                    # "Relevance Scores": results.get("relevance_scores", []),
                    "Metadata": results.get("metadata", [])
                })
                st.write("### Top Results")
                st.table(df)

                # Display AI-generated answer
                st.write("### AI Enhanced Answer")
                st.write(results.get("gen_ai_output"))

                new_documents_uploaded = True

            except requests.RequestException as e:
                # Handle the exception and display a user-friendly message
                st.error("Error: Could not query the uploaded documents. Please ensure the backend service is running.")
