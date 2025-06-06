from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    openai_api_key: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chroma_persist_directory: str = "./chroma_db"
    pdf_path: str = "./data/ARN42404-FM_5-0-000-WEB-1.pdf"
    csv_path: str = "./data/template_fields.csv"
    
    class Config:
        env_file = ".env"

settings = Settings() 