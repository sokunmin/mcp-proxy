# Docker Usage Guide

This guide explains how to run mcp-proxy with multiple named MCP servers using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

2. **Access the MCP servers:**
   - The proxy will be available on `http://localhost:8080`
   - Named servers are accessible at:
     - `http://localhost:8080/servers/fetch/sse` (mcp-server-fetch via uvx)
     - `http://localhost:8080/servers/time/sse` (mcp-server-time via uvx)
     - `http://localhost:8080/servers/playwright/sse` (@playwright/mcp via npx)

3. **Health check:**
   - Status endpoint: `http://localhost:8080/status`

## Configuration

The `servers.json` file defines the MCP servers to run:

```json
{
  "mcpServers": {
    "fetch": {
      "disabled": false,
      "timeout": 60,
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "transportType": "stdio"
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Docker Features

- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for monitoring
- **Support for both uvx and npx** package managers
- **Environment variable passing** for package managers

## Customization

To modify the server configuration:

1. Edit `servers.json`
2. Rebuild the container: `docker-compose up --build`

To add new MCP servers, add them to the `mcpServers` object in `servers.json` with either `uvx` (Python packages) or `npx` (Node.js packages) commands.

## Troubleshooting

- **Container fails to start:** Check the logs with `docker-compose logs`
- **Package installation issues:** Ensure the package names are correct and available via uvx/npx
- **Port conflicts:** Change the port mapping in `docker-compose.yml` if 8080 is already in use