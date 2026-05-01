from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.config import OLLAMA_FILTER_MODEL

class MistralDataFilter:
    """
    A class to filter raw data retrieved from tools using the qwen2.5:7b model.
    It removes unwanted information and extracts only the relevant parts based on the user's query.
    """
    def __init__(self):
        # Initialize the ChatOllama model for filtering
        self.llm = ChatOllama(model=OLLAMA_FILTER_MODEL, temperature=0)
        
        # Define the strict filtering prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a strict filtering assistant. Analyze the provided context and extract ONLY the parts that are directly relevant to the user's query. Remove any unrelated or unwanted information. If nothing is relevant, return 'No matching content found.' Do not add any new knowledge."),
            ("user", "Query: {query}\n\nContext:\n{context}")
        ])
        
        # Create the pipeline
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def filter_data(self, query: str, context: str) -> str:
        """
        Filters the raw context against the user query.
        
        Args:
            query: The original user search query.
            context: The raw data/text retrieved from tools.
            
        Returns:
            A string containing only the relevant information.
        """
        if not context or context.strip() == "":
            return "No context provided to filter."
            
        filtered_content = self.chain.invoke({
            "query": query,
            "context": context
        })
        
        return filtered_content

    def stream_data(self, query: str, context: str):
        """
        Streams the filtered context against the user query.
        """
        if not context or context.strip() == "":
            yield "No context provided to filter."
            return
            
        for chunk in self.chain.stream({
            "query": query,
            "context": context
        }):
            yield chunk
