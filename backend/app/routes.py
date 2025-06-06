import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import logging
import traceback
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

# Create router
router = APIRouter()

# Global agent instance
agent = None

def test_dependencies():
    """Test all dependencies before initializing agent."""
    issues = []
    
    # Test OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY environment variable not set")
    
    # Test imports
    try:
        from langchain_openai import ChatOpenAI
        logger.info("✓ langchain_openai import successful")
    except ImportError as e:
        issues.append(f"Failed to import langchain_openai: {e}")
    
    try:
        import chromadb
        logger.info("✓ chromadb import successful")
    except ImportError as e:
        issues.append(f"Failed to import chromadb: {e}")
    
    try:
        from data_processing.pdf_processor import PDFProcessor
        from data_processing.csv_processor import CSVProcessor  
        from data_processing.embeddings import EmbeddingManager
        logger.info("✓ data_processing imports successful")
    except ImportError as e:
        issues.append(f"Failed to import data_processing: {e}")
    
    try:
        from config import settings
        logger.info("✓ config import successful")
        logger.info(f"✓ PDF path: {settings.pdf_path}")
        logger.info(f"✓ CSV path: {settings.csv_path}")
        logger.info(f"✓ ChromaDB path: {settings.chroma_persist_directory}")
    except ImportError as e:
        issues.append(f"Failed to import config: {e}")
    
    # Test file existence
    try:
        from config import settings
        if not os.path.exists(settings.pdf_path):
            issues.append(f"PDF file not found at: {settings.pdf_path}")
        if not os.path.exists(settings.csv_path):
            issues.append(f"CSV file not found at: {settings.csv_path}")
        if not os.path.exists(settings.chroma_persist_directory):
            issues.append(f"ChromaDB directory not found at: {settings.chroma_persist_directory}")
    except Exception as e:
        issues.append(f"Error checking file paths: {e}")
    
    return issues

def initialize_agent():
    """Initialize the RAG agent with detailed error handling."""
    global agent
    
    logger.info("Starting agent initialization...")
    
    # First, test all dependencies
    dependency_issues = test_dependencies()
    if dependency_issues:
        logger.error("Dependency issues found:")
        for issue in dependency_issues:
            logger.error(f"  - {issue}")
        return False, dependency_issues
    
    try:
        # Import the agent class
        logger.info("Importing RAGAgent...")
        from agent import RAGAgent
        
        # Initialize the agent
        logger.info("Creating RAGAgent instance...")
        agent = RAGAgent()
        
        logger.info("RAG Agent initialized successfully")
        return True, []
        
    except ImportError as e:
        error_msg = f"Failed to import RAGAgent: {e}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, [error_msg]
    except Exception as e:
        error_msg = f"Failed to initialize RAG Agent: {e}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, [error_msg]

@router.get("/api/debug")
async def debug_info():
    """Debug endpoint to check system state."""
    global agent
    
    # Test dependencies
    dependency_issues = test_dependencies()
    
    # Try to initialize agent if not already done
    agent_status = "not_attempted"
    agent_errors = []
    
    if agent is None:
        success, errors = initialize_agent()
        if success:
            agent_status = "initialized"
        else:
            agent_status = "failed"
            agent_errors = errors
    else:
        agent_status = "already_initialized"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "dependency_issues": dependency_issues,
        "agent_status": agent_status,
        "agent_errors": agent_errors,
        "environment": {
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "working_directory": os.getcwd()
        }
    }

@router.get("/api/health")
async def health_check():
    """Health check endpoint."""
    global agent
    
    agent_status = "initialized" if agent is not None else "not_initialized"
    
    return {
        "status": "healthy",
        "agent_status": agent_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/api/examples")
async def get_example_queries():
    """Get example queries for testing the system."""
    return {
        "examples": [
            {
                "category": "Award Generation",
                "query": "Write an award bullet for a Soldier that got a 600 on their ACFT",
                "expected_tool": "csv"
            },
            {
                "category": "Information Retrieval", 
                "query": "What is the role of the S6 during MDMP?",
                "expected_tool": "pdf"
            },
            {
                "category": "Hybrid Query",
                "query": "Write a situation paragraph for my infantry battalion's upcoming mission at NTC",
                "expected_tool": "csv with pdf support"
            }
        ]
    }

@router.post("/api/query")
async def process_query(request: QueryRequest):
    """Main endpoint for processing user queries."""
    global agent
    
    # Initialize agent if not already done
    if agent is None:
        success, errors = initialize_agent()
        if not success:
            error_detail = "Failed to initialize RAG agent. Issues: " + "; ".join(errors)
            logger.error(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Process the query
        logger.info(f"Processing query: {request.question[:50]}...")
        result = agent.process_query(request.question)
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "tool_used": result["tool_used"],
            "confidence": result["confidence"],
            "classification": result["classification"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your query: {str(e)}"
        )

@router.get("/api/status")
async def get_status():
    """Get detailed system status."""
    global agent
    
    try:
        status = {
            "agent_initialized": agent is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        if agent is not None:
            status.update({
                "csv_processor_ready": hasattr(agent, 'csv_processor') and agent.csv_processor is not None,
                "pdf_processor_ready": hasattr(agent, 'pdf_processor') and agent.pdf_processor is not None,
                "embedding_manager_ready": hasattr(agent, 'embedding_manager') and agent.embedding_manager is not None,
                "llm_ready": hasattr(agent, 'llm') and agent.llm is not None
            })
        
        return status
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
