import os
import anyio

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = os.getenv("MCP_HTTP_URL", "http://172.16.0.4:8000/mcp")  # no trailing slash

async def main():
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            result = await session.call_tool("cisco_show_version", {"host": "Cisco-3560-PoE-switch"})
            print(result.structuredContent["result"]["raw"][:200])

if __name__ == "__main__":
    anyio.run(main)
