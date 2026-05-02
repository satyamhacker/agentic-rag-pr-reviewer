"""
(NAYA) Configuration & Agnostic Setup (Level 2.1)
Yahan local LLM wrappers aur LangSmith telemetry set hogi.
"""
import os
import sys
from dotenv import load_dotenv
from langchain_core.tracers.langchain import LangChainTracer

# Ensure we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import OLLAMA_MODEL, OLLAMA_EMBEDDING_MODEL

# Load environment variables
load_dotenv()

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# 1️⃣ Local LLM & Embeddings (Under Test)
local_llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.7)
local_embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

# 2️⃣ Cloud Fallback (Zero Downtime)
fallback_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 3️⃣ 🔥 LANGSMITH TRACER (EVAL ONLY)
# Note: project_name alag rakhne se dashboard mein traffic mix nahi hoga
eval_tracer = LangChainTracer(
    project_name="llm-eval-suite",
    api_key=os.getenv("LANGCHAIN_API_KEY")
)

# Export for test files
__all__ = ["local_llm", "local_embeddings", "fallback_llm", "OLLAMA_MODEL", "eval_tracer"]
