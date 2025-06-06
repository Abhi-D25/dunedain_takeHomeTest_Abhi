import unittest
import os
from app.data_processing import PDFProcessor, CSVProcessor, EmbeddingManager
from app.config import settings

class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        self.pdf_processor = PDFProcessor()
        self.csv_processor = CSVProcessor()
        self.embedding_manager = EmbeddingManager()

    def test_pdf_processing(self):
        """Test PDF loading and chunking."""
        # Ensure PDF exists
        self.assertTrue(os.path.exists(settings.pdf_path))
        
        # Test PDF loading
        pages = self.pdf_processor.load_pdf(settings.pdf_path)
        self.assertIsInstance(pages, list)
        self.assertTrue(len(pages) > 0)
        
        # Test chunking
        chunks = self.pdf_processor.chunk_text(pages[0], settings.chunk_size, settings.chunk_overlap)
        self.assertIsInstance(chunks, list)
        self.assertTrue(len(chunks) > 0)
        self.assertIn("text", chunks[0])
        self.assertIn("metadata", chunks[0])

    def test_csv_processing(self):
        """Test CSV loading and searching."""
        # Ensure CSV exists
        self.assertTrue(os.path.exists(settings.csv_path))
        
        # Test CSV loading
        df = self.csv_processor.load_csv(settings.csv_path)
        self.assertIsNotNone(df)
        
        # Test index creation
        index = self.csv_processor.create_search_index(df)
        self.assertIsInstance(index, dict)
        self.assertTrue(len(index) > 0)
        
        # Test exact search
        exact_results = self.csv_processor.search_exact("DA638")
        self.assertIsInstance(exact_results, list)
        
        # Test fuzzy search
        fuzzy_results = self.csv_processor.search_fuzzy("DA638", threshold=0.6)
        self.assertIsInstance(fuzzy_results, list)

    def test_embeddings(self):
        """Test embedding generation and similarity search."""
        # Test embedding generation
        texts = ["Test document 1", "Test document 2"]
        embeddings = self.embedding_manager.generate_embeddings(texts)
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), len(texts))
        
        # Test collection creation
        collection = self.embedding_manager.get_collection("test_collection")
        self.assertIsNotNone(collection)

if __name__ == '__main__':
    unittest.main() 