import os
import sys

# Ensure core configuration can be accessed
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from langchain_ollama import ChatOllama
from core.config import OLLAMA_MODEL

# Import all custom tools
from tools.all_tools import check_html_syntax, check_js_logic, check_sql_security
from tools.code_repl import repl_tool
from tools.web_scraper import get_web_scraper_tools

# Extract web tools
web_tools = get_web_scraper_tools()
navigate_tool = next((t for t in web_tools if t.name == "navigate_browser"), None)
get_element_tool = next((t for t in web_tools if t.name == "get_elements"), None)

# Step 1: The Grand Array Assembly
# Array of all available tools
master_tools = [
    check_html_syntax,
    check_js_logic,
    check_sql_security,
    navigate_tool,
    get_element_tool,
    repl_tool,
]

# Step 2: Dictionary Mapping for O(1) Lookup
# Allows fast instant lookup during agent execution
tool_registry = {t.name: t for t in master_tools if t is not None}

# Step 3: Schema Conversion & The Handshake
# Initialize ChatOllama with the model defined in config
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

# Bind all master tools to the LLM to create the tool-calling schema
llm_with_tools = llm.bind_tools([t for t in master_tools if t is not None])

if __name__ == "__main__":
    print(f"✅ Successfully initialized LLM '{OLLAMA_MODEL}' and bound {len(tool_registry)} tools!")
    for name in tool_registry.keys():
        print(f" - {name}")
