# Repository Explainer

This document provides a quick map of the project for new contributors.

## What this repo is

`MCP_Experiments` is a prototype **MCP server** project for exposing controlled, read-only home-lab actions (currently Cisco IOS `show version`) to MCP clients such as Open WebUI.

## Main runtime path

1. `mcp_server/server.py` builds a `FastMCP` app and reads transport settings from environment variables.
2. It registers the `cisco_show_version` tool.
3. Tool execution is delegated to `mcp_server/tools/cisco.py`.
4. Cisco tool code opens an interactive SSH session with `pexpect`, logs in, disables paging, runs commands, and returns structured output.

## Important directories

- `mcp_server/`: Server entrypoint and tool implementation.
- `scripts/`: Test clients for HTTP and stdio flows.
- `config/`: SSH config artifacts and examples.
- `docs/`: Architecture and documentation notes.

## Security model in practice

- Host access is allowlisted in `HOSTS` mapping (`mcp_server/tools/cisco.py`).
- Only predefined commands are executed by tool functions.
- SSH behavior is controlled through a dedicated ssh config file path (`MCP_SSH_CONFIG`) and environment-driven secrets.

## How to run quickly

- Start server (HTTP mode): set `MCP_TRANSPORT=streamable-http` and run `python -m mcp_server.server`.
- Validate from desktop client: run `python scripts/test_mcp_streamable_http.py` with `MCP_HTTP_URL` set.
- SSH stdio fallback: run `python scripts/test_mcp_via_ssh.py` with `MCP_PI_SSH` set.
