"""
(NAYA) Configuration & Agnostic Setup (Level 2.1)
Yahan local LLM wrappers aur LangSmith telemetry set hogi.
"""
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import OLLAMA_MODEL, OLLAMA_EMBEDDING_MODEL

# Load environment variables
load_dotenv()

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize local LLM and embeddings
local_llm = ChatOllama(model=OLLAMA_MODEL)
local_embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

# Initialize fallback LLM (Google Gemini)
fallback_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Export for test files
__all__ = ["local_llm", "local_embeddings", "fallback_llm", "OLLAMA_MODEL"]
