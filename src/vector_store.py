"""
Vector Store Manager using Milvus

This module handles embedding generation, vector storage,
and top-k retrieval using Milvus.
"""

import os
import json
from typing import List, Dict, Optional

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from openai import OpenAI
import numpy as np


class VectorStore:
    """Manages vector embeddings and similarity search using Milvus."""
    
    def __init__(
        self,
        collection_name: str = "postgres_docs",
        embedding_model: str = "text-embedding-3-small",
        embedding_dimensions: int = 1536,
        host: Optional[str] = None,
        port: Optional[str] = None,
    ):
        self.collection_name = collection_name
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model_name = embedding_model
        self.embedding_dimensions = embedding_dimensions
        """Initialize the vector store.
        
        Args:
            collection_name: Name of the Milvus collection
            embedding_model: OpenAI embedding model name
            embedding_dimensions: Dimension of the embedding vectors
            host: Milvus server host (defaults to env var or localhost)
            port: Milvus server port (defaults to env var or 19530)
        """
        self.collection_name = collection_name
        
        # Get Milvus connection details from environment or use defaults
        if host is None:
            host = os.getenv("MILVUS_HOST", "localhost")
        if port is None:
            port = os.getenv("MILVUS_PORT", "19530")
        
        # Connect to Milvus
        print(f"Connecting to Milvus at {host}:{port}")
        connections.connect(
            alias="default",
            host=host,
            port=port
        )
        
        # Create or get collection
        self.collection = self._create_collection()
        
        print(f"Vector store initialized. Collection: {collection_name}")
    
    def _create_collection(self) -> Collection:
        """Create or get existing Milvus collection.
        
        Returns:
            Milvus Collection object
        """
        # Check if collection exists
        if utility.has_collection(self.collection_name):
            print(f"Collection '{self.collection_name}' already exists")
            collection = Collection(self.collection_name)
            collection.load()
            return collection
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dimensions),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="chunk_id", dtype=DataType.INT64),
            FieldSchema(name="total_chunks", dtype=DataType.INT64),
        ]
        
        schema = CollectionSchema(fields=fields, description="PostgreSQL documentation")
        
        # Create collection
        print(f"Creating collection '{self.collection_name}'")
        collection = Collection(name=self.collection_name, schema=schema)
        
        # Create HNSW index for hierarchical navigable small world graph
        # Better for high-dimensional vectors and provides faster similarity search
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {
                "M": 16,        # Number of bi-directional links per node
                "efConstruction": 256  # Size of dynamic candidate list during construction
            }
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        
        collection.load()
        return collection
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts using OpenAI API.
        
        Args:
            texts: List of text strings
            
        Returns:
            NumPy array of embeddings
        """
        response = self.openai_client.embeddings.create(
            input=texts,
            model=self.embedding_model_name
        )
        embeddings = np.array([item.embedding for item in response.data])
        return embeddings
    
    def add_documents(self, chunks: List[Dict[str, str]]) -> None:
        """Add document chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
        """
        print(f"\nAdding {len(chunks)} chunks to vector store...")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Prepare data for Milvus
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        sources = [chunk['metadata']['source'] for chunk in chunks]
        titles = [chunk['metadata']['title'] for chunk in chunks]
        chunk_ids = [chunk['metadata']['chunk_id'] for chunk in chunks]
        total_chunks = [chunk['metadata']['total_chunks'] for chunk in chunks]
        
        # Insert data in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            
            data = [
                ids[i:end_idx],
                embeddings[i:end_idx].tolist(),
                texts[i:end_idx],
                sources[i:end_idx],
                titles[i:end_idx],
                chunk_ids[i:end_idx],
                total_chunks[i:end_idx],
            ]
            
            self.collection.insert(data)
            self.collection.flush()
            
            print(f"Added batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
        print(f"Successfully added {len(chunks)} chunks to vector store")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        expr: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            expr: Optional filter expression
            
        Returns:
            List of result dictionaries with text, metadata, and distance
        """
        # Generate query embedding using OpenAI
        embeddings = self.generate_embeddings([query])
        query_embedding = embeddings[0].tolist()
        
        # Search parameters for HNSW
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}  # Size of dynamic candidate list during search
        }
        
        # Search in Milvus
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["id", "text", "source", "title", "chunk_id", "total_chunks"]
        )
        
        # Format results
        formatted_results = []
        for hit in results[0]:
            formatted_results.append({
                'id': hit.entity.get('id'),
                'text': hit.entity.get('text'),
                'metadata': {
                    'source': hit.entity.get('source'),
                    'title': hit.entity.get('title'),
                    'chunk_id': hit.entity.get('chunk_id'),
                    'total_chunks': hit.entity.get('total_chunks')
                },
                'distance': hit.distance
            })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.num_entities
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'connection': f"{connections.get_connection_addr('default')}"
        }
    
    def drop_collection(self):
        """Drop the collection."""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            print(f"Dropped collection '{self.collection_name}'")


def build_vector_store(chunks_file: str = "data/raw_docs/document_chunks.json") -> VectorStore:
    """Build and populate the vector store from chunks file.
    
    Args:
        chunks_file: Path to the chunks JSON file
        
    Returns:
        Initialized and populated VectorStore
    """
    # Load chunks
    print(f"Loading chunks from {chunks_file}")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Check if collection is already populated
    stats = vector_store.get_collection_stats()
    if stats['total_chunks'] > 0:
        print(f"Collection already contains {stats['total_chunks']} chunks")
        response = input("Do you want to rebuild the vector store? (yes/no): ")
        if response.lower() != 'yes':
            print("Using existing vector store")
            return vector_store
        
        # Drop and recreate collection
        vector_store.drop_collection()
        connections.disconnect("default")
        vector_store = VectorStore()
    
    # Add documents
    vector_store.add_documents(chunks)
    
    # Print stats
    stats = vector_store.get_collection_stats()
    print(f"\nVector store stats:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Connection: {stats['connection']}")
    
    return vector_store


def main():
    """Main function to build the vector store."""
    print("Building vector store with Milvus...")
    vector_store = build_vector_store()
    
    # Test retrieval
    print("\n" + "="*60)
    print("Testing retrieval...")
    test_query = "How do I create an index in PostgreSQL?"
    results = vector_store.retrieve(test_query, top_k=3)
    
    print(f"\nQuery: {test_query}")
    print(f"\nTop {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (distance: {result['distance']:.4f}) ---")
        print(f"Source: {result['metadata']['title']}")
        print(f"URL: {result['metadata']['source']}")
        print(f"Text preview: {result['text'][:200]}...")


if __name__ == "__main__":
    main()
