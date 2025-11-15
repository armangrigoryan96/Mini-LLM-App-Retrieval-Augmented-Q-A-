"""
Streamlit UI for PostgreSQL RAG Q&A System

Interactive chat interface for asking questions about PostgreSQL documentation.
"""

import streamlit as st
from dotenv import load_dotenv
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline


# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="PostgreSQL Documentation Q&A",
    page_icon="🐘",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_rag_pipeline():
    """Initialize and cache the RAG pipeline."""
    try:
        # Initialize vector store
        vector_store = VectorStore()
        
        # Check if vector store has data
        stats = vector_store.get_collection_stats()
        if stats['total_chunks'] == 0:
            st.warning("Vector store is empty. Building vector database automatically...")
            
            # Import and run scraper
            from src.scraper import PostgresDocScraper, DocumentChunker
            
            # Get max docs from env (default to 2 for cost savings)
            max_docs_str = os.getenv("MAX_DOCS", "2")
            max_docs = int(max_docs_str) if max_docs_str and max_docs_str != "0" else None
            
            # Get max chunks per doc from env (default to 5 for cost savings)
            max_chunks_str = os.getenv("MAX_CHUNKS_PER_DOC", "5")
            max_chunks_per_doc = int(max_chunks_str) if max_chunks_str and max_chunks_str != "0" else None
            
            with st.spinner(f"Fetching PostgreSQL documentation (max {max_docs or 'all'} docs)..."):
                scraper = PostgresDocScraper()
                documents = scraper.fetch_all(max_docs=max_docs)
                st.success(f"Fetched {len(documents)} documents")
            
            with st.spinner(f"Chunking documents (max {max_chunks_per_doc or 'all'} chunks per doc)..."):
                chunker = DocumentChunker()
                chunks = chunker.chunk_documents(documents, max_chunks_per_doc=max_chunks_per_doc)
                st.success(f"Created {len(chunks)} chunks")
            
            with st.spinner("Building vector database (this may take a few minutes)..."):
                vector_store.add_documents(chunks)
                st.success("Vector database built successfully!")
                st.rerun()
        
        # Initialize RAG pipeline
        rag = RAGPipeline(
            vector_store=vector_store,
            model_name=os.getenv("LLM_MODEL", "gpt-4o"),
            top_k=int(os.getenv("TOP_K", 5))
        )
        
        return rag
    except Exception as e:
        st.error(f"Error initializing RAG pipeline: {e}")
        st.info("Make sure you have:")
        st.code("""
1. Set OPENAI_API_KEY in .env file
2. Start Milvus: docker-compose up -d
        """)
        st.stop()


def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🐘 PostgreSQL Documentation Q&A")
    st.markdown("""
    Ask questions about PostgreSQL 16 documentation. This system uses RAG (Retrieval-Augmented Generation)
    to provide accurate answers based on official PostgreSQL documentation.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Initialize RAG pipeline
        with st.spinner("Initializing system..."):
            rag = initialize_rag_pipeline()
        
        # Display stats
        stats = rag.vector_store.get_collection_stats()
        st.success("System ready!")
        st.metric("Documents in database", stats['total_chunks'])
        
        # Settings
        check_relevance = st.checkbox(
            "Check query relevance",
            value=True,
            help="Filter out questions unrelated to PostgreSQL"
        )
        
        show_sources = st.checkbox(
            "Show sources",
            value=True,
            help="Display source documents for each answer"
        )
        
        # Clear history button
        if st.button("🗑️ Clear Chat History"):
            rag.clear_history()
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Example questions (from qa_dataset.py)
        st.header("💡 Example Questions")
        example_questions = [
            "How do I create a simple index on a single column in PostgreSQL?",
            "What is the difference between TRUNCATE and DELETE in PostgreSQL?",
            "What is MVCC in PostgreSQL?",
            "How do I grant SELECT privileges on a table to a user?",
            "What is the difference between a view and a materialized view?",
            "What does the ANALYZE command do?",
            "What is the MERGE command used for?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state.example_question = question
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if show_sources and "sources" in message and message["sources"]:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        **{i}. {source['title']}** (relevance: {1-source['distance']:.2%})
                        
                        [{source['url']}]({source['url']})
                        """)
    
    # Handle example question click
    if "example_question" in st.session_state:
        user_input = st.session_state.example_question
        del st.session_state.example_question
    else:
        # Chat input
        user_input = st.chat_input("Ask a question about PostgreSQL...")
    
    # Process user input
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = rag.answer_question(user_input, check_relevance=check_relevance)
            
            # Display answer
            st.markdown(response['answer'])
            
            # Display sources
            if show_sources and response['sources']:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(response['sources'], 1):
                        st.markdown(f"""
                        **{i}. {source['title']}** (relevance: {1-source['distance']:.2%})
                        
                        [{source['url']}]({source['url']})
                        """)
            
            # Add assistant message to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response['answer'],
                "sources": response.get('sources', [])
            })
    
    # Footer
    st.divider()
    st.caption("Powered by OpenAI GPT-4o and Milvus")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found!")
        st.info("Please create a `.env` file with your OpenAI API key:")
        st.code("OPENAI_API_KEY=your_api_key_here")
        st.stop()
    
    main()
