# MCP Experiments

This repository is a working prototype of a **Model Context Protocol (MCP)** tool server used to expose **read-only home-lab infrastructure tools** to a local LLM workflow.

The current implementation focuses on a Raspberry Pi–hosted MCP server that provides a Cisco IOS tool (`show version`) over SSH, and is consumable from:

- Open WebUI (via MCP Streamable HTTP)
- A desktop Python client (via MCP Streamable HTTP)
- A desktop Python client over SSH stdio (fallback / debugging path)

---

## Current State (Working)

- MCP server running on a Raspberry Pi using `FastMCP`
- Supports two transports:
  - `streamable-http` (for Open WebUI)
  - `stdio` (for SSH-based testing)
- Cisco IOS tool exposed:
  - `cisco_show_version`
- Tool calls successfully execute from Open WebUI and return structured output
- Desktop test harnesses exist for regression testing

---

## Repository Layout

- `mcp_server/server.py`  
  Entry point for the MCP server. Transport is selected via `MCP_TRANSPORT`.

- `mcp_server/tools/cisco.py`  
  Cisco SSH implementation for `show version`.

- `config/`  
  SSH configuration examples (no secrets).

- `scripts/`  
  Desktop-side test harnesses:
  - `test_mcp_streamable_http.py`
  - `test_mcp_via_ssh.py`

---

## Configuration

Create a local environment file on the Raspberry Pi (not committed):

.env.local  
Contains:
- Cisco credentials / SSH configuration used by the tool
- MCP transport selection
- HTTP bind settings

Example variables (documented in `.env.local.example`):
- MCP_TRANSPORT
- MCP_HTTP_HOST
- MCP_HTTP_PORT
- MCP_HTTP_PATH

---

## Running the MCP Server (Streamable HTTP)

On the Raspberry Pi:

export MCP_TRANSPORT=streamable-http  
export MCP_HTTP_HOST=0.0.0.0  
export MCP_HTTP_PORT=8000  
export MCP_HTTP_PATH=/mcp  

python -m mcp_server.server

---

## Validating from the Desktop (Streamable HTTP)

export MCP_HTTP_URL="http://<pi-ip>:8000/mcp"  
python scripts/test_mcp_streamable_http.py

---

## Validating from the Desktop (SSH stdio fallback)

export MCP_PI_SSH="pi@<pi-ip>"  
python scripts/test_mcp_via_ssh.py

---

## Design Notes / Goals

- Read-only tooling by default (no configuration changes to network devices)
- Secrets hygiene:
  - `.env.local` is ignored
  - `.env.local.example` documents required variables safely
- Reproducibility:
  - Test harnesses are kept in `scripts/` to validate functionality after upgrades
    (Open WebUI, MCP version, Python, etc.)

---

## Current Capabilities

- Expose real infrastructure data to a local LLM
- Tool calls routed through Open WebUI
- Structured + raw CLI output available for follow-up reasoning
- Safe, auditable execution path (SSH + allowlisting)

---

## Planned Improvements

- Additional Cisco read-only tools (`show clock`, `show interfaces status`)
- Structured field extraction (IOS version, uptime, serials)
- Host allowlist discovery tool
- Open WebUI configuration walkthrough
