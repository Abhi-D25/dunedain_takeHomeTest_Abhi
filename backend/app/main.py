from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Agent API",
    description="A Retrieval-Augmented Generation system for military documents and templates",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import and include routes with better error handling
try:
    from routes import router
    app.include_router(router)
    logger.info("Routes loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import routes: {e}")
    logger.error("Make sure routes.py exists in the same directory as main.py")
except Exception as e:
    logger.error(f"Unexpected error loading routes: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting RAG Agent API...")
    logger.info(f"OpenAI API Key configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Agent API",
        "status": "running",
        "docs": "/docs"
    }

# Basic health check as fallback
@app.get("/health")
async def basic_health():
    """Basic health check."""
    return {"status": "healthy", "message": "Basic health check"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)