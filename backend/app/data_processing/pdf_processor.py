import sys
import os
from typing import List, Dict
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import chromadb
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from dotenv import load_dotenv
load_dotenv()

class PDFProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
        
        # Use PersistentClient to ensure data persists
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
        self.collection = self.chroma_client.get_or_create_collection("pdf_documents")

    def load_pdf(self, file_path: str) -> List[str]:
        """Load PDF and extract text from each page."""
        pages = []
        with open(file_path, 'rb') as file:
            pdf = pypdf.PdfReader(file)
            for page in pdf.pages:
                pages.append(page.extract_text())
        return pages

    def chunk_text(self, page_text: str, page_num: int, chunk_size: int, overlap: int) -> List[Dict]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
        )
        
        chunks = text_splitter.split_text(page_text)
        return [
            {
                "text": chunk,
                "metadata": {
                    "source": "ARN42404-FM_5-0-000-WEB-1.pdf",
                    "page": page_num,
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]

    def process_pdf_to_vectorstore(self) -> None:
        """Process PDF and store in ChromaDB."""
        print(f"Loading PDF from: {settings.pdf_path}")
        
        # Force delete and recreate collection to fix dimension mismatch
        try:
            self.chroma_client.delete_collection("pdf_documents")
            print("Deleted existing collection")
        except:
            print("No existing collection to delete")
        
        # Create fresh collection with no default embedding function
        self.collection = self.chroma_client.create_collection(
            name="pdf_documents",
            embedding_function=None  # This prevents ChromaDB from using default embeddings
        )
        print("Created fresh collection without default embedding function")
        
        # Load PDF
        pages = self.load_pdf(settings.pdf_path)
        print(f"Loaded PDF with {len(pages)} pages")
        
        # Process each page and generate embeddings
        all_documents = []
        all_metadatas = []
        all_ids = []
        all_embeddings = []
        
        for page_num, page_text in enumerate(pages, 1):
            if not page_text.strip():  # Skip empty pages
                continue
                
            chunks = self.chunk_text(page_text, page_num, settings.chunk_size, settings.chunk_overlap)
            print(f"Page {page_num}: Created {len(chunks)} chunks")
            
            # Collect all chunks for batch processing
            for chunk in chunks:
                all_documents.append(chunk["text"])
                all_metadatas.append(chunk["metadata"])
                all_ids.append(f"page_{page_num}_chunk_{chunk['metadata']['chunk_index']}")
        
        print(f"Total chunks to process: {len(all_documents)}")
        
        # Generate embeddings for all documents
        print("Generating embeddings...")
        all_embeddings = self.embeddings.embed_documents(all_documents)
        print(f"Generated {len(all_embeddings)} embeddings, dimension: {len(all_embeddings[0])}")
        
        # Add all documents in batches with embeddings
        batch_size = 100
        for i in range(0, len(all_documents), batch_size):
            batch_docs = all_documents[i:i+batch_size]
            batch_metas = all_metadatas[i:i+batch_size]
            batch_ids = all_ids[i:i+batch_size]
            batch_embeddings = all_embeddings[i:i+batch_size]
            
            print(f"Processing batch {i//batch_size + 1}: {len(batch_docs)} documents")
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids,
                embeddings=batch_embeddings  # Provide our own embeddings
            )
        
        # Verify storage
        final_count = self.collection.count()
        print(f"Successfully stored {final_count} documents in ChromaDB")
        
        # Test a simple query with OpenAI embeddings
        test_embedding = self.embeddings.embed_query("military decision making process")
        print(f"Test embedding dimension: {len(test_embedding)}")
        
        test_results = self.collection.query(
            query_embeddings=[test_embedding],
            n_results=3
        )
        print(f"Test query returned {len(test_results['documents'][0])} results")
        if test_results['documents'][0]:
            print(f"Sample result: {test_results['documents'][0][0][:100]}...")