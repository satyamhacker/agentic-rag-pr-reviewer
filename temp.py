import os

def create_project_structure():
    # Define the structure
    structure = [
        ".env",
        ".gitignore",
        "requirements.txt",
        "knowledge_base/html_cheatsheet.pdf",
        "knowledge_base/mysql_cheatsheet.pdf",
        "knowledge_base/javascript_cheatsheet.pdf",
        "database/chroma_db/.gitkeep",
        "core/__init__.py",
        "core/state.py",
        "core/config.py",
        "tools/__init__.py",
        "tools/web_scraper.py",
        "tools/code_repl.py",
        "tools/rag_retriever.py",
        "agents/__init__.py",
        "agents/supervisor.py",
        "agents/workers.py",
        "ingest.py",
        "main.py"
    ]

    # Content for specific files
    file_contents = {
        ".gitignore": """# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
database/chroma_db/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
""",
        "requirements.txt": """langgraph
langchain
langchain-community
chromadb
playwright
python-dotenv
""",
        "core/__init__.py": "# Core module initialization",
        "tools/__init__.py": "# Tools module initialization",
        "agents/__init__.py": "# Agents module initialization",
        "core/state.py": """from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    # Add other state variables here
""",
        "core/config.py": """from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM or other global configurations here
# Example: api_key = os.getenv("OPENAI_API_KEY")
""",
        "tools/web_scraper.py": """# Placeholder for Playwright async DOM extraction logic
""",
        "tools/code_repl.py": """# Placeholder for PythonREPL sandboxing wrapper
""",
        "tools/rag_retriever.py": """# Placeholder for ChromaDB retrieval logic
""",
        "agents/supervisor.py": """# Placeholder for LangGraph Supervisor (Routing logic)
""",
        "agents/workers.py": """# Placeholder for WebWorker and RagAuditor nodes
""",
        "ingest.py": """# Placeholder for PDF ingestion and embedding script
""",
        "main.py": """# Placeholder for Main Graph compilation and entry point
"""
    }

    # Create directories and files
    for path in structure:
        # Create directory if it doesn't exist
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}/")
        
        # Create file if it doesn't exist (or if it's a directory marker like .gitkeep)
        if not os.path.isdir(path):
            if path not in file_contents:
                # For PDFs or binary files, just create an empty placeholder
                if path.endswith(".pdf"):
                    open(path, 'a').close()
                    print(f"Created placeholder: {path}")
                # For .gitkeep or empty files
                else:
                    with open(path, 'w') as f:
                        pass
                    print(f"Created empty file: {path}")
            else:
                # Write specific content
                with open(path, 'w') as f:
                    f.write(file_contents[path])
                print(f"Created file with content: {path}")

if __name__ == "__main__":
    print("Initializing project structure...")
    create_project_structure()
    print("Project structure created successfully!")
    print("Don't forget to add your PDFs to the 'knowledge_base/' folder.")
