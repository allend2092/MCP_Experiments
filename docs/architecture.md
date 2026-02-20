# Architecture Overview

High-level flow:

LLM (local) → Open WebUI (MCP client)
            → MCP Server (Raspberry Pi)
            → Network Devices / Services

The MCP server acts as a controlled execution boundary that
holds credentials and performs privileged actions on behalf
of the model.
