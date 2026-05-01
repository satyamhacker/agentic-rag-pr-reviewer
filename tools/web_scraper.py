
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

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

@tool
def playwright_web_search(query: str) -> str:
    """
    Search the web for current events or real-time information using a headless browser.
    Use this tool when you need up-to-date knowledge that is not in the local database.
    """
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            
            # Add a realistic User-Agent to bypass basic bot protection
            page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Navigate to Yahoo Search
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            page.goto(f"https://search.yahoo.com/search?p={encoded_query}")
            
            # Extract the text snippets from the search results
            snippets = page.locator(".algo").all_inner_texts()
            
            browser.close()
            
            if not snippets:
                return "No search results found."
                
            # Return top 5 results as a formatted string
            return "\n\n".join(snippets[:5])
    except Exception as e:
        print(f"⚠️ Playwright search failed: {str(e)}")
        return f"Search failed due to an error: {str(e)}"

# Example usage to test the script directly
def test():
    print("Initializing Playwright browser...")
    tools = get_web_scraper_tools()
    print(f"✅ Loaded {len(tools)} tools from PlayWrightBrowserToolkit!")
    for tool in tools:
        print(f" - {tool.name}")

if __name__ == "__main__":
    test()
