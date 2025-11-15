"""
Unit tests for the scraper module
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.scraper import PostgresDocScraper, DocumentChunker


class TestPostgresDocScraper(unittest.TestCase):
    """Test cases for PostgresDocScraper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = PostgresDocScraper(output_dir="test_data")
    
    def test_initialization(self):
        """Test scraper initialization"""
        self.assertEqual(self.scraper.output_dir, "test_data")
        self.assertEqual(len(self.scraper.URLS), 35)
        self.assertIsNotNone(self.scraper.html_converter)
    
    @patch('src.scraper.requests.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetching"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = "<html><head><title>Test Page</title></head><body>Test content</body></html>"
        mock_response.text = "<html><head><title>Test Page</title></head><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_page("https://example.com/test")
        
        self.assertEqual(result['title'], "Test Page")
        self.assertIn("Test content", result['content'])
    
    @patch('src.scraper.requests.get')
    def test_fetch_page_failure(self, mock_get):
        """Test page fetching with error"""
        mock_get.side_effect = Exception("Network error")
        
        url = "https://example.com/test"
        result = self.scraper.fetch_page(url)
        
        self.assertEqual(result['url'], url)
        self.assertEqual(result['content'], '')
    
    def test_fetch_all_with_max_docs(self):
        """Test fetching with max_docs limit"""
        with patch.object(self.scraper, 'fetch_page') as mock_fetch:
            mock_fetch.return_value = {
                'url': 'test', 
                'title': 'Test', 
                'content': 'Content'
            }
            
            docs = self.scraper.fetch_all(max_docs=3, delay=0)
            
            self.assertEqual(len(docs), 3)
            self.assertEqual(mock_fetch.call_count, 3)


class TestDocumentChunker(unittest.TestCase):
    """Test cases for DocumentChunker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    
    def test_initialization(self):
        """Test chunker initialization"""
        self.assertIsNotNone(self.chunker.text_splitter)
    
    def test_chunk_documents(self):
        """Test document chunking"""
        documents = [
            {
                'url': 'https://example.com/test',
                'title': 'Test Doc',
                'content': 'A' * 250  # Long content to ensure chunking
            }
        ]
        
        chunks = self.chunker.chunk_documents(documents)
        
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]['metadata']['source'], documents[0]['url'])
        self.assertEqual(chunks[0]['metadata']['title'], documents[0]['title'])
        self.assertIn('text', chunks[0])
        self.assertIn('chunk_id', chunks[0]['metadata'])
    
    def test_chunk_documents_with_max_chunks(self):
        """Test chunking with max_chunks_per_doc limit"""
        documents = [
            {
                'url': 'https://example.com/test',
                'title': 'Test Doc',
                'content': 'A' * 500  # Long content
            }
        ]
        
        chunks = self.chunker.chunk_documents(documents, max_chunks_per_doc=2)
        
        self.assertLessEqual(len(chunks), 2)
    
    def test_chunk_empty_documents(self):
        """Test chunking empty document list"""
        chunks = self.chunker.chunk_documents([])
        self.assertEqual(len(chunks), 0)


if __name__ == '__main__':
    unittest.main()
