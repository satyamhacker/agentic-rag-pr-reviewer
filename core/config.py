from dotenv import load_dotenv
import os

load_dotenv()

# LangSmith tracing (Module 3 - Level 3.2)
# Reads LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY from .env automatically

# LLM config — used across all modules
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ChromaDB config — used in ingest.py and tools/rag_retriever.py
CHROMA_PERSIST_DIR = "./database/chroma_db"
CHROMA_COLLECTION_NAME = "rag_app"

# PDF source folder — used in ingest.py (Module 1 - Level 1.1)
PDF_SOURCE_DIR = "./knowledge_base_pdf"
