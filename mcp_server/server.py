from __future__ import annotations

from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_server.tools.cisco import cisco_show_version


server = Server(name="mcp-home-network-tools")


@server.tool(
    name="cisco_show_version",
    description="Run 'show version' on a known Cisco IOS device and return the raw output.",
)
def tool_cisco_show_version(host: str) -> Dict[str, Any]:
    return cisco_show_version(host)


def main() -> None:
    stdio_server(server)


if __name__ == "__main__":
    main()
