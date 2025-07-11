from typing import List, Dict
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

class EmbeddingManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
        
        # Create ChromaDB client with proper persistence
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )

    def get_collection(self, collection_name: str):
        """Get or create a ChromaDB collection."""
        return self.chroma_client.get_or_create_collection(collection_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.embeddings.embed_documents(texts)

    def query_similar(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        """Query similar documents from a collection."""
        collection = self.get_collection(collection_name)
        query_embedding = self.embeddings.embed_query(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return [
            {
                "text": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]