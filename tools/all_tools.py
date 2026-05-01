from langchain_core.tools import tool
from tools.rag_retriever import RAGRetriever

def get_vector_store():
    """Helper to initialize and return the Chroma vector store."""
    return RAGRetriever().vector_store

@tool
def check_html_syntax(query: str) -> str:
    """
    Check HTML syntax and structural guidelines.
    Use this tool exclusively when the query is about HTML tags, semantic elements, DOM structure, or HTML attributes.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"source": {"$contains": "html_cheatsheet"}}})
    results = retriever.invoke(query)
    
    if not results:
        return "No HTML syntax information found."
    return "\n\n".join([doc.page_content for doc in results])

@tool
def check_js_logic(query: str) -> str:
    """
    Check JavaScript logic, programming patterns, and syntax.
    Use this tool exclusively when the query is about JavaScript functions, variables, loops, logic, arrays, objects, or DOM manipulation.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"source": {"$contains": "javascript_cheatsheet"}}})
    results = retriever.invoke(query)
    
    if not results:
        return "No JS logic information found."
    return "\n\n".join([doc.page_content for doc in results])

@tool
def check_sql_security(query: str) -> str:
    """
    Check SQL queries for security, best practices, and correct syntax.
    Use this tool exclusively when the query is about SQL databases, SQL injection, queries, joins, or table structures.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"source": {"$contains": "mysql_cheatsheet"}}})
    results = retriever.invoke(query)
    
    if not results:
        return "No SQL security information found."
    return "\n\n".join([doc.page_content for doc in results])
