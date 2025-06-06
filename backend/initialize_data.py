import os
from app.data_processing import PDFProcessor, CSVProcessor, EmbeddingManager
from app.config import settings

def initialize_data():
    print("Starting data initialization...")
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    csv_processor = CSVProcessor()
    embedding_manager = EmbeddingManager()
    
    # Process PDF
    print("\nProcessing PDF file...")
    try:
        pdf_processor.process_pdf_to_vectorstore()
        print("✓ PDF processing completed successfully")
    except Exception as e:
        print(f"✗ Error processing PDF: {str(e)}")
        return False
    
    # Process CSV
    print("\nProcessing CSV file...")
    try:
        index = csv_processor.process_csv()
        print(f"✓ CSV processing completed successfully. Indexed {len(index)} entries")
    except Exception as e:
        print(f"✗ Error processing CSV: {str(e)}")
        return False
    
    # Verify ChromaDB persistence
    print("\nVerifying ChromaDB persistence...")
    try:
        collection = embedding_manager.get_collection("pdf_documents")
        count = collection.count()
        print(f"✓ ChromaDB verification successful. Found {count} documents")
    except Exception as e:
        print(f"✗ Error verifying ChromaDB: {str(e)}")
        return False
    
    print("\nData initialization completed successfully!")
    return True

if __name__ == "__main__":
    # Verify environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        exit(1)
    
    # Run initialization
    success = initialize_data()
    exit(0 if success else 1) 