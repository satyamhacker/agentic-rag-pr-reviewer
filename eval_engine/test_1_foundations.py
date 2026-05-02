"""
(Module 1) Probabilistic testing, Perplexity, LLM-as-a-judge
"""
import os
import sys

# Ensure we can import from eval_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval_engine.eval_config import local_llm, eval_tracer
from langchain_core.runnables import RunnableConfig

if __name__ == "__main__":
    print("Testing local_llm invocation with LangSmith tracer...")
    
    # 🔍 SIRF YE CALL LANGSMITH MEIN JAYEGI
    response = local_llm.invoke(
        "What is the semantic HTML tag for navigation?",
        config=RunnableConfig(callbacks=[eval_tracer])
    )

    print("✅ LLM Response:", response.content)
