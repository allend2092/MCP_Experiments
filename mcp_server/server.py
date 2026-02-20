from __future__ import annotations

import os
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from mcp_server.tools.cisco import cisco_show_version

mcp = FastMCP("mcp-home-network-tools")


@mcp.tool()
def cisco_show_version_tool(host: str) -> Dict[str, Any]:
    """Run 'show version' on a known Cisco IOS device and return structured output."""
    return cisco_show_version(host)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport in ("http", "streamable-http", "streamable_http"):
        # Bind settings for the Pi
        host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_HTTP_PORT", "8000"))
        path = os.getenv("MCP_HTTP_PATH", "/mcp")

        # FastMCP exposes the server over Streamable HTTP (default path is /mcp).
        mcp.run(transport="streamable-http", host=host, port=port, path=path)
    else:
        # local dev / inspector style
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
