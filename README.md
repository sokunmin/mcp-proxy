# FastMCP Proxy Server

This project provides a simple and flexible proxy server built with **FastMCP**. It is designed to expose one or more underlying MCP (Model Context Protocol) servers over various transport protocols, making them accessible to a wider range of clients.

The server is containerized using Docker for easy and consistent deployment, with flexible environment-based configuration supporting both production and development workflows.

## Features

- **Multiple Transports**: Expose MCP servers over `stdio`, `sse` (Server-Sent Events), or `http`.
- **Flexible Configuration**: Easily configure which MCP servers to proxy by editing the `servers.json` file.
- **Environment-Based Setup**: Use `.env` file for easy configuration management across different environments.
- **Lightweight & Fast**: Built on the efficient FastMCP library and runs in a small Alpine Linux container.
- **Dual Docker Configurations**: Optimized Dockerfiles for both production and development workflows.
- **MCP Server Support**: Supports both Node.js (`npx`) and Python (`uvx`) based MCP servers.
- **Cross-Platform Development**: Includes `.gitattributes` for consistent line endings across different operating systems.

## Requirements

- Docker and Docker Compose
- `.env` file for environment configuration (provided)

---

## How to Run

This project uses environment variables for flexible configuration. All settings are controlled via the `.env` file, which you can modify or override as needed.

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sokunmin/mcp-proxy.git
    cd mcp-proxy
    ```

2.  **Review the `.env` file:**
    ```bash
    cat .env
    ```
    Default values:
    ```
    TZ=Etc/UTC
    HOST=0.0.0.0
    TRANSPORT=sse
    PORT=8000
    ```

3.  **Run with default settings (development mode):**
    ```bash
    docker-compose up --build
    ```
    The server will be accessible at `http://localhost:8000`.

### Running Different Modes

#### Development Mode (Default)
```bash
# Uses Dockerfile.dev for faster builds
docker-compose up mcp-proxy
```

#### Production Mode
```bash
# Uses Dockerfile for smaller images
docker-compose up mcp-proxy-prod
```

### Transport Protocols

The proxy supports both **SSE (Server-Sent Events)** and **HTTP** transports. You can switch between them by modifying the `TRANSPORT` variable.

#### Using SSE Transport (Default)
```bash
# .env file already has TRANSPORT=sse
docker-compose up mcp-proxy
```

#### Using HTTP Transport
```bash
# Method 1: Edit .env file
# Change TRANSPORT=http in .env file
docker-compose up mcp-proxy

# Method 2: Override environment variable
TRANSPORT=http PORT=8001 docker-compose up mcp-proxy
```

### Environment Configuration

#### Using the .env File

Modify the `.env` file to change default behavior:

```bash
# Edit .env file
vim .env

# Example: Change to HTTP transport on port 8001
TRANSPORT=http
PORT=8001

# Run with new settings
docker-compose up mcp-proxy
```

#### Override Environment Variables

You can override `.env` values using environment variables:

```bash
# Run with HTTP transport on port 8001
TRANSPORT=http PORT=8001 docker-compose up mcp-proxy

# Run with SSE transport on custom port
TRANSPORT=sse PORT=9000 docker-compose up mcp-proxy

# Run production mode with custom settings
TRANSPORT=http PORT=8080 docker-compose up mcp-proxy-prod
```

#### Supported Environment Variables

- **`TRANSPORT`**: Transport protocol (`sse`, `http`, `stdio`) - Default: `sse`
- **`HOST`**: Host to bind to - Default: `0.0.0.0`
- **`PORT`**: Port to listen on - Default: `8000`
- **`TZ`**: Timezone - Default: `Etc/UTC`

#### Examples

```bash
# Development mode with default settings (SSE on port 8000)
docker-compose up mcp-proxy

# Production mode with HTTP transport
TRANSPORT=http PORT=8001 docker-compose up mcp-proxy-prod

# Development mode with custom port
PORT=9000 docker-compose up mcp-proxy

# HTTP transport on port 8001
TRANSPORT=http PORT=8001 docker-compose up mcp-proxy
```

---

## Configuration

To configure the proxy, edit the `servers.json` file. You can add, remove, or modify the MCP servers that you want to expose.

```json
{
  "mcpServers": {
    "context7": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "time": {
      "transport": "stdio",
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone", "Etc/UTC"]
    }
  }
}
```

---

## Docker Configuration Details

### Production Dockerfile
- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-alpine`
- **Size**: Smaller, optimized for deployment
- **Build Time**: Standard (no build cache)
- **Use Case**: Production deployments, CI/CD pipelines
- **Service**: `mcp-proxy-prod`

### Development Dockerfile (`Dockerfile.dev`)
- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-alpine`
- **Size**: Larger (~20-30% due to bytecode compilation)
- **Build Time**: Faster (with build cache and layer optimization)
- **Features**:
  - Build cache mounts for faster dependency installation
  - Layer caching for efficient rebuilds
  - Bytecode compilation for better runtime performance
- **Use Case**: Active development, frequent code changes
- **Service**: `mcp-proxy` (default)

### Environment Configuration
- **`.env` file**: Contains default environment variables
- **Variable override**: Environment variables can be overridden at runtime
- **Cross-platform**: `.gitattributes` ensures consistent line endings across Windows/Unix systems

---

## How to Test

You can test the running proxy using any MCP-compliant client or a tool like `curl`.

### Testing SSE Transport (Port 8000)
```bash
# Test the SSE endpoint
curl http://localhost:8000/sse/

# Check server health
curl http://localhost:8000/
```

### Testing HTTP Transport (Port 8001)
```bash
# Test the HTTP endpoint
curl http://localhost:8001/

# Check server health
curl http://localhost:8001/
```

### Testing with Different Services
```bash
# Test default service (SSE development)
docker-compose up mcp-proxy
curl http://localhost:8000/sse/

# Test HTTP transport
TRANSPORT=http PORT=8001 docker-compose up mcp-proxy
curl http://localhost:8001/

# Test production mode
docker-compose up mcp-proxy-prod
curl http://localhost:8000/sse/

# Test production mode with HTTP transport
TRANSPORT=http PORT=8001 docker-compose up mcp-proxy-prod
curl http://localhost:8001/
```

### Testing MCP Servers

The proxy currently supports these MCP servers:

- **context7**: Document search and context retrieval (Node.js via `npx`)
- **fetch**: Web content fetching (Python via `uvx`)
- **time**: Time and timezone operations (Python via `uvx`)

All servers are automatically started by the proxy when needed.

---

## Troubleshooting

### Common Issues

1. **Node.js dependency errors**: Ensure you're using the correct Dockerfile (not copying Node.js binaries between stages)
2. **Build cache issues**: Use `docker-compose down` and `docker-compose up --build` to force a clean rebuild
3. **Port conflicts**: Make sure port 8000 is not in use by other applications

### Development Tips

- Use `Dockerfile.dev` for faster iteration during development
- Use `Dockerfile` for smaller production images
- Modify `.env` file for persistent configuration changes
- Use environment variable overrides for temporary changes
- The `servers.json` file is mounted as a volume, so changes take effect on container restart
- Cross-platform development is supported with `.gitattributes` for consistent line endings

---

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.

For development setup, use the development Docker configuration for faster build times and better debugging experience.
