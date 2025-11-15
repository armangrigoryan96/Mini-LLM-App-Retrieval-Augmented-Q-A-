"""
Unit tests for the vector store module
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from src.vector_store import VectorStore


class TestVectorStore(unittest.TestCase):
    """Test cases for VectorStore"""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('src.vector_store.OpenAI')
    @patch('src.vector_store.Collection')
    @patch('src.vector_store.utility')
    @patch('src.vector_store.connections')
    def setUp(self, mock_connections, mock_utility, mock_collection, mock_openai):
        """Set up test fixtures"""
        # Mock OpenAI client
        self.mock_openai_client = MagicMock()
        mock_openai.return_value = self.mock_openai_client
        
        # Mock Milvus connections and utility
        mock_utility.has_collection.return_value = False
        self.mock_collection = MagicMock()
        mock_collection.return_value = self.mock_collection
        
        # Create vector store instance
        self.vector_store = VectorStore(
            collection_name="test_collection",
            embedding_model="text-embedding-3-small"
        )
    
    def test_initialization(self):
        """Test vector store initialization"""
        self.assertEqual(self.vector_store.collection_name, "test_collection")
        self.assertEqual(self.vector_store.embedding_dimensions, 1536)
    
    def test_generate_embeddings(self):
        """Test embedding generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_embedding_obj = Mock()
        mock_embedding_obj.embedding = [0.1] * 1536
        mock_response.data = [mock_embedding_obj, mock_embedding_obj]
        self.mock_openai_client.embeddings.create.return_value = mock_response
        
        texts = ["text1", "text2"]
        embeddings = self.vector_store.generate_embeddings(texts)
        
        self.assertEqual(embeddings.shape, (2, 1536))
        self.mock_openai_client.embeddings.create.assert_called_once()
    
    @patch('src.vector_store.Collection')
    def test_add_documents(self, mock_collection_class):
        """Test adding documents to vector store"""
        # Mock collection
        mock_collection = Mock()
        self.vector_store.collection = mock_collection
        
        # Mock embeddings
        with patch.object(self.vector_store, 'generate_embeddings') as mock_gen:
            mock_gen.return_value = np.array([[0.1] * 1536, [0.2] * 1536])
            
            chunks = [
                {
                    'text': 'chunk1',
                    'metadata': {
                        'source': 'url1',
                        'title': 'title1',
                        'chunk_id': 0,
                        'total_chunks': 2
                    }
                },
                {
                    'text': 'chunk2',
                    'metadata': {
                        'source': 'url2',
                        'title': 'title2',
                        'chunk_id': 1,
                        'total_chunks': 2
                    }
                }
            ]
            
            self.vector_store.add_documents(chunks)
            
            # Verify collection insert was called
            mock_collection.insert.assert_called_once()
    
    def test_retrieve(self):
        """Test document retrieval"""
        # Mock collection search
        mock_collection = Mock()
        mock_hit = Mock()
        mock_hit.entity = Mock()
        mock_hit.entity.get.side_effect = lambda k: {
            'text': 'test text',
            'source': 'test source',
            'title': 'test title',
            'chunk_id': 0,
            'total_chunks': 1
        }.get(k)
        mock_hit.distance = 0.95
        
        mock_result = [[mock_hit]]
        mock_collection.search.return_value = mock_result
        
        self.vector_store.collection = mock_collection
        
        # Mock embeddings
        with patch.object(self.vector_store, 'generate_embeddings') as mock_gen:
            mock_gen.return_value = np.array([[0.1] * 1536])
            
            results = self.vector_store.retrieve("test query", top_k=1)
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['text'], 'test text')
            self.assertEqual(results[0]['distance'], 0.95)
    
    def test_get_collection_stats(self):
        """Test getting collection statistics"""
        mock_collection = Mock()
        mock_collection.num_entities = 100
        self.vector_store.collection = mock_collection
        
        stats = self.vector_store.get_collection_stats()
        
        self.assertEqual(stats['total_chunks'], 100)
        self.assertEqual(stats['collection_name'], 'test_collection')


if __name__ == '__main__':
    unittest.main()
