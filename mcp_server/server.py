from __future__ import annotations

import os
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from mcp_server.tools.cisco import cisco_show_version as _cisco_show_version


def _build_mcp() -> FastMCP:
    """
    Build FastMCP with env-driven HTTP settings at construction time.
    This is important for mcp==1.26.x streamable-http behavior.
    """
    host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_HTTP_PORT", "8000"))
    path = os.getenv("MCP_HTTP_PATH", "/mcp")

    return FastMCP(
        "mcp-home-network-tools",
        host=host,
        port=port,
        streamable_http_path=path,
    )


mcp = _build_mcp()


@mcp.tool(name="cisco_show_version")
def cisco_show_version(host: str) -> Dict[str, Any]:
    """Run 'show version' on a known Cisco IOS device and return structured output."""
    return _cisco_show_version(host)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport in ("http", "streamable-http", "streamable_http"):
        # For mcp==1.26.x this correctly initializes StreamableHTTP lifecycle.
        mcp.run(transport="streamable-http")
        return

    # local dev / stdio
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

