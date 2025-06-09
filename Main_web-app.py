import streamlit as st
import requests
import json
from datetime import datetime
import os
from  documentprocessor import maindocprocesser , mainwebprocess
# Set page config
st.set_page_config(
    page_title="Chat with your Docuuments(AI-Based Document RAG system)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)



# FastAPI integration for OLLAMA
def query_ollama_via_fastapi(query):
    """Query OLLAMA through FastAPI backend"""
    try:
        fastapi_url = st.session_state.get('fastapi_url', 'http://127.0.0.1:8000')
        
        payload = {
            "requesttext": query
        }
        
        response = requests.post(
            f"{fastapi_url}/submit_query",
            json=payload,
            timeout=600
        )
        print(response)
 
        response.raise_for_status()
        #return response.json().get('response', 'No response received')
        return response

    except Exception as e:
        return f"Error querying OLLAMA via FastAPI: {str(e)}"

def save_uploaded_file(uploaded_file):
    """Save uploaded file to specified path and return file path"""
    try:
        # Create directory if it doesn't exist
        save_path="data/source"
        os.makedirs(save_path, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = uploaded_file.name.split('.')[-1]
        base_name = uploaded_file.name.rsplit('.', 1)[0]
        unique_filename = f"{base_name}_{timestamp}.{file_extension}"
        
        file_path = os.path.join(save_path, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path, unique_filename
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None, None


# Main Streamlit app
def main():
    
    st.title("🤖 Chat with your document(AI-Based Document RAG system)")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LLM Selection
        llm_provider = st.selectbox(
            "Select LLM Provider",
            ["OLLAMA (FastAPI)", "OpenAI", "Anthropic (Claude)"]
        )
        
        if llm_provider == "OLLAMA (FastAPI)":
            st.info("Using FastAPI backend for OLLAMA")
            
            # FastAPI URL configuration
            fastapi_url = st.text_input(
                "FastAPI URL", 
                value="http://127.0.0.1:8000",
                help="URL of your FastAPI backend"
            )
            st.session_state['fastapi_url'] = fastapi_url
            
            # Test FastAPI connection
            if st.button("Test FastAPI Connection"):
                try:
                    response = requests.get(f"{fastapi_url}/health", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ FastAPI connection successful")
                    else:
                        st.error("❌ FastAPI connection failed")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
            
            ollama_model = st.text_input("OLLAMA Model", value="llama2")
            model_config = {"provider": "ollama_fastapi", "model": ollama_model}
            
        elif llm_provider == "OpenAI":
            openai_api_key = st.text_input("OpenAI API Key", type="password")
            openai_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
            model_config = {"provider": "openai", "api_key": openai_api_key, "model": openai_model}
            
        elif llm_provider == "Anthropic (Claude)":
            anthropic_api_key = st.text_input("Anthropic API Key", type="password")
            anthropic_model = st.selectbox("Model", ["claude-3-sonnet-20240229", "claude-3-opus-20240229"])
            model_config = {"provider": "anthropic", "api_key": anthropic_api_key, "model": anthropic_model}
        
        ## Temperature setting
        #temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        #st.markdown("---")
        #st.header("📊 Database Stats")
        
        # Show database statistics
        #docs = get_all_documents() or []
        #st.metric("Total Documents", len(docs))
    
    # Main content area with tabs
    tab1, tab2 = st.tabs(["📝 Query", "📁 Upload Documents"])
    #tab1, tab2, tab3, tab4 = st.tabs(["📝 Query", "📁 Upload Documents", "🔍 Browse Documents", "📈 Query History"])

    with tab1:
        st.header("Ask Questions")      
        # Query input
        query = st.text_area("Enter your question:", height=100)
        
        submit_query = st.button("Submit Query", type="primary")

        if submit_query and query:
            with st.spinner("Processing query..."):
                
                # Query the selected LLM
                if model_config["provider"] == "ollama_fastapi":
                    response = query_ollama_via_fastapi(
                        query=query
                    )
                elif model_config["provider"] == "openai":
                    if model_config.get("api_key"):
                        response = query_openai(model_config["api_key"], model_config["model"], full_prompt)
                    else:
                        response = "Please provide OpenAI API key"
                elif model_config["provider"] == "anthropic":
                    if model_config.get("api_key"):
                        response = query_anthropic(model_config["api_key"], model_config["model"], full_prompt)
                    else:
                        response = "Please provide Anthropic API key"
                
                # Display response
                st.subheader("Response:")
                st.markdown(response.content)
                
                # Save query to database
                #save_query(query, response, f"{model_config['provider']}-{model_config['model']}")
                
                st.success("Query saved to history!")
        elif submit_query:
            st.error("Please enter a question")

    with tab2:
        st.header("Upload Documents")
        
        # File upload section
        st.subheader("📄 Upload Files")
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} file(s)")
            
            for uploaded_file in uploaded_files:
                with st.expander(f"Process: {uploaded_file.name}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**File:** {uploaded_file.name}")
                        st.write(f"**Size:** {uploaded_file.size} bytes")
                        st.write(f"**Type:** {uploaded_file.type}")
                    
                    with col2:
                        if st.button(f"Process", key=f"process_{uploaded_file.name}"):
                            with st.spinner(f"Processing {uploaded_file.name}..."):
                                # Extract text based on file type
                                file_extension = uploaded_file.name.split('.')[-1].lower()
                                
                                if file_extension == 'pdf':
                                    save_uploaded_file(uploaded_file)
                                    maindocprocesser()
                                elif file_extension == 'docx':
                                    content = extract_text_from_docx(uploaded_file)
                                elif file_extension == 'txt':
                                    content = extract_text_from_txt(uploaded_file)
                                else:
                                    st.error(f"Unsupported file type: {file_extension}")
                                    continue
                                

        
        st.markdown("---")
        
        # Web URL section
        st.subheader("🌐 Add Web Content")
        
        
        col1, col2 = st.columns([3, 1])
        with col1:
            web_url = st.text_input("Enter URL:", placeholder="https://example.com/article")
        with col2:
            scrape_button = st.button("WebLoader", type="secondary")
        
        if scrape_button and web_url:
            with st.spinner("Scraping web content..."):
                content=[WebBaseLoader(url).load() for url in urls]

                if content:
                    docs_list = [item for sublist in content for item in sublist]
                    mainwebprocess(docs_list)
                    
                    st.success(f"Web content saved!")
                    
                    # Show preview
                    with st.expander("Preview Scraped Content"):
                        preview = content[:1000] + "..." if len(content) > 1000 else content
                        st.text_area("Content Preview:", preview, height=200)
        elif scrape_button:
            st.error("Please enter a valid URL")



    
    # Handle rerun query from history
    if 'rerun_query' in st.session_state:
        st.sidebar.info(f"Ready to rerun: {st.session_state['rerun_query'][:50]}...")

if __name__ == "__main__":
    main()