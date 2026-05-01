import os
import sys
from langchainhub import Client

client = Client()


# Ensure core configuration can be accessed
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tools.binding_tools_to_llm import llm_with_tools, tool_registry

def main():
    print("🚀 Initializing Agentic RAG Entry Point...")
    
    # Step 2: Stealing Wisdom (LangChain Hub)
    # Using strict Commit Hash (:50442af1) to prevent Version Mutability risks
    try:
        print("📥 Pulling RAG Prompt from LangChain Hub...")
        prompt = client.pull("rlm/rag-prompt:50442af1")
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
            # Invoke LLM with tools
            response = llm_with_tools.invoke(user_input)
            
            if response.tool_calls:
                from tools.data_filter import MistralDataFilter
                data_filter = MistralDataFilter()
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    print(f"🛠️ Agent decided to use tool: {tool_name} with args: {tool_args}")
                    
                    if tool_name in tool_registry:
                        tool = tool_registry[tool_name]
                        # Execute the tool
                        raw_data = tool.invoke(tool_args)
                        print(f"📄 Retrieved raw data from {tool_name}. Size: {len(str(raw_data))} characters.")
                        
                        print("🧹 Filtering relevant data using qwen2.5:7b...")
                        filtered_data = data_filter.filter_data(user_input, str(raw_data))
                        
                        print("\n✨ Final Relevant Data:\n")
                        print(filtered_data)
                        print("\n" + "="*50)
                    else:
                        print(f"❌ Unknown tool requested by agent: {tool_name}")
            else:
                # If no tool was called, print the direct response
                print("\n💬 Agent Response:\n")
                print(response.content)
                print("\n" + "="*50)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
if __name__ == "__main__":
    main()
