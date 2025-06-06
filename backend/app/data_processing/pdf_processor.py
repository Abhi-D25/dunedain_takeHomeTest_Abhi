from typing import List, Dict
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings
from dotenv import load_dotenv
load_dotenv()

class PDFProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
        self.chroma_client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_directory
        ))
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
        # Load PDF
        pages = self.load_pdf(settings.pdf_path)
        
        # Process each page
        for page_num, page_text in enumerate(pages, 1):
            chunks = self.chunk_text(page_text, page_num, settings.chunk_size, settings.chunk_overlap)
            
            # Add to ChromaDB
            for chunk in chunks:
                self.collection.add(
                    documents=[chunk["text"]],
                    metadatas=[chunk["metadata"]],
                    ids=[f"page_{page_num}_chunk_{chunk['metadata']['chunk_index']}"]
                ) 