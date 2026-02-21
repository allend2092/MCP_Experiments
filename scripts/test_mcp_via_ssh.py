import os
import anyio

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

PI_HOST = os.getenv("MCP_PI_SSH", "pi@172.16.0.4")

async def main():
    server = StdioServerParameters(
        command="ssh",
        args=[
            "-T",
            PI_HOST,
            "cd ~/MCP_Server/MCP_Experiments && "
            "source .venv/bin/activate && "
            "source ./.env.local && "
            "python -m mcp_server.server",
        ],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            result = await session.call_tool("cisco_show_version", {"host": "Cisco-3560-PoE-switch"})
            print(result.structuredContent["result"]["raw"][:200])

if __name__ == "__main__":
    anyio.run(main)
