import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Optional
import re
from langchain_openai import ChatOpenAI
from data_processing.pdf_processor import PDFProcessor
from data_processing.csv_processor import CSVProcessor  
from data_processing.embeddings import EmbeddingManager
from config import settings

class RAGAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        self.pdf_processor = PDFProcessor()
        self.csv_processor = CSVProcessor()
        self.embedding_manager = EmbeddingManager()
        
        # Load CSV data
        self.csv_processor.process_csv()

    def classify_query(self, query: str) -> Dict[str, any]:
        """
        Classify the user query to determine which tools to use.
        The CSV contains system prompts/output formats for specific fields in PDF documents.
        Default to PDF, but ask for clarification when ambiguous.
        """
        query_lower = query.lower()
        
        # Keywords that clearly indicate form/document generation (CSV use)
        form_generation_keywords = [
            'write', 'create', 'generate', 'draft', 'compose', 'bullet', 'award', 
            'evaluation', 'citation', 'recommendation', 'da638', 'da form',
            'template', 'format'
        ]
        
        # Keywords that indicate information seeking (PDF use)  
        info_seeking_keywords = [
            'what', 'how', 'explain', 'describe', 'define', 'tell me', 'role', 
            'process', 'procedure', 'steps', 'during', 'why', 'when', 'where'
        ]
        
        # Military context that might benefit from both sources
        military_context_keywords = [
            'mdmp', 'mission', 'operation', 'training', 'ntc', 'deployment', 
            'exercise', 'planning', 'staff', 's1', 's2', 's3', 's4', 's5', 's6'
        ]
        
        # Ambiguous phrases that warrant clarification
        ambiguous_phrases = [
            'help with', 'need to', 'working on', 'assistance', 'support'
        ]
        
        # Count keyword matches
        form_score = sum(1 for keyword in form_generation_keywords if keyword in query_lower)
        info_score = sum(1 for keyword in info_seeking_keywords if keyword in query_lower)
        context_score = sum(1 for keyword in military_context_keywords if keyword in query_lower)
        ambiguous_score = sum(1 for phrase in ambiguous_phrases if phrase in query_lower)
        
        # Check for ambiguous queries that need clarification
        if ambiguous_score > 0 and (form_score == 0 and info_score == 0):
            return {
                "primary_tool": "clarification",
                "secondary_tool": None,
                "confidence": "low",
                "reasoning": "Query is ambiguous and would benefit from clarification"
            }
        
        # Clear form generation with military context (use both)
        if form_score > 0 and context_score > 0:
            return {
                "primary_tool": "csv",
                "secondary_tool": "pdf", 
                "confidence": "high",
                "reasoning": "Document generation request with military context - using CSV for format and PDF for context"
            }
        
        # Clear form generation only
        if form_score > 0 and info_score == 0:
            return {
                "primary_tool": "csv",
                "secondary_tool": None,
                "confidence": "high", 
                "reasoning": "Clear document generation request - using CSV for format/template"
            }
        
        # Clear information seeking
        if info_score > 0 and form_score == 0:
            return {
                "primary_tool": "pdf",
                "secondary_tool": None,
                "confidence": "high",
                "reasoning": "Information retrieval request - using PDF documents"
            }
        
        # Mixed signals - use both sources
        if form_score > 0 and info_score > 0:
            return {
                "primary_tool": "pdf",
                "secondary_tool": "csv",
                "confidence": "medium",
                "reasoning": "Mixed generation and information request - using both sources"
            }
        
        # Default to PDF as specified
        return {
            "primary_tool": "pdf",
            "secondary_tool": None,
            "confidence": "low",
            "reasoning": "Defaulting to PDF document search as fallback"
        }

    def search_csv(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search CSV data for relevant template information."""
        # Try exact search first
        exact_results = self.csv_processor.search_exact(query)
        if exact_results:
            return exact_results[:max_results]
        
        # Fall back to fuzzy search with lower threshold for better matches
        fuzzy_results = self.csv_processor.search_fuzzy(query, threshold=0.3)
        return fuzzy_results[:max_results]

    def search_pdf(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search PDF documents for relevant information."""
        try:
            results = self.embedding_manager.query_similar(
                collection_name="pdf_documents",
                query=query,
                n_results=max_results
            )
            return results
        except Exception as e:
            print(f"Error searching PDF: {str(e)}")
            return []

    def generate_clarification_request(self, query: str) -> Dict:
        """Generate a clarification request for ambiguous queries."""
        return {
            "answer": f"I'd be happy to help with '{query}'. To provide the most accurate assistance, could you clarify:\n\n" +
                     "- Are you looking to CREATE/WRITE a document (like an award citation, evaluation, or form)?\n" +
                     "- Are you seeking INFORMATION about military procedures, processes, or roles?\n" +
                     "- Is this related to a specific form (like DA638) or military process (like MDMP)?\n\n" +
                     "Please provide a bit more detail so I can give you the best possible response.",
            "sources_used": {"csv_sources": 0, "pdf_sources": 0},
            "tool_used": "clarification",
            "confidence": "high"
        }

    def generate_response(self, query: str, csv_results: List[Dict], pdf_results: List[Dict], 
                         classification: Dict) -> Dict:
        """Generate a response using the LLM with retrieved context."""
        
        # Handle clarification requests
        if classification["primary_tool"] == "clarification":
            return self.generate_clarification_request(query)
        
        # Build context from results
        context_parts = []
        
        if csv_results:
            context_parts.append("=== DOCUMENT FORMAT/TEMPLATE INFORMATION ===")
            for result in csv_results:
                context_parts.append(
                    f"Template: {result.get('template_name', 'Unknown')}\n"
                    f"Field: {result.get('field_label', 'Unknown')}\n"
                    f"Format Instructions: {result.get('instructions', 'No instructions')}\n"
                )
        
        if pdf_results:
            context_parts.append("=== MILITARY PROCEDURE/KNOWLEDGE INFORMATION ===")
            for result in pdf_results:
                metadata = result.get('metadata', {})
                context_parts.append(
                    f"Source: {metadata.get('source', 'Unknown')} (Page {metadata.get('page', 'Unknown')})\n"
                    f"Content: {result.get('text', '')}\n"
                )
        
        context = "\n".join(context_parts)
        
        # Create enhanced prompts based on classification
        if classification["primary_tool"] == "csv":
            if classification["secondary_tool"] == "pdf":
                # Hybrid: CSV primary with PDF context
                system_prompt = """You are a military document assistant. You specialize in creating military documents using proper formats while incorporating relevant military knowledge.

The CSV data provides specific formatting instructions and templates for military documents. The PDF data provides additional military context and procedures.

When generating documents:
1. Follow the formatting instructions from the template data exactly
2. Incorporate relevant military knowledge and context from the procedures
3. Use appropriate military language, terminology, and standards
4. Be concise, professional, and accurate"""
            else:
                # CSV only
                system_prompt = """You are a military document assistant specializing in creating military forms and documents. 

Use the provided template information to generate the requested content. Follow the specific formatting instructions provided for each field exactly. Be concise, professional, and use appropriate military language and standards."""
        else:
            # PDF primary or PDF only
            system_prompt = """You are a military knowledge assistant. Use the provided military document information to answer questions about military procedures, processes, and information. 

Be accurate, detailed, and cite the source when possible. Use proper military terminology and provide comprehensive explanations."""
        
        # Generate response
        if not context.strip():
            # No relevant context found
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"I couldn't find specific relevant information for: {query}\n\nPlease provide a general response based on standard military knowledge, but note that more specific information might be available with a more targeted query."}
            ]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nUser Request: {query}"}
            ]
        
        try:
            response = self.llm.invoke(messages)
            return {
                "answer": response.content,
                "sources_used": {
                    "csv_sources": len(csv_results),
                    "pdf_sources": len(pdf_results)
                },
                "tool_used": classification["primary_tool"],
                "confidence": classification["confidence"]
            }
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error generating a response: {str(e)}",
                "sources_used": {"csv_sources": 0, "pdf_sources": 0},
                "tool_used": "error",
                "confidence": "none"
            }

    def process_query(self, query: str) -> Dict:
        """Main method to process a user query."""
        
        # Step 1: Classify the query
        classification = self.classify_query(query)
        
        # Step 2: Search relevant sources
        csv_results = []
        pdf_results = []
        
        if classification["primary_tool"] == "csv" or classification["secondary_tool"] == "csv":
            csv_results = self.search_csv(query)
        
        if classification["primary_tool"] == "pdf" or classification["secondary_tool"] == "pdf":
            pdf_results = self.search_pdf(query)
        
        # Step 3: Generate response
        response = self.generate_response(query, csv_results, pdf_results, classification)
        
        # Step 4: Add metadata
        response.update({
            "classification": classification,
            "sources": {
                "csv_results": csv_results,
                "pdf_results": [
                    {
                        "text": r.get("text", "")[:200] + "...",  # Truncate for response
                        "page": r.get("metadata", {}).get("page"),
                        "source": r.get("metadata", {}).get("source")
                    }
                    for r in pdf_results
                ]
            }
        })
        
        return response