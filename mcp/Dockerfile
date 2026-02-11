FROM python:3.12-slim

# Install git and build tools (git for setuptools-scm, build-essential for C extensions like numcodecs)
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy the repo (including .git for setuptools-scm version detection)
COPY . /app

# Install dependencies with MCP extra
RUN uv sync --frozen --no-dev --extra mcp

# Expose SSE port
EXPOSE 8000

# Run the MCP server in SSE mode
CMD ["uv", "run", "sheerwater-mcp", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
