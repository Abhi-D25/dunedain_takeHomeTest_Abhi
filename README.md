# RAG Agent System

A Retrieval-Augmented Generation (RAG) system with a FastAPI backend and React frontend.

## Setup

1. Backend Setup:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Frontend Setup:
   ```bash
   cd frontend
   npm install
   ```

3. Environment Setup:
   - Copy `backend/.env.example` to `backend/.env`
   - Add your OpenAI API key to the `.env` file

4. Running the Application:
   - Backend: 
     ```bash
     cd backend
     python app/main.py
     ```
   - Frontend:
     ```bash
     cd frontend
     npm run dev
     ```

The backend will be available at http://localhost:8000 and the frontend at http://localhost:5173.

## Features

- FastAPI backend with CORS support
- React frontend with Vite
- OpenAI integration
- Document processing capabilities
- Vector database integration with ChromaDB 