# 📁 Project Folder & File Structure

> **For Beginners:** This document explains every file and folder in this project so you know exactly where to go when you want to make a change.

---

## 🗂️ High-Level Overview

```
agentic-rag-pr-reviewer/
│
├── 📄 main.py                        ← Entry point — run this to start the agent
├── 📄 .env                           ← Secret keys and model config (never commit this!)
├── 📄 requirements.txt               ← All Python dependencies to install
├── 📄 README.md                      ← Basic project overview
├── 📄 folder_file_structure.md       ← THIS FILE — project navigation guide
│
├── 📁 config/                        ← Global configuration (model names, DB paths)
│   ├── __init__.py
│   └── config.py
│
├── 📁 tools/                         ← All agent tools + helper logic
│   ├── __init__.py
│   ├── all_tools.py                  ← Define every @tool here (HTML, JS, SQL, Web search)
│   ├── binding_tools_to_llm.py       ← Wire tools to the LLM (master list + registry)
│   ├── rag_retriever.py              ← ChromaDB vector search logic
│   ├── data_filter.py                ← LLM-based noise filter for retrieved results
│   ├── pdf_to_embeddings.py          ← Ingest PDFs → chunk → embed → store in ChromaDB
│   ├── code_repl.py                  ← Python REPL tool (execute code at runtime)
│   └── web_scraper.py                ← Playwright browser tool (navigate + get elements)
│
├── 📁 database/                      ← Persistent vector store (auto-generated)
│   └── chroma_db/                    ← ChromaDB files live here (do NOT edit manually)
│
└── 📁 knowledge_base_pdf/            ← Drop your PDF files here to add to the knowledge base
    ├── html_cheatsheet.pdf
    ├── javascript_cheatsheet.pdf
    └── mysql_cheatsheet.pdf
```

---

## 📄 Root-Level Files

### `main.py`
**The application entry point.** Run `python main.py` to start the interactive agent loop.

- Pulls the RAG prompt from LangChain Hub (`rlm/rag-prompt:50442af1`)
- Starts a terminal loop to accept user questions
- Streams the LLM response in real-time
- Detects if the LLM requested a tool call → executes the tool → passes raw result to `MistralDataFilter` for cleanup
- Prints the final filtered, relevant answer

> 🔧 **If you want to:** Change how the agent responds, add logging, or modify the main conversation loop → **edit this file.**

---

### `.env`
**Environment variables and secret keys.** Never commit this file to git.

Contains:
- `OLLAMA_MODEL` → The main LLM model (default: `qwen2.5:7b`)
- `OLLAMA_EMBEDDING_MODEL` → Model for generating embeddings (default: `nomic-embed-text`)
- `OLLAMA_FILTER_MODEL` → Model for filtering tool results (default: `qwen2.5:7b`)
- `LANGCHAIN_API_KEY` → LangSmith API key for tracing/monitoring
- `LANGCHAIN_TRACING_V2` → Enable/disable LangSmith tracing (`true`/`false`)
- `HUGGINGFACE_API_KEY` → HuggingFace key (for future smolagents integration)

> 🔧 **If you want to:** Switch the LLM model, enable LangSmith tracing, or add a new API key → **edit this file.**

---

### `requirements.txt`
**All Python packages needed to run this project.**

Key dependencies:
- `langchain`, `langchain-community`, `langchain-core` → Core agentic framework
- `langchain-ollama` → Connect to locally running Ollama models
- `langchain-chroma` → ChromaDB vector store integration
- `langchain-experimental` → Python REPL tool
- `chromadb` → Vector database for RAG
- `pypdf` → PDF parsing
- `playwright` → Headless browser for web scraping and live search
- `langchainhub` → Pull prompts from LangChain Hub
- `python-dotenv` → Load `.env` variables

> 🔧 **If you want to:** Add a new Python package → add it here and run `pip install -r requirements.txt`.

---

## 📁 `config/` — Global Configuration

### `config/__init__.py`
Package initializer. Makes `config` importable as a Python module. Usually left empty.

---

### `config/config.py`
**Single source of truth for all configuration values.** All other files import constants from here.

Contains:
- `OLLAMA_MODEL` → LLM model name (read from `.env`)
- `OLLAMA_EMBEDDING_MODEL` → Embedding model name (read from `.env`)
- `OLLAMA_FILTER_MODEL` → Filtering model name (read from `.env`)
- `CHROMA_PERSIST_DIR` → Path to the ChromaDB folder (`./database/chroma_db`)
- `CHROMA_COLLECTION_NAME` → ChromaDB collection name (`rag_app`)
- `PDF_SOURCE_DIR` → Folder where PDFs are stored (`./knowledge_base_pdf`)

> 🔧 **If you want to:** Change the DB path, rename the collection, or point to a different PDF folder → **edit this file.**

---

## 📁 `tools/` — Agent Tools & Helper Modules

### `tools/__init__.py`
Package initializer. Makes `tools` importable as a Python module. Usually left empty.

---

### `tools/all_tools.py` ⭐ *(Most important for adding new features)*
**All agent-facing `@tool` functions are defined here.** The LLM picks from these tools based on the user's query.

Current tools:
- `check_html_syntax(query)` → Searches ChromaDB filtered to `html_cheatsheet.pdf` — answers HTML tag/structure questions
- `check_js_logic(query)` → Searches ChromaDB filtered to `javascript_cheatsheet.pdf` — answers JavaScript questions
- `check_sql_security(query)` → Searches ChromaDB filtered to `mysql_cheatsheet.pdf` — answers SQL/database questions

> 🔧 **If you want to:** Add a new tool (e.g., a CSS checker, a Python syntax tool) → **add a new `@tool` function in this file**, then register it in `binding_tools_to_llm.py`.

---

### `tools/binding_tools_to_llm.py` ⭐ *(Register new tools here after defining them)*
**Wires all tools to the LLM.** This is the central assembly point.

What it does:
1. **Imports** all tools from `all_tools.py`, `code_repl.py`, and `web_scraper.py`
2. **Builds `master_tools`** — a flat list of every tool the agent can use
3. **Builds `tool_registry`** — a `dict` (`{tool_name: tool_object}`) for fast O(1) lookup during execution in `main.py`
4. **Initializes the LLM** (`ChatOllama`) using the model from `config.py`
5. **Binds tools to LLM** via `.bind_tools()` → creates `llm_with_tools` that is imported and used in `main.py`

> 🔧 **If you want to:** Add a newly created tool to the agent → import it here and add it to the `master_tools` list.

---

### `tools/rag_retriever.py`
**ChromaDB vector similarity search logic.** Used by the `@tool` functions in `all_tools.py` to search the knowledge base.

Contains:
- `RAGRetriever` class → Connects to ChromaDB, loads the vector store, exposes `similarity_search_with_score()`
- `RAGRetrievalTool` class → A `BaseTool` wrapper around `RAGRetriever` (for LangChain agent compatibility)
- `format_docs()` → Helper to join document page content into a single string
- `filter_relevant_content()` → Uses the filter LLM to strip irrelevant noise from retrieved chunks before returning

> 🔧 **If you want to:** Change how similarity search works, adjust relevance threshold, or tweak result filtering → **edit this file.**

---

### `tools/data_filter.py`
**LLM-powered noise filter for tool results.** After a tool retrieves raw data, this class sends it through an LLM to extract only the relevant parts.

Contains `MistralDataFilter` class with:
- `filter_data(query, context)` → Returns a cleaned, filtered string (blocking call)
- `stream_data(query, context)` → Streams the filtered output token by token (used in `main.py` for real-time printing)

Uses a strict system prompt: *"Extract ONLY the parts directly relevant to the query. Do not add new knowledge."*

> 🔧 **If you want to:** Change the filtering behavior, modify the system prompt, or swap the filter model → **edit this file.**

---

### `tools/pdf_to_embeddings.py`
**One-time ingestion pipeline: PDF → Chunks → Embeddings → ChromaDB.**
Run this script whenever you add new PDFs to `knowledge_base_pdf/`.

Contains `PDFEmbedder` class with:
- `load_and_split_documents()` → Scans `PDF_SOURCE_DIR`, loads each PDF using `PyPDFLoader`, tags each page's `metadata["source"]` with the PDF filename
- `embed_and_store_documents(documents)` → Splits docs into 1000-char chunks (200 overlap) using `RecursiveCharacterTextSplitter`, generates embeddings via Ollama, stores into ChromaDB with a progress bar
- `run_pipeline()` → Calls both methods in sequence

> 🔧 **If you want to:** Add new PDFs to the knowledge base → drop them in `knowledge_base_pdf/` and run `python tools/pdf_to_embeddings.py`.
> **If you want to:** Change chunk size, overlap, or embedding model → **edit this file.**

---

### `tools/code_repl.py`
**Python REPL tool — lets the agent execute Python code at runtime.**

Creates a `python_repl` instance from `PythonREPL` and wraps it as a LangChain `Tool` named `python_repl`.
The agent uses this for math calculations, array manipulations, or any logic that needs actual code execution.

> 🔧 **If you want to:** Change the REPL description or swap it for a safer sandbox → **edit this file.**

---

### `tools/web_scraper.py`
**Playwright-powered headless browser tools for live web scraping and searching.**

- `playwright_web_search(query)` → Uses Playwright to do a headless search on Yahoo and extracts the text snippets from the results.
- `get_web_scraper_tools()` → Starts an async Playwright browser, wraps it in `PlayWrightBrowserToolkit`, and returns only 2 tools (Principle of Least Privilege):
  - `navigate_browser` → Goes to a URL
  - `get_elements` → Extracts elements from the current page

> 🔧 **If you want to:** Add more Playwright tools (e.g., click, fill form) or swap Playwright for another scraper → **edit this file.**

---

## 📁 `database/` — Vector Store (Auto-Generated)

### `database/chroma_db/`
**ChromaDB persistent storage.** Auto-created when you run `pdf_to_embeddings.py`.

Contains binary index files managed by ChromaDB — **do not manually edit these files.**
To reset the knowledge base, delete this folder and re-run the ingestion pipeline.

---

## 📁 `knowledge_base_pdf/` — Source Documents

All PDFs placed here become part of the agent's knowledge base after running the ingestion pipeline.

| File | Topic |
|------|-------|
| `html_cheatsheet.pdf` | HTML tags, semantic elements, DOM structure |
| `javascript_cheatsheet.pdf` | JS syntax, functions, arrays, DOM manipulation |
| `mysql_cheatsheet.pdf` | SQL queries, joins, security best practices |

> 🔧 **If you want to:** Add a new topic (e.g., CSS, Python) → drop the PDF here → run `pdf_to_embeddings.py` → add a new `@tool` in `all_tools.py`.

---

## 🔄 Data Flow Summary

```
User Input (terminal)
        │
        ▼
   main.py  ──────────────────────────────────────────────────────┐
        │                                                          │
        ▼                                                          │
  llm_with_tools.stream()          ← from binding_tools_to_llm.py│
  (LLM decides which tool to call)                                 │
        │                                                          │
        ▼                                                          │
  tool_registry[tool_name].invoke()                               │
  e.g. check_html_syntax()         ← defined in all_tools.py      │
        │                                                          │
        ▼                                                          │
  RAGRetriever (ChromaDB search)   ← from rag_retriever.py        │
  + filter via ChromaDB source metadata                           │
        │                                                          │
        ▼                                                          │
  MistralDataFilter.stream_data()  ← from data_filter.py         │
  (strip noise, keep relevant info)                               │
        │                                                          │
        ▼                                                          ▼
   Final Answer streamed to terminal ◄──────────────────────────────
```

---

## 🚀 Quick Guide: "Where Do I Go To..."

| Task | File to Edit |
|------|-------------|
| Add a new agent tool | `tools/all_tools.py` → then register in `tools/binding_tools_to_llm.py` |
| Add a new PDF to the knowledge base | Drop PDF in `knowledge_base_pdf/` → run `pdf_to_embeddings.py` |
| Change which LLM model is used | `.env` → `OLLAMA_MODEL` |
| Change DB path or collection name | `config/config.py` |
| Modify the main conversation loop | `main.py` |
| Change how results are filtered | `tools/data_filter.py` |
| Change how ChromaDB is queried | `tools/rag_retriever.py` |
| Change chunk size for PDF ingestion | `tools/pdf_to_embeddings.py` |
| Add/remove Playwright browser actions | `tools/web_scraper.py` |
| Enable LangSmith tracing | `.env` → set `LANGCHAIN_TRACING_V2=true` + add `LANGCHAIN_API_KEY` |
