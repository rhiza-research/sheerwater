# Sheerwater MCP Server

Deployment and packaging files for the Sheerwater MCP server.

The server code itself lives in the Python package at `sheerwater/mcp/`.

## Building the MCPB bundle

The `.mcpb` file is a ZIP archive that enables one-click installation in Claude Desktop and other MCP clients.

```bash
npx @anthropic-ai/mcpb pack .
```

Run from the repo root. This uses `manifest.json` and `.mcpbignore` (both at the repo root) to package the server.

## Running locally

```bash
uv sync --extra mcp
uv run sheerwater-mcp --help
```

## Docker

```bash
docker build -f mcp/Dockerfile -t sheerwater-mcp .
```
