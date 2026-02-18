# Sheerwater MCP Server

Deployment and packaging files for the Sheerwater MCP server.

The server code itself lives in the Python package at `sheerwater/mcp/`.

## Building the MCPB bundle

The `.mcpb` file is a ZIP archive that enables one-click installation in Claude Desktop and other MCP clients.

```bash
npx @anthropic-ai/mcpb pack .
```

Run from the repo root. This uses `manifest.json` and `.mcpbignore` (both at the repo root) to package the server.

## Installation

Core library only:

```bash
uv sync
```

With MCP server dependencies (fastmcp, anthropic):

```bash
uv sync --extra mcp
```

With dev tools (pytest, ruff, jupyter, etc.):

```bash
uv sync --group dev
```

Everything:

```bash
uv sync --extra mcp --group dev
```

## Running locally

```bash
uv run sheerwater-mcp --help
```

## Docker

```bash
docker build -f mcp/Dockerfile -t sheerwater-mcp .
```
