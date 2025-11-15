"""
Unit tests for the RAG pipeline module
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.rag_pipeline import RAGPipeline


class TestRAGPipeline(unittest.TestCase):
    """Test cases for RAGPipeline"""
    
    @patch('src.rag_pipeline.ChatOpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def setUp(self, mock_chat):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        mock_chat.return_value = self.mock_llm
        
        self.mock_vector_store = Mock()
        self.pipeline = RAGPipeline(
            vector_store=self.mock_vector_store,
            model_name="gpt-4o",
            top_k=5
        )
    
    def test_initialization(self):
        """Test pipeline initialization"""
        self.assertEqual(self.pipeline.top_k, 5)
        self.assertEqual(len(self.pipeline.chat_history), 0)
    
    def test_check_query_relevance_relevant(self):
        """Test relevance checking for relevant query"""
        mock_response = Mock()
        mock_response.content = "RELEVANT - This is about PostgreSQL"
        self.mock_llm.invoke.return_value = mock_response
        
        is_relevant, explanation = self.pipeline.check_query_relevance(
            "How do I create a table in PostgreSQL?"
        )
        
        self.assertTrue(is_relevant)
        self.assertIn("RELEVANT", explanation)
    
    def test_check_query_relevance_irrelevant(self):
        """Test relevance checking for irrelevant query"""
        mock_response = Mock()
        mock_response.content = "IRRELEVANT - This is about cooking"
        self.mock_llm.invoke.return_value = mock_response
        
        is_relevant, explanation = self.pipeline.check_query_relevance(
            "How do I make pizza?"
        )
        
        self.assertFalse(is_relevant)
    
    def test_format_chat_history_empty(self):
        """Test formatting empty chat history"""
        history = self.pipeline.format_chat_history()
        self.assertEqual(history, "No previous conversation")
    
    def test_format_chat_history_with_messages(self):
        """Test formatting chat history with messages"""
        self.pipeline.chat_history = [
            {'role': 'user', 'content': 'Question 1'},
            {'role': 'assistant', 'content': 'Answer 1'}
        ]
        
        history = self.pipeline.format_chat_history()
        self.assertIn("User: Question 1", history)
        self.assertIn("Assistant: Answer 1", history)
    
    def test_format_context(self):
        """Test formatting context from retrieved documents"""
        docs = [
            {
                'text': 'Document 1 content',
                'metadata': {'title': 'Title 1', 'source': 'url1'}
            },
            {
                'text': 'Document 2 content',
                'metadata': {'title': 'Title 2', 'source': 'url2'}
            }
        ]
        
        context = self.pipeline.format_context(docs)
        
        self.assertIn("Document 1 content", context)
        self.assertIn("Document 2 content", context)
        self.assertIn("Title 1", context)
        self.assertIn("Title 2", context)
    
    def test_answer_question_irrelevant(self):
        """Test answering irrelevant question"""
        # Mock relevance check to return False
        with patch.object(self.pipeline, 'check_query_relevance') as mock_check:
            mock_check.return_value = (False, "Not relevant")
            
            response = self.pipeline.answer_question(
                "What's the weather?",
                check_relevance=True
            )
            
            self.assertFalse(response['relevant'])
            self.assertEqual(len(response['sources']), 0)
    
    def test_answer_question_relevant(self):
        """Test answering relevant question"""
        # Mock relevance check
        with patch.object(self.pipeline, 'check_query_relevance') as mock_check:
            mock_check.return_value = (True, "Relevant")
            
            # Mock vector store retrieval
            self.mock_vector_store.retrieve.return_value = [
                {
                    'text': 'Test content',
                    'metadata': {'title': 'Test', 'source': 'url'},
                    'distance': 0.9
                }
            ]
            
            # Mock LLM response
            mock_response = Mock()
            mock_response.content = "This is the answer"
            self.mock_llm.invoke.return_value = mock_response
            
            response = self.pipeline.answer_question(
                "How do I create a table?",
                check_relevance=True
            )
            
            self.assertTrue(response['relevant'])
            self.assertEqual(response['answer'], "This is the answer")
            self.assertEqual(len(response['sources']), 1)
    
    def test_clear_history(self):
        """Test clearing chat history"""
        self.pipeline.chat_history = [
            {'role': 'user', 'content': 'Test'}
        ]
        
        self.pipeline.clear_history()
        
        self.assertEqual(len(self.pipeline.chat_history), 0)


if __name__ == '__main__':
    unittest.main()
