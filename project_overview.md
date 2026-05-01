# 🤖 Agentic RAG PR Reviewer — Complete Project Overview

> A step-by-step guide to everything this project is, what it does, what is already built, and what is planned next.

---

## 📌 Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [How It Works — The Strategy](#3-how-it-works--the-strategy)
4. [Tech Stack](#4-tech-stack)
5. [Architecture Overview](#5-architecture-overview)
6. [Features Implemented (Current State)](#6-features-implemented-current-state)
7. [Features In Progress / Planned](#7-features-in-progress--planned)
8. [The Learning Roadmap (Modules)](#8-the-learning-roadmap-modules)
9. [Business Value](#9-business-value)

---

## 1. What Is This Project?

**Agentic RAG PR Reviewer** is an **Autonomous Multi-Agent AI System** that:

- Takes any live Pull Request (PR) URL or code question as input.
- Uses a **headless browser (Playwright)** to extract live code from the page.
- Cross-checks it against the company's **private internal rulebooks** (HTML, JavaScript, MySQL cheatsheets stored as PDFs).
- Generates a **compliance audit report** answering whether the code follows internal guidelines.

The end goal is a fully autonomous **"Stack-Master Code Auditor"** — a multi-agent factory where a **Supervisor Agent** routes tasks to specialized **Worker Agents** (Web Scraper Worker and RAG Auditor Worker), coordinated by **LangGraph**, and monitored in real-time by **LangSmith**.

---

## 2. The Problem It Solves

### Problem 1: Code Review Fatigue
Senior engineers waste 30–40% of their time manually checking syntax, typos, and company guideline compliance during code reviews. This is slow, boring, and prone to human error.

### Problem 2: The LLM Knowledge Gap
Generic LLMs (ChatGPT, Copilot) have general internet knowledge but are completely blind to **private internal rules** stored in company PDF documents. They will pass code on external standards but miss internal compliance requirements.

### Problem 3: Dynamic Content Blocking
Modern web apps are Single Page Applications (SPAs) that render content via JavaScript. Normal web scrapers (`requests`, `BeautifulSoup`) get a blank page. A headless browser is required to actually see the code.

---

## 3. How It Works — The Strategy

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                   THE MACHINE                           │
                    │                                                         │
  User Input ──────►  Supervisor Agent (LangGraph)                           │
  (PR URL or        │      │                                                  │
   question)        │      ├──► Web Worker (Playwright)                       │
                    │      │       └── Scrapes live PR page / web search      │
                    │      │                                                  │
                    │      └──► RAG Auditor Worker (ChromaDB)                 │
                    │              └── Retrieves rules from PDF cheatsheets   │
                    │                                                         │
                    │  Data Filter (qwen2.5:7b LLM)                          │
                    │      └── Strips noise, extracts relevant answer         │
                    │                                                         │
                    │  Final Answer ──────────────────────────────────────── ► Terminal
                    └─────────────────────────────────────────────────────────┘
```

**Four pillars:**
1. **The Brain** (LangGraph) — Supervisor routes the right task to the right worker.
2. **The Eyes** (Playwright) — Headless browser fetches live JavaScript-rendered pages.
3. **The Memory** (RAG Pipeline + ChromaDB) — PDFs are embedded and stored as a searchable vector database.
4. **The Filter** (Data Filter LLM) — Cleans raw retrieved data down to just the relevant answer.

---

## 4. Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| **LLM** | Ollama (`qwen2.5:7b`) | Local LLM for agent reasoning and filtering |
| **Embeddings** | Ollama (`nomic-embed-text`) | Converts text chunks to vectors |
| **Vector DB** | ChromaDB | Persistent storage of PDF embeddings |
| **Agent Framework** | LangChain + LangGraph | Tool binding, agent orchestration |
| **Web Scraping** | Playwright (sync + async) | Headless browser for live web search and DOM extraction |
| **PDF Parsing** | PyPDF | Loads PDF pages as documents |
| **Code Execution** | PythonREPL (langchain-experimental) | Lets the agent run Python code at runtime |
| **Prompt Hub** | LangChain Hub | Pulls versioned expert prompts |
| **Observability** | LangSmith | Traces every agent step, token usage, and latency |
| **Config** | python-dotenv | Loads environment variables from `.env` |

---

## 5. Architecture Overview

### Current File Structure

```
agentic-rag-pr-reviewer/
│
├── main.py                    ← Entry point — interactive agent loop
├── .env                       ← Secret keys + model config
├── requirements.txt           ← All Python dependencies
│
├── config/
│   ├── __init__.py
│   └── config.py              ← Single source of truth for all constants
│
├── tools/
│   ├── __init__.py
│   ├── all_tools.py           ← @tool functions (HTML, JS, SQL RAG tools)
│   ├── binding_tools_to_llm.py← Assembles all tools + binds to LLM
│   ├── rag_retriever.py       ← ChromaDB vector search logic
│   ├── data_filter.py         ← LLM noise filter for raw tool results
│   ├── pdf_to_embeddings.py   ← PDF ingestion pipeline (run once)
│   ├── code_repl.py           ← Python REPL tool
│   └── web_scraper.py         ← Playwright browser + web search tool
│
├── database/
│   └── chroma_db/             ← Auto-generated ChromaDB SQLite files
│
└── knowledge_base_pdf/
    ├── html_cheatsheet.pdf
    ├── javascript_cheatsheet.pdf
    └── mysql_cheatsheet.pdf
```

### Target / Final Architecture (Planned — Module 3)

```
agentic-rag-pr-reviewer/
│
├── core/
│   ├── config.py              ← LLM init + constants
│   └── state.py               ← AgentState TypedDict (LangGraph shared memory)
│
├── agents/
│   ├── supervisor.py          ← Supervisor routing logic
│   └── workers.py             ← WebScraper + RAGAuditor worker nodes
│
├── tools/                     ← (Same as current)
├── database/                  ← (Same as current)
├── knowledge_base_pdf/        ← (Same as current)
├── ingest.py                  ← Standalone PDF embedding pipeline
└── main.py                    ← StateGraph compile + invoke
```

---

## 6. Features Implemented (Current State)

### ✅ Feature 1: PDF Knowledge Base Ingestion (Module 1 — Complete)

**File:** `tools/pdf_to_embeddings.py`

The `PDFEmbedder` class implements a complete one-time ingestion pipeline:
- Scans `knowledge_base_pdf/` and loads all `.pdf` files using `PyPDFLoader`
- Tags each page's metadata with `source = pdf_filename` (used later for domain filtering)
- Splits all pages into overlapping chunks using `RecursiveCharacterTextSplitter`:
  - `chunk_size = 1000` characters
  - `chunk_overlap = 200` characters (prevents context loss at chunk boundaries)
- Generates vector embeddings using `OllamaEmbeddings (nomic-embed-text)`
- Stores embeddings persistently in **ChromaDB** at `./database/chroma_db`

> Currently 3 PDFs ingested: HTML, JavaScript, and MySQL cheatsheets.

---

### ✅ Feature 2: RAG Vector Retriever (Module 1 — Complete)

**File:** `tools/rag_retriever.py`

The `RAGRetriever` class:
- Loads the persisted ChromaDB vector store from disk (no re-embedding needed)
- Exposes `similarity_search_with_score()` — performs cosine/L2 distance search
- Filters results by relevance threshold (`min_relevance_score`)
- Includes `filter_relevant_content()` — sends retrieved chunks to the filter LLM to strip irrelevant noise before returning

The `RAGRetrievalTool` class wraps the retriever as a LangChain `BaseTool` for agent compatibility.

---

### ✅ Feature 3: Domain-Filtered RAG Tools (Module 2 — Complete)

**File:** `tools/all_tools.py`

Three specialized `@tool` functions that search ChromaDB but **filter by source PDF** using metadata:

| Tool | Filters to | Answers questions about |
|---|---|---|
| `check_html_syntax(query)` | `html_cheatsheet.pdf` | HTML tags, semantic elements, DOM structure, attributes |
| `check_js_logic(query)` | `javascript_cheatsheet.pdf` | JS functions, loops, arrays, objects, DOM manipulation |
| `check_sql_security(query)` | `mysql_cheatsheet.pdf` | SQL queries, joins, injection prevention, best practices |

Each tool retrieves `k=4` most similar chunks filtered by source, then returns the raw page content. The key design principle: **one tool per knowledge domain** — preventing the LLM from suffering "Decision Paralysis" when picking the right rulebook.

---

### ✅ Feature 4: Python REPL Code Executor (Module 2 — Complete)

**File:** `tools/code_repl.py`

Wraps LangChain's `PythonREPL` as a tool named `python_repl`.

The agent uses this for:
- Math calculations (e.g., calculating bundle sizes, percentages)
- Array and string logic that needs deterministic computation
- Any task where LLM would hallucinate a number

> ⚠️ Security Note: This is `langchain_experimental` — never expose it without Docker sandboxing in production.

---

### ✅ Feature 5: Playwright Web Scraper + Browser Tools (Module 2 — Complete)

**File:** `tools/web_scraper.py`

Two capabilities in one file:

**A. `playwright_web_search(query)` — Live Web Search Tool**
- Launches a headless Chromium browser using Playwright sync API
- Adds a realistic User-Agent to bypass basic bot protection
- Navigates to Yahoo Search for the given query
- Extracts top 5 result snippets (`.algo` CSS selector)
- Returns them as a formatted string for the LLM to reason over
- Used when the agent needs up-to-date, real-world information not in the local database

**B. `get_web_scraper_tools()` — Async Playwright Browser Tools**
- Creates an async Playwright browser instance
- Wraps it in `PlayWrightBrowserToolkit`
- Returns only 2 tools (Principle of Least Privilege):
  - `navigate_browser` → Navigate to a URL
  - `get_elements` → Extract DOM elements from the current page
- Intentionally excludes dangerous tools like `click_element` and `fill_element` to prevent Confused Deputy Attacks

---

### ✅ Feature 6: LLM Data Filter (Module 2 — Complete)

**File:** `tools/data_filter.py`

The `MistralDataFilter` class takes raw, noisy data from any tool and strips it down to only the parts relevant to the user's question.

- Uses `qwen2.5:7b` as the filter model (configured via `.env`)
- Strict system prompt: *"Extract ONLY the parts directly relevant to the user's query. Do not add any new knowledge."*
- `filter_data(query, context)` — blocking call, returns filtered string
- `stream_data(query, context)` — streaming call, yields tokens one by one (used in `main.py` for real-time printing)

This prevents LLM hallucination from large, noisy retrieved contexts.

---

### ✅ Feature 7: Tool Registry + LLM Binding (Module 2 — Complete)

**File:** `tools/binding_tools_to_llm.py`

The central assembly point for the agent:

1. Imports all tools from `all_tools.py`, `code_repl.py`, `web_scraper.py`
2. Builds `master_tools` — a flat list of all 7 tools the agent can call:
   - `check_html_syntax`
   - `check_js_logic`
   - `check_sql_security`
   - `playwright_web_search`
   - `navigate_browser`
   - `get_elements`
   - `python_repl`
3. Builds `tool_registry` — a `{tool_name: tool_object}` dictionary for O(1) lookup
4. Initializes `ChatOllama` with `qwen2.5:7b`
5. Binds all tools to the LLM via `.bind_tools()` → creates `llm_with_tools`

`llm_with_tools` is what gets imported into `main.py` — it's the LLM that now "knows" what tools exist and can generate `tool_calls` JSON.

---

### ✅ Feature 8: Interactive Agent Loop with Streaming (Module 2.5 — Complete)

**File:** `main.py`

The entry point runs a terminal-based interactive agent loop:

1. **Pulls RAG Prompt** from LangChain Hub (`rlm/rag-prompt:50442af1` — pinned to exact commit hash to prevent version drift)
2. **Interactive Loop**: Accepts user input from the terminal
3. **Streams LLM response** in real-time, token by token
4. **Detects tool calls** in the LLM response (`response.tool_calls`)
5. **Executes the tool** using `tool_registry[tool_name].invoke(tool_args)`
6. **Filters the raw result** through `MistralDataFilter.stream_data()`
7. **Streams the final clean answer** to the terminal

This implements the **Execution Gap Bridge** — the LLM generates a JSON "ticket" describing which tool to use, and `main.py` actually executes it and feeds the result back.

---

### ✅ Feature 9: Global Configuration System (Complete)

**File:** `config/config.py`

Single source of truth — all other files import from here:

| Constant | Default Value | Purpose |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5:7b` | Main reasoning LLM |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | PDF embedding model |
| `OLLAMA_FILTER_MODEL` | `qwen2.5:7b` | Data filtering LLM |
| `CHROMA_PERSIST_DIR` | `./database/chroma_db` | Where ChromaDB saves files |
| `CHROMA_COLLECTION_NAME` | `rag_app` | ChromaDB collection name |
| `PDF_SOURCE_DIR` | `./knowledge_base_pdf` | Where PDF files live |

---

## 7. Features In Progress / Planned

These are the features documented in `work_to_do.md` that are **not yet implemented** in the actual codebase:

### 🔲 Module 3, Level 3.1 — Execution Gap & ReAct Message State

Formalizing the tool execution loop using proper LangChain message objects:
- Wrap user query in `HumanMessage`
- Append the full `ai_message` object (preserves `tool_calls` metadata)
- Execute each tool call in a loop
- Wrap results in `ToolMessage` with matching `tool_call_id` (prevents `400 Bad Request` "Orphaned Tool Message" errors)
- Feed entire message history back to the LLM for final synthesis

**Files to create:** `test_execution_gap.py`, updates to `main.py`

---

### 🔲 Module 3, Level 3.2 — LangGraph Multi-Agent Supervisor + LangSmith Telemetry

The **final capstone feature** — the full multi-agent factory:

**`core/state.py`:**
- `AgentState` TypedDict with `messages: Annotated[Sequence[BaseMessage], operator.add]`
- The `operator.add` reducer ensures state is appended, never overwritten across agent hops

**`agents/supervisor.py`:**
- `supervisor_node(state)` — reads messages, decides routing
- Outputs one of: `"web_scraper"`, `"rag_auditor"`, or `"FINISH"`

**`agents/workers.py`:**
- `web_scraper_node(state)` — runs Playwright navigate + extract
- `rag_auditor_node(state)` — runs RAG tool calls for HTML/JS/SQL

**`main.py` (updated):**
- `StateGraph(AgentState)` initialization
- Add all three nodes
- `add_conditional_edges` from Supervisor based on `state["next_agent"]`
- `add_edge(START, "supervisor")` as the graph entry point
- `.compile()` and `.invoke()`

**LangSmith Observability:**
- Enable via `.env`: `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY`
- Every agent step, token count, and latency visible as a DAG trace in the LangSmith web UI

---

### 🔲 Module 1.5 — Retrieval Optimization (Optional Enhancement)

Advanced RAG techniques explored in the learning material but not implemented in code:

- **HyDE (Hypothetical Document Embeddings)** — Generate a fake "ideal answer" first, then search DB for similar content (Answer-to-Answer matching vs Question-to-Answer)
- **Contextual Compression** (`ContextualCompressionRetriever`) — Filter retrieved chunks by relevance score before feeding to LLM, using `EmbeddingsFilter` with `similarity_threshold=0.76`
- **StrOutputParser Integration** — Explicit LCEL pipeline (`prompt | llm | StrOutputParser()`) to always return clean strings, never raw `AIMessage` objects

---

### 🔲 Module 2.5 — smolagents CodeAgent (Optional Enhancement)

Explored in learning material — a separate agent type from HuggingFace's `smolagents` library:
- `CodeAgent` that generates and executes Python code on the fly, rather than calling pre-defined tools
- Read-Only Agency principle — only safe tools provided (no write/email/DB access)
- Useful for dynamic tasks like "read this CSV and plot a chart"

---

## 8. The Learning Roadmap (Modules)

This project was built as a step-by-step learning journey across 3 modules:

```
Module 1: The Foundation (RAG Core)
  ├── Level 1.1 ✅ — PDF loading, RecursiveCharacterTextSplitter, metadata tagging
  ├── Level 1.2 ✅ — ChromaDB HNSW indexing, disk persistence, similarity search
  └── Level 1.5 🔲 — HyDE, Contextual Compression Reranking, LCEL Output Parsing

Module 2: The Arsenal (Agentic Tooling)
  ├── Level 2.1 ✅ — Async Playwright headless browser DOM extraction
  ├── Level 2.2 ✅ — PythonREPL sandboxing + Domain-filtered RAG tools
  ├── Level 2.3 ✅ — Tool binding to LLM, semantic routing, O(1) tool registry
  └── Level 2.5 🔲 — smolagents CodeAgent, Search API fallback routing, LangChain Hub

Module 3: The Megazord Factory (LangGraph Orchestration)
  ├── Level 3.1 🔲 — Execution Gap bridge, ReAct message state, ToolMessage ID matching
  └── Level 3.2 🔲 — Multi-Agent Supervisor routing, LangGraph StateGraph, LangSmith telemetry
```

**Legend:** ✅ = Implemented in codebase | 🔲 = Planned / Not yet implemented

---

## 9. Business Value

| Metric | Before This Tool | After This Tool |
|---|---|---|
| Code review time | 30–40% of senior engineer's day | Automated in seconds |
| Internal compliance | Manual, error-prone checklist | 100% automated against PDF rulebook |
| Dynamic page scraping | Fails on JS-rendered SPAs | Full JavaScript rendering via Playwright |
| LLM knowledge | General internet only | Private internal documentation via RAG |
| Observability | Black box | Full DAG trace per query in LangSmith |
| Estimated time reduction | — | **~80% reduction in code review time** |

---

## 10. How To Run The Project

### Step 1: Setup
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
playwright install            # Install browser binaries
```

### Step 2: Configure
Edit `.env` and fill in:
```
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_FILTER_MODEL=qwen2.5:7b
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=<your_key_if_tracing>
```

### Step 3: Start Ollama
```bash
ollama serve           # In a separate terminal, keep it running
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### Step 4: Ingest PDFs (Run Once)
```bash
python tools/pdf_to_embeddings.py
```
This creates the ChromaDB vector store from your 3 PDF cheatsheets.

### Step 5: Run the Agent
```bash
python main.py
```

Then type questions like:
- `"What is the correct way to use a SQL JOIN?"` → triggers `check_sql_security`
- `"What is the semantic tag for navigation in HTML?"` → triggers `check_html_syntax`
- `"What is the weather in Mumbai today?"` → triggers `playwright_web_search`
- `"Calculate 500 * 48"` → triggers `python_repl`

---

## 11. Config & Database Directories Explained

### `config/config.py`
**Single source of truth for all configuration values.** All other files import constants from here — never hardcode values directly in tool or agent files.

| Constant | Value | Used In |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5:7b` (from `.env`) | `binding_tools_to_llm.py`, `data_filter.py` |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` (from `.env`) | `pdf_to_embeddings.py`, `rag_retriever.py` |
| `OLLAMA_FILTER_MODEL` | `qwen2.5:7b` (from `.env`) | `data_filter.py`, `rag_retriever.py` |
| `CHROMA_PERSIST_DIR` | `./database/chroma_db` | `pdf_to_embeddings.py`, `rag_retriever.py` |
| `CHROMA_COLLECTION_NAME` | `rag_app` | `pdf_to_embeddings.py`, `rag_retriever.py` |
| `PDF_SOURCE_DIR` | `./knowledge_base_pdf` | `pdf_to_embeddings.py` |

> 🔧 **If you want to:** Change the LLM model, DB path, or collection name → **edit `config/config.py`** (the change will automatically apply everywhere).

### `config/__init__.py`
Empty package initializer. Makes `config/` importable as a Python module. Do not put logic here.

---

### `database/chroma_db/`
**Auto-generated ChromaDB persistent storage.** Created the first time you run `python tools/pdf_to_embeddings.py`.

- Contains SQLite + binary HNSW index files managed internally by ChromaDB.
- **Do NOT manually edit or delete individual files inside this folder.**
- **To fully reset** the knowledge base: delete this entire folder, then re-run `pdf_to_embeddings.py`.
- This folder is listed in `.gitignore` — never commit it to Git (it's heavy and machine-specific).

---

## 12. Quick Guide — "Where Do I Go To..."

| Task | File(s) to Edit |
|---|---|
| **Add a new agent tool** (e.g., CSS checker) | Create `@tool` in `tools/all_tools.py` → register in `tools/binding_tools_to_llm.py` |
| **Add a new PDF to the knowledge base** | Drop PDF in `knowledge_base_pdf/` → run `python tools/pdf_to_embeddings.py` |
| **Change which LLM model is used** | `.env` → `OLLAMA_MODEL` |
| **Change the embedding model** | `.env` → `OLLAMA_EMBEDDING_MODEL` |
| **Change the ChromaDB path or collection name** | `config/config.py` |
| **Modify the main conversation loop** | `main.py` |
| **Change how raw tool results are filtered** | `tools/data_filter.py` (edit the system prompt or swap model) |
| **Change how ChromaDB is queried / relevance threshold** | `tools/rag_retriever.py` |
| **Change chunk size or overlap for PDF ingestion** | `tools/pdf_to_embeddings.py` |
| **Add/remove Playwright browser actions** | `tools/web_scraper.py` |
| **Change the live web search engine** | `tools/web_scraper.py` → `playwright_web_search()` function |
| **Enable LangSmith tracing** | `.env` → `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY=<key>` |
| **Add a new LangGraph worker agent** | Create node in `agents/workers.py` → wire in `main.py` StateGraph |
| **Change Supervisor routing logic** | `agents/supervisor.py` (planned — not yet created) |
