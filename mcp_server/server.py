from __future__ import annotations

import os
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from mcp_server.tools.cisco import cisco_show_version as _cisco_show_version


def create_mcp() -> FastMCP:
    """Create FastMCP with explicit env-driven network settings."""
    return FastMCP(
        "mcp-home-network-tools",
        host=os.getenv("MCP_HTTP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_HTTP_PORT", "8000")),
        streamable_http_path=os.getenv("MCP_HTTP_PATH", "/mcp"),
    )


mcp = create_mcp()


@mcp.tool(name="cisco_show_version")
def cisco_show_version(host: str) -> Dict[str, Any]:
    """Run 'show version' on a known Cisco IOS device and return structured output."""
    return _cisco_show_version(host)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport in ("http", "streamable-http", "streamable_http"):
        mcp.run(transport="streamable-http")
        return

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
