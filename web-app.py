import streamlit as st
import requests
import json
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="LLM Query & Document Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Placeholder functions - implement these separately
def init_database():
    """Initialize SQLite database for document storage"""
    pass

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    pass

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    pass

def extract_text_from_txt(file):
    """Extract text from TXT file"""
    pass

def scrape_web_content(url):
    """Basic web scraping function"""
    pass

def save_document(title, content, source_type, source_url=None, file_hash=None, metadata=None):
    """Save document to database"""
    pass

def get_all_documents():
    """Retrieve all documents from database"""
    pass

def search_documents(query):
    """Search documents by content"""
    pass

def save_query(query_text, response, model_used):
    """Save query and response to database"""
    pass

def get_query_history():
    """Get query history from database"""
    pass

# FastAPI integration for OLLAMA
def query_ollama_via_fastapi(query, model="llama2", temperature=0.7, context=""):
    """Query OLLAMA through FastAPI backend"""
    try:
        fastapi_url = st.session_state.get('fastapi_url', 'http://localhost:8000')
        
        payload = {
            "query": query,
            "model": model,
            "temperature": temperature,
            "context": context
        }
        
        response = requests.post(
            f"{fastapi_url}/query-ollama",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json().get('response', 'No response received')
    except Exception as e:
        return f"Error querying OLLAMA via FastAPI: {str(e)}"

def query_openai(api_key, model, prompt, temperature=0.7):
    """Query OpenAI API"""
    pass

def query_anthropic(api_key, model, prompt, temperature=0.7):
    """Query Anthropic Claude API"""
    pass

# Main Streamlit app
def main():
    # Initialize database
    init_database()
    
    st.title("🤖 LLM Query & Document Manager")
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
                value="http://localhost:8000",
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
        
        # Temperature setting
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        st.markdown("---")
        st.header("📊 Database Stats")
        
        # Show database statistics
        docs = get_all_documents() or []
        st.metric("Total Documents", len(docs))
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Query", "📁 Upload Documents", "🔍 Browse Documents", "📈 Query History"])
    
    with tab1:
        st.header("Ask Questions")
        
        # Context selection
        use_context = st.checkbox("Use document context for answers")
        
        context_text = ""
        if use_context:
            search_query = st.text_input("Search documents for context (optional)")
            if search_query:
                context_docs = search_documents(search_query) or []
                if context_docs:
                    st.write(f"Found {len(context_docs)} relevant documents")
                    # Assuming doc structure: [id, title, content, ...]
                    context_text = "\n\n".join([doc[2] for doc in context_docs[:3]])
                else:
                    st.warning("No relevant documents found")
            else:
                # Use all documents as context
                all_docs = get_all_documents() or []
                context_text = "\n\n".join([doc[2] for doc in all_docs[:5]])
        
        # Query input
        query = st.text_area("Enter your question:", height=100)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_query = st.button("Submit Query", type="primary")
        with col2:
            if use_context and context_text:
                st.info(f"Using context from documents ({len(context_text)} characters)")
        
        if submit_query and query:
            with st.spinner("Processing query..."):
                # Prepare prompt with context if enabled
                if use_context and context_text:
                    full_prompt = f"Context:\n{context_text}\n\nQuestion: {query}\n\nPlease answer based on the provided context."
                else:
                    full_prompt = query
                
                # Query the selected LLM
                if model_config["provider"] == "ollama_fastapi":
                    response = query_ollama_via_fastapi(
                        query=query,
                        model=model_config["model"],
                        temperature=temperature,
                        context=context_text if use_context else ""
                    )
                elif model_config["provider"] == "openai":
                    if model_config.get("api_key"):
                        response = query_openai(model_config["api_key"], model_config["model"], full_prompt, temperature)
                    else:
                        response = "Please provide OpenAI API key"
                elif model_config["provider"] == "anthropic":
                    if model_config.get("api_key"):
                        response = query_anthropic(model_config["api_key"], model_config["model"], full_prompt, temperature)
                    else:
                        response = "Please provide Anthropic API key"
                
                # Display response
                st.subheader("Response:")
                st.markdown(response)
                
                # Save query to database
                save_query(query, response, f"{model_config['provider']}-{model_config['model']}")
                
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
                                    content = extract_text_from_pdf(uploaded_file)
                                elif file_extension == 'docx':
                                    content = extract_text_from_docx(uploaded_file)
                                elif file_extension == 'txt':
                                    content = extract_text_from_txt(uploaded_file)
                                else:
                                    st.error(f"Unsupported file type: {file_extension}")
                                    continue
                                
                                if content:
                                    # Save to database
                                    doc_id = save_document(
                                        title=uploaded_file.name,
                                        content=content,
                                        source_type="file_upload",
                                        metadata={"file_size": len(content), "file_type": file_extension}
                                    )
                                    
                                    st.success(f"Document saved! ID: {doc_id}")
                                    
                                    # Show preview
                                    with st.expander("Preview Content"):
                                        preview = content[:1000] + "..." if len(content) > 1000 else content
                                        st.text_area("Content Preview:", preview, height=200)
        
        st.markdown("---")
        
        # Web URL section
        st.subheader("🌐 Add Web Content")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            web_url = st.text_input("Enter URL:", placeholder="https://example.com/article")
        with col2:
            scrape_button = st.button("Scrape Content", type="secondary")
        
        if scrape_button and web_url:
            with st.spinner("Scraping web content..."):
                content = scrape_web_content(web_url)
                
                if content:
                    # Generate title from URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(web_url)
                    title = f"Web: {parsed_url.netloc}"
                    
                    doc_id = save_document(
                        title=title,
                        content=content,
                        source_type="web_scrape",
                        source_url=web_url,
                        metadata={"domain": parsed_url.netloc}
                    )
                    
                    st.success(f"Web content saved! ID: {doc_id}")
                    
                    # Show preview
                    with st.expander("Preview Scraped Content"):
                        preview = content[:1000] + "..." if len(content) > 1000 else content
                        st.text_area("Content Preview:", preview, height=200)
        elif scrape_button:
            st.error("Please enter a valid URL")
    
    with tab3:
        st.header("Browse Documents")
        
        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search documents:", placeholder="Enter keywords...")
        
        with col2:
            source_filter = st.selectbox("Filter by source:", ["All", "file_upload", "web_scrape"])
        
        with col3:
            sort_order = st.selectbox("Sort by:", ["Newest", "Oldest", "Title"])
        
        # Get and filter documents
        if search_term:
            documents = search_documents(search_term) or []
            st.info(f"Found {len(documents)} documents matching '{search_term}'")
        else:
            documents = get_all_documents() or []
        
        # Display documents
        if documents:
            st.write(f"Showing {len(documents)} document(s)")
            
            for i, doc in enumerate(documents):
                # Assuming doc structure: [id, title, content, source_type, source_url, file_hash, created_at, metadata]
                with st.expander(f"📄 {doc[1]} ({doc[3]}) - {doc[6] if len(doc) > 6 else 'Unknown date'}"):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**ID:** {doc[0]}")
                        st.write(f"**Source Type:** {doc[3]}")
                        if len(doc) > 4 and doc[4]:  # source_url
                            st.write(f"**URL:** {doc[4]}")
                        if len(doc) > 6:
                            st.write(f"**Created:** {doc[6]}")
                    
                    with col2:
                        if st.button(f"Use as Context", key=f"context_{doc[0]}"):
                            st.session_state[f'selected_context'] = doc[2]
                            st.success("Document selected as context!")
                    
                    # Content preview
                    content_preview = doc[2][:500] + "..." if len(doc[2]) > 500 else doc[2]
                    st.text_area("Content:", content_preview, height=150, key=f"doc_content_{doc[0]}")
        else:
            st.info("No documents found. Upload some documents to get started!")
    
    with tab4:
        st.header("Query History")
        
        # Get query history
        queries = get_query_history() or []
        
        if queries:
            st.write(f"Showing {len(queries)} recent queries")
            
            # Add export option
            if st.button("📥 Export History"):
                # This would implement export functionality
                st.info("Export functionality would be implemented here")
            
            for i, query in enumerate(queries):
                # Assuming query structure: [id, query_text, response, model_used, created_at]
                query_preview = query[1][:100] + "..." if len(query[1]) > 100 else query[1]
                
                with st.expander(f"Query {i+1}: {query_preview} ({query[4] if len(query) > 4 else 'Unknown time'})"):
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write(f"**Model:** {query[3] if len(query) > 3 else 'Unknown'}")
                    with col2:
                        st.write(f"**Time:** {query[4] if len(query) > 4 else 'Unknown'}")
                    
                    st.write("**Query:**")
                    st.markdown(query[1])
                    
                    st.write("**Response:**")
                    st.markdown(query[2])
                    
                    # Option to rerun query
                    if st.button(f"🔄 Rerun Query", key=f"rerun_{query[0]}"):
                        st.session_state['rerun_query'] = query[1]
                        st.success("Query copied! Go to Query tab to run it.")
        else:
            st.info("No query history found. Start asking questions to build your history!")
    
    # Handle rerun query from history
    if 'rerun_query' in st.session_state:
        st.sidebar.info(f"Ready to rerun: {st.session_state['rerun_query'][:50]}...")

if __name__ == "__main__":
    main()