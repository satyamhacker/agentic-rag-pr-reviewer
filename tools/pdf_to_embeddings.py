"""
RAG Retriever Tool
This module implements the retrieval component of the RAG system using ChromaDB.
"""
import os
import sys
from typing import List, Tuple

# Add the parent directory to the path to import core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import BaseTool
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, OLLAMA_EMBEDDING_MODEL, OLLAMA_FILTER_MODEL


class RAGRetriever:
    """
    A retriever class that uses ChromaDB to find relevant documents based on similarity search.
    """
    def __init__(self):
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        
        # Ensure we're using the full path to the database directory
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', CHROMA_PERSIST_DIR))
        
        # Load the persisted vector store
        self.vector_store = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=db_path
        )
    
    def similarity_search_with_score(self, query: str, k: int = 4, min_relevance_score: float = 1.0) -> List[Tuple]:
        """
        Perform similarity search with scores in the vector database.
        
        Args:
            query: The query string to search for
            k: Number of top results to return (default: 4)
            min_relevance_score: Maximum distance score to consider (default: 0.6)
            
        Returns:
            List of tuples containing (Document, score) pairs that meet the relevance threshold
        """
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Filter results based on relevance threshold
        filtered_results = [(doc, score) for doc, score in results if score <= min_relevance_score]
        
        return filtered_results


class RAGRetrievalTool(BaseTool):
    """
    LangChain tool that wraps the RAGRetriever for use in agent workflows.
    """
    name: str = "rag_retriever"
    description: str = "Retrieve relevant documents based on similarity search. Input should be a search query."
    
    def __init__(self):
        super().__init__()
        self.retriever = RAGRetriever()
    
    def _run(self, query: str, min_relevance_score: float = 1.0) -> str:
        """
        Run the RAG retrieval tool.
        
        Args:
            query: The search query string
            min_relevance_score: Maximum distance score to consider (default: 0.6)
            
        Returns:
            Formatted string with the search results
        """
        results = self.retriever.similarity_search_with_score(query, k=4, min_relevance_score=min_relevance_score)
        
        if not results:
            return "No relevant documents found. The query may be unrelated to the knowledge base content."
        
        docs = [doc for doc, score in results]
        return filter_relevant_content(query, docs)
    
    async def _arun(self, query: str):
        """Async version of the tool."""
        raise NotImplementedError("RAGRetriever does not support async")


def format_docs(docs):
    """
    Custom formatter to extract page_content from document chunks
    and join them with double newlines for LLM context clarity.
    
    Args:
        docs: List of Document objects from retriever
        
    Returns:
        str: Formatted string with all chunks joined by \n\n
    """
    return "\n\n".join([doc.page_content for doc in docs])


def filter_relevant_content(query: str, docs: List[Document]) -> str:
    """
    Analyzes the retrieved documents using mistral:7b and filters out irrelevant content.
    Only passes matching content based on the user query.
    
    Args:
        query: The user's search query
        docs: List of Document objects from retriever
        
    Returns:
        str: Filtered content containing only relevant information
    """
    llm = ChatOllama(model=OLLAMA_FILTER_MODEL, temperature=0)
    
    # Format the documents using the existing function
    formatted_context = format_docs(docs)
    
    # Explicitly create a ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict filtering assistant. Analyze the provided context and extract ONLY the parts that are directly relevant to the user's query. Remove any unrelated or unwanted information. If nothing is relevant, return 'No matching content found.' Do not add any new knowledge."),
        ("user", "Query: {query}\n\nContext:\n{context}")
    ])
    
    # Create the pipeline ending with StrOutputParser to get raw string instead of AIMessage
    chain = prompt | llm | StrOutputParser()
    
    filtered_content = chain.invoke({
        "query": query,
        "context": formatted_context
    })
    
    return filtered_content


# Test function to verify the functionality
def test_similarity_search():
    """
    Test function to verify the similarity search functionality works correctly.
    """
    print("🔍 Testing RAG Retriever...")
    
    # Initialize the retriever
    retriever = RAGRetriever()
    
    # Perform a test query
    query = "How text formatting is done?"
    print(f"Query: {query}")
    
    results = retriever.similarity_search_with_score(query, k=4)
    
    if len(results) == 0:
        print("No relevant results found within the specified relevance threshold.")
    else:
        print(f"Number of results: {len(results)}")
        docs = [doc for doc, score in results]
        
        print("\n--- Filtering relevant content with LLM ---")
        filtered_text = filter_relevant_content(query, docs)
        print(filtered_text)
    
    print("\n✅ RAG Retriever test completed.")


if __name__ == "__main__":
    # Run the test to verify functionality
    test_similarity_search()