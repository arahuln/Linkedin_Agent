# from fastmcp import FastMCP
from fastmcp.server.server import FastMCP
# from langchain_community.tools import DuckDuckGoSearchResults
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv

load_dotenv()
# from ddgs import DDGS

search_tool = TavilySearch(
    tavly_api_key = os.getenv("TAVILY_API_KEY"),
    search_depth="basic",
    topic="general",
    max_results=1,
)

# search_tool = DuckDuckGoSearchResults()
# search_tool = search_tool

mcp = FastMCP("Demo")

@mcp.tool
def add(a:int, b:int) -> int:
    """ Adds two numbers """
    return a+b

@mcp.tool
def search(query: str) -> str:
    """ Searches about the query and provides the answer """
    result = search_tool.invoke(input = query)
    answer = result['results'][0]['content']
    return answer

if __name__ == "__main__":
    mcp.run()
    