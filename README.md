# RAG Agent System Documentation

## Overview

This RAG (Retrieval-Augmented Generation) system is designed to intelligently decide whether to pull information from PDFs, CSV data, or both, based on sophisticated query analysis and intent recognition.

## How to Run the System

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment in /backend
cp .env.example .env
# Add your OpenAI API key to .env file

# Confirm data sources in .env match that in backend/data (PDF and CSV)

# Initialize data (processes PDF and CSV)
python initialize_data.py

# Start the server
python app/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access the Application
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- API Documentation: http://localhost:8000/docs
