import asyncio
from fastmcp import Client
from fastmcp.client.auth import OAuth
import os
from dotenv import load_dotenv

load_dotenv()

mcp_url = os.getenv("MCP_URL")

oauth = OAuth(mcp_url=mcp_url)

async def main():
    async with Client(f"{mcp_url}", auth = oauth) as client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"""Tool: {tool.name} ;;;;;;; tool description: {tool.description}""")
        # print(f"Available tools: {tools}")

        result = await client.call_tool("add", {"a": 5, "b": 7})
        print(f"Result of add: {result.data}")

        search_result = await client.call_tool("search", {"query": "What is FastMCP?"})
        print(f"Search result: {search_result.data}")

if __name__ == "__main__":
    asyncio.run(main())