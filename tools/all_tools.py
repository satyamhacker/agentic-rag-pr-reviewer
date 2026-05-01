from langchain_core.tools import tool
from tools.rag_retriever import RAGRetriever
# Step 1: The Brittle Scraper Shield
from langchain_community.tools import DuckDuckGoSearchRun


def get_vector_store():
    """Helper to initialize and return the Chroma vector store."""
    return RAGRetriever().vector_store

@tool
def check_html_syntax(query: str) -> str:
    """
    Search the database for HTML syntax and structural guidelines.
    Pass the user's natural language question as the query.
    Use this tool exclusively when the query is about HTML tags, semantic elements, DOM structure, or HTML attributes.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"source": "html_cheatsheet.pdf"}})
    results = retriever.invoke(query)
    
    if not results:
        return "No HTML syntax information found."
    return "\n\n".join([doc.page_content for doc in results])

@tool
def check_js_logic(query: str) -> str:
    """
    Search the database for JavaScript logic, programming patterns, and syntax.
    Pass the user's natural language question as the query.
    Use this tool exclusively when the query is about JavaScript functions, variables, loops, logic, arrays, objects, or DOM manipulation.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"source": "javascript_cheatsheet.pdf"}})
    results = retriever.invoke(query)
    
    if not results:
        return "No JS logic information found."
    return "\n\n".join([doc.page_content for doc in results])

@tool
def check_sql_security(query: str) -> str:
    """
    Search the database for SQL queries, security, best practices, and syntax.
    Pass the user's natural language question as the query, NOT an actual SQL statement.
    Use this tool exclusively when the query is about SQL databases, SQL injection, queries, joins, or table structures.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"source": "mysql_cheatsheet.pdf"}})
    results = retriever.invoke(query)
    
    if not results:
        return "No SQL security information found."
    return "\n\n".join([doc.page_content for doc in results])


@tool
def safe_duckduckgo_search(query: str) -> str:
    """
    Search the web for current events or real-time information using DuckDuckGo.
    Use this tool when you need up-to-date knowledge that is not in the local database.
    """
    try:
        ddg = DuckDuckGoSearchRun()
        return ddg.invoke(query)
    except Exception as e:
        print(f"⚠️ [Graceful Degradation] DuckDuckGo Search failed: {str(e)}")
        # Manual print message / trigger backup API fallback concept
        return "Search failed due to rate limits or network issues. Triggering backup protocol or please search manually."
