import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
import traceback
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ConversationMemory:
    """Simple in-memory conversation storage for sessions."""
    def __init__(self):
        self.conversations = {}
    
    def add_exchange(self, session_id: str, query: str, response: Dict):
        """Add a query-response exchange to session history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "intent": response.get("intent_analysis", {}),
            "strategy": response.get("strategy", {})
        })
        
        # Keep only last 10 exchanges per session
        if len(self.conversations[session_id]) > 10:
            self.conversations[session_id] = self.conversations[session_id][-10:]
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        return self.conversations.get(session_id, [])
    
    def get_recent_context(self, session_id: str, num_exchanges: int = 3) -> str:
        """Get recent conversation context for memory."""
        history = self.get_session_history(session_id)
        if not history:
            return ""
        
        recent = history[-num_exchanges:]
        context_parts = []
        
        for exchange in recent:
            context_parts.append(f"Previous Q: {exchange['query']}")
            context_parts.append(f"Previous A: {exchange['response'].get('answer', '')[:200]}...")
        
        return "\n".join(context_parts)

# Create router and memory
router = APIRouter()
conversation_memory = ConversationMemory()

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
    """Initialize the enhanced RAG agent with detailed error handling."""
    global agent
    
    logger.info("Starting enhanced agent initialization...")
    
    # First, test all dependencies
    dependency_issues = test_dependencies()
    if dependency_issues:
        logger.error("Dependency issues found:")
        for issue in dependency_issues:
            logger.error(f"  - {issue}")
        return False, dependency_issues
    
    try:
        # Import the enhanced agent class
        logger.info("Importing Enhanced RAGAgent...")
        from agent import RAGAgent
        
        # Initialize the agent
        logger.info("Creating Enhanced RAGAgent instance...")
        agent = RAGAgent()
        
        logger.info("Enhanced RAG Agent initialized successfully")
        return True, []
        
    except ImportError as e:
        error_msg = f"Failed to import Enhanced RAGAgent: {e}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, [error_msg]
    except Exception as e:
        error_msg = f"Failed to initialize Enhanced RAG Agent: {e}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, [error_msg]

@router.get("/api/debug")
async def debug_info():
    """Enhanced debug endpoint with agent reasoning insights."""
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
    
    # Test agent capabilities if available
    agent_capabilities = {}
    if agent is not None:
        try:
            # Test military term expansion
            test_query = "What is the role of S6 during MDMP?"
            expanded = agent.expand_military_terms(test_query)
            agent_capabilities["military_term_expansion"] = expanded != test_query.lower()
            
            # Test intent analysis
            intent = agent.analyze_query_intent(test_query)
            agent_capabilities["intent_analysis"] = intent.get("primary_intent") is not None
            
            # Test CSV search
            csv_results = agent.enhanced_csv_search("award bullet", intent)
            agent_capabilities["csv_search"] = len(csv_results) > 0
            
        except Exception as e:
            agent_capabilities["error"] = str(e)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "dependency_issues": dependency_issues,
        "agent_status": agent_status,
        "agent_errors": agent_errors,
        "agent_capabilities": agent_capabilities,
        "conversation_sessions": len(conversation_memory.conversations),
        "environment": {
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "working_directory": os.getcwd()
        }
    }

@router.get("/api/health")
async def health_check():
    """Enhanced health check endpoint."""
    global agent
    
    agent_status = "initialized" if agent is not None else "not_initialized"
    
    health_data = {
        "status": "healthy",
        "agent_status": agent_status,
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-enhanced",
        "features": {
            "hybrid_reasoning": True,
            "conversation_memory": True,
            "enhanced_search": True,
            "military_terminology": True
        }
    }
    
    if agent is not None:
        health_data["agent_capabilities"] = {
            "military_terms_supported": len(agent.military_terms),
            "csv_processor_ready": hasattr(agent, 'csv_processor'),
            "pdf_processor_ready": hasattr(agent, 'pdf_processor'),
            "embedding_manager_ready": hasattr(agent, 'embedding_manager')
        }
    
    return health_data

@router.get("/api/examples")
async def get_example_queries():
    """Enhanced example queries that specifically test the requirements."""
    return {
        "examples": [
            {
                "category": "Award Generation (Example 1)",
                "query": "Write an award bullet for a Soldier that got a 600 on their ACFT",
                "expected_tool": "csv + pdf (hybrid)",
                "description": "Should find ACFT context from PDF and award template from CSV"
            },
            {
                "category": "Information Retrieval (Example 2)", 
                "query": "What is the role of the S6 during MDMP?",
                "expected_tool": "pdf",
                "description": "Should search PDF for MDMP procedures and S6 roles"
            },
            {
                "category": "Hybrid Generation (Example 3)",
                "query": "Write a situation paragraph for my infantry battalion's upcoming mission at NTC",
                "expected_tool": "csv + pdf (hybrid)",
                "description": "Should use CSV for paragraph structure and PDF for military context"
            },
            {
                "category": "Template-Focused Generation",
                "query": "Create a character assessment for an NCO evaluation",
                "expected_tool": "csv",
                "description": "Should focus on evaluation report templates"
            },
            {
                "category": "Knowledge-Focused Query",
                "query": "Explain the steps of the military decision making process",
                "expected_tool": "pdf",
                "description": "Should provide detailed MDMP information from manuals"
            }
        ]
    }

@router.post("/api/query")
async def process_query(request: QueryRequest):
    """Enhanced query processing with conversation memory and detailed responses."""
    global agent
    
    # Initialize agent if not already done
    if agent is None:
        success, errors = initialize_agent()
        if not success:
            error_detail = "Failed to initialize enhanced RAG agent. Issues: " + "; ".join(errors)
            logger.error(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Get conversation context if session provided
        conversation_context = ""
        if request.session_id:
            conversation_context = conversation_memory.get_recent_context(request.session_id)
        
        # Process the query with enhanced agent
        logger.info(f"Processing enhanced query: {request.question[:50]}...")
        result = agent.process_query(request.question)
        
        # Store in conversation memory
        if request.session_id:
            conversation_memory.add_exchange(request.session_id, request.question, result)
        
        # Create enhanced response
        enhanced_response = {
            "answer": result["answer"],
            "sources": result["sources"],
            "tool_used": result["tool_used"],
            "confidence": result["confidence"],
            "reasoning_chain": result.get("reasoning_chain", {}),
            "strategy": result.get("strategy", {}),
            "intent_analysis": result.get("intent_analysis", {}),
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat(),
            "agent_version": "enhanced-v2.0"
        }
        
        # Add conversation history if available
        if request.session_id:
            history = conversation_memory.get_session_history(request.session_id)
            enhanced_response["conversation_length"] = len(history)
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Error processing enhanced query: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your query: {str(e)}"
        )

@router.get("/api/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    history = conversation_memory.get_session_history(session_id)
    
    return {
        "session_id": session_id,
        "conversation_length": len(history),
        "history": history,
        "timestamp": datetime.now().isoformat()
    }

@router.delete("/api/conversation/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session."""
    if session_id in conversation_memory.conversations:
        del conversation_memory.conversations[session_id]
        return {"message": f"Conversation history cleared for session {session_id}"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/api/agent/reasoning/{session_id}")
async def get_reasoning_analysis(session_id: str):
    """Get detailed reasoning analysis for recent queries in a session."""
    history = conversation_memory.get_session_history(session_id)
    
    reasoning_analysis = []
    for exchange in history[-5:]:  # Last 5 exchanges
        reasoning_data = {
            "query": exchange["query"],
            "timestamp": exchange["timestamp"],
            "intent_detected": exchange.get("intent", {}),
            "strategy_used": exchange.get("strategy", {}),
            "sources_found": {
                "csv_count": len(exchange["response"].get("sources", {}).get("csv_results", [])),
                "pdf_count": len(exchange["response"].get("sources", {}).get("pdf_results", []))
            }
        }
        reasoning_analysis.append(reasoning_data)
    
    return {
        "session_id": session_id,
        "reasoning_analysis": reasoning_analysis,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/api/status")
async def get_status():
    """Get detailed enhanced system status."""
    global agent
    
    try:
        status = {
            "agent_initialized": agent is not None,
            "timestamp": datetime.now().isoformat(),
            "version": "enhanced-v2.0",
            "features_active": {
                "hybrid_reasoning": True,
                "conversation_memory": True,
                "enhanced_search": True,
                "military_terminology": True,
                "intent_analysis": True
            }
        }
        
        if agent is not None:
            status.update({
                "csv_processor_ready": hasattr(agent, 'csv_processor') and agent.csv_processor is not None,
                "pdf_processor_ready": hasattr(agent, 'pdf_processor') and agent.pdf_processor is not None,
                "embedding_manager_ready": hasattr(agent, 'embedding_manager') and agent.embedding_manager is not None,
                "llm_ready": hasattr(agent, 'llm') and agent.llm is not None,
                "military_terms_loaded": len(getattr(agent, 'military_terms', {})),
                "conversation_sessions_active": len(conversation_memory.conversations)
            })
            
            # Test core functionalities
            try:
                test_intent = agent.analyze_query_intent("test query")
                status["intent_analysis_working"] = test_intent is not None
            except:
                status["intent_analysis_working"] = False
        
        return status
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "agent_initialized": False
        }