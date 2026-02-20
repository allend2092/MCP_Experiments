#!/usr/bin/env bash
set -e

source .venv/bin/activate
exec python -m mcp_server.server
