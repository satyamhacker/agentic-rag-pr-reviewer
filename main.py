import os
import sys

# Ensure core configuration can be accessed
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from langchain import hub
from tools.binding_tools_to_llm import llm_with_tools, tool_registry

def main():
    print("🚀 Initializing Agentic RAG Entry Point...")
    
    # Step 2: Stealing Wisdom (LangChain Hub)
    # Using strict Commit Hash (:50442af1) to prevent Version Mutability risks
    try:
        print("📥 Pulling RAG Prompt from LangChain Hub...")
        prompt = hub.pull("rlm/rag-prompt:50442af1")
        print("✅ Successfully pulled 'rlm/rag-prompt:50442af1'")
    except Exception as e:
        print(f"❌ Failed to pull prompt from LangChain Hub: {str(e)}")
        sys.exit(1)
        
    print(f"✅ Loaded {len(tool_registry)} tools into LLM.")
    for name in tool_registry.keys():
        print(f" - {name}")

    print("\n✅ System is ready. You can now pass input to the agent!")
    
    # Interactive loop to accept prompts from the terminal
    while True:
        try:
            user_input = input("\n🤖 Enter your prompt for the agent (or 'exit' to quit): ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            print(f"⏳ Processing: '{user_input}'...")
            # TODO: Agent execution logic will be plugged in here later
            print("🔜 The compiled agent graph will process this query in upcoming steps!")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
if __name__ == "__main__":
    main()
