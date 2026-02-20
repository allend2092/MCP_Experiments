from __future__ import annotations

import os
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from mcp_server.tools.cisco import cisco_show_version

mcp = FastMCP("mcp-home-network-tools")


@mcp.tool(name="cisco_show_version")
def cisco_show_version_tool(host: str) -> Dict[str, Any]:
    """Run 'show version' on a known Cisco IOS device and return structured output."""
    return cisco_show_version(host)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport in ("http", "streamable-http", "streamable_http"):
        # Bind settings for the Pi
        bind_host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
        bind_port = int(os.getenv("MCP_HTTP_PORT", "8000"))
        path = os.getenv("MCP_HTTP_PATH", "/mcp")

        # Serve as an ASGI app via uvicorn
        # Some MCP SDK versions expose this as `mcp.http_app(path=...)`
        # Others as `mcp.app(path=...)`. We'll try `http_app` first.
        try:
            app = mcp.http_app(path=path)  # preferred
        except AttributeError:
            app = mcp.app(path=path)       # fallback in some versions

        import uvicorn
        uvicorn.run(app, host=bind_host, port=bind_port, log_level="info")
        return

    # local dev / stdio
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

