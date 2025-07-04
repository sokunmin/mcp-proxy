# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP proxy server that exposes multiple MCP (Model Context Protocol) servers over various transport protocols. It's designed for production deployment using Docker containers.

## Core Architecture

- **mcp_proxy.py**: Main FastMCP proxy application that loads server configurations and handles transport protocols
- **servers.json**: Configuration file defining which MCP servers to proxy (context7, fetch, time)
- **entrypoint.sh**: Docker entrypoint script that configures transport and networking based on environment variables
- **Dockerfile**: Production-ready Alpine Linux container with Python 3.12 and Node.js for mixed server support

## Key Commands

### Docker Development
```bash
# Build and run with Docker Compose (recommended)
docker-compose up --build

# Build container manually
docker build -t mcp-proxy .

# Run with specific transport
TRANSPORT=http PORT=8001 docker-compose up

# View logs
docker-compose logs -f
```

### Direct Python Execution
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run with different transports
python mcp_proxy.py sse --host 0.0.0.0 --port 8000
python mcp_proxy.py http --host 0.0.0.0 --port 8001
python mcp_proxy.py stdio
```

## Configuration

### Environment Variables
- `TRANSPORT`: Protocol type (sse, http, stdio) - defaults to sse
- `HOST`: Bind address - defaults to 0.0.0.0
- `PORT`: Service port - defaults to 8000 for sse, 8001 for http
- `TZ`: Timezone - defaults to Etc/UTC

### MCP Server Configuration
Edit `servers.json` to add/modify MCP servers:
- **context7**: Node.js server via npx (document search)
- **fetch**: Python server via uvx (web content fetching)  
- **time**: Python server via uvx (time operations)

## Transport Protocols

The proxy supports three transport modes:
- **stdio**: Standard input/output for direct process communication
- **sse**: Server-Sent Events for web-based streaming
- **http**: Streamable HTTP for traditional web requests

## Dependencies

- **FastMCP 2.9.0+**: Core MCP proxy framework
- **Node.js/npm**: Required for npx-based MCP servers
- **Python 3.12**: Runtime environment
- **uv**: Package management (containerized environment)

## Container Architecture

Uses `ghcr.io/astral-sh/uv:python3.12-alpine` base image with:
- Pre-installed uv for fast Python package management
- Node.js/npm for mixed server ecosystem support
- Non-root execution for security
- Multi-transport port exposure (8000, 8001)