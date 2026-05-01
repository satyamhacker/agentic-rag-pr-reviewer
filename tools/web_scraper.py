
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

def get_web_scraper_tools():
    """
    Starts an async Playwright browser and returns a list of web scraping tools.
    """
    # Create the async browser instance
    # Note: create_async_playwright_browser is NOT an async function itself, it creates an async-capable browser
    browser = create_async_playwright_browser()
    
    # Bind the browser to the PlayWrightBrowserToolkit
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    
    # Extract the tools (Navigate, Click, Extract Text, etc.)
    all_tools = toolkit.get_tools()
    
    # Principle of Least Privilege: Only provide necessary tools
    # Prevents Tool Bloat and Confused Deputy Attacks
    tools = []
    for tool in all_tools:
        if tool.name in ["navigate_browser", "get_elements"]:
            tools.append(tool)
            
    return tools

# Example usage to test the script directly
def test():
    print("Initializing Playwright browser...")
    tools = get_web_scraper_tools()
    print(f"✅ Loaded {len(tools)} tools from PlayWrightBrowserToolkit!")
    for tool in tools:
        print(f" - {tool.name}")

if __name__ == "__main__":
    test()
