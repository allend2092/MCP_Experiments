import os
import anyio

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


async def main() -> None:
    server = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server.server"],
        env=os.environ.copy(),  # <-- IMPORTANT: pass env explicitly
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:")
            for t in tools.tools:
                print(f"- {t.name}")

            tool_names = {t.name for t in tools.tools}
            if "cisco_show_version" in tool_names:
                tool_name = "cisco_show_version"
            elif "cisco_show_version_tool" in tool_names:
                tool_name = "cisco_show_version_tool"
            else:
                raise RuntimeError(f"Expected tool not found. Available: {sorted(tool_names)}")

            result = await session.call_tool(
                tool_name,
                {"host": "Cisco-3560-PoE-switch"},
            )

            print("\nRESULT:")
            #print(result.model_dump_json(indent=2))
            if result.isError:
                # Errors often come back as text; show them
                print("ERROR:")
                if result.content:
                    print(result.content[0].text)
                else:
                    print(result.model_dump_json(indent=2))
                return

            # Success: prefer structuredContent
            if result.structuredContent is not None and "result" in result.structuredContent:
                data = result.structuredContent["result"]
                print("STRUCTURED RESULT KEYS:", list(data.keys()))
                print("\nRAW (first 200 chars):")
                print(data["raw"][:200])
            else:
                # Fallback if a tool ever returns unstructured content
                print("NO structuredContent; fallback to text:")
                print(result.content[0].text if result.content else "<no content>")


if __name__ == "__main__":
    anyio.run(main)
