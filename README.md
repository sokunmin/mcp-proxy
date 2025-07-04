
# FastMCP Proxy Server

This project provides a simple and flexible proxy server built with **FastMCP**. It is designed to expose one or more underlying MCP (Model Context Protocol) servers over various transport protocols, making them accessible to a wider range of clients.

The server is containerized using Docker for easy and consistent deployment, optimized for production environments.

## Features

- **Multiple Transports**: Expose MCP servers over `stdio`, `sse` (Server-Sent Events), or `http`.
- **Flexible Configuration**: Easily configure which MCP servers to proxy by editing the `servers.json` file.
- **Lightweight & Fast**: Built on the efficient FastMCP library and runs in a small Alpine Linux container.
- **Production Ready**: Optimized Docker configuration for production deployment.
- **MCP Server Support**: Supports both Node.js (`npx`) and Python (`uvx`) based MCP servers.

## Requirements

- Docker and Docker Compose

---

## How to Run

This project is designed for production deployment using Docker. You can run it using either Docker Compose or direct Docker commands:

### Prerequisites

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sokunmin/mcp-proxy.git
    cd mcp-proxy
    ```

### Method 1: Using Docker Compose (Recommended)

The easiest way to run the proxy with predefined configuration:

```bash
# Run with default settings (SSE transport, port 8000)
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the service
docker-compose down
```

#### Override Environment Variables

You can override the default transport without editing files:

```bash
# Run with HTTP transport
TRANSPORT=http PORT=8001 docker-compose up

# Run with custom port
PORT=9000 docker-compose up

# Run with multiple overrides
TRANSPORT=http PORT=8080 docker-compose up
```

### Method 2: Using Docker Run

For more control over the container configuration:

#### Step 1: Build the Image
```bash
docker build -t mcp-proxy .
```

#### Step 2: Run the Container

**Option A: Using environment variables directly**

```bash
# SSE Transport (Default)
docker run -d --name mcp-proxy \
  -p 8000:8000 \
  -e TRANSPORT=sse \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e TZ=Etc/UTC \
  mcp-proxy

# HTTP Transport
docker run -d --name mcp-proxy-http \
  -p 8001:8001 \
  -e TRANSPORT=http \
  -e HOST=0.0.0.0 \
  -e PORT=8001 \
  -e TZ=Etc/UTC \
  mcp-proxy
```

**Option B: Using .env file with consistent PORT variable**

```bash
# Load environment variables from .env file
source .env

# Run with loaded variables
docker run -d --name mcp-proxy \
  -p ${PORT}:${PORT} \
  -e TRANSPORT=${TRANSPORT} \
  -e HOST=${HOST} \
  -e PORT=${PORT} \
  -e TZ=${TZ} \
  mcp-proxy

# For HTTP transport, override specific variables
TRANSPORT=http PORT=8001 docker run -d --name mcp-proxy-http \
  -p ${PORT}:${PORT} \
  -e TRANSPORT=${TRANSPORT} \
  -e HOST=${HOST} \
  -e PORT=${PORT} \
  -e TZ=${TZ} \
  mcp-proxy
```

**Option C: Using --env-file**

```bash
# Use .env file directly
docker run -d --name mcp-proxy \
  --env-file .env \
  -p 8000:8000 \
  mcp-proxy

# Override specific variables
docker run -d --name mcp-proxy-http \
  --env-file .env \
  -e TRANSPORT=http \
  -e PORT=8001 \
  -p 8001:8001 \
  mcp-proxy
```

#### Container Management

```bash
# View logs
docker logs mcp-proxy

# Stop the container
docker stop mcp-proxy

# Remove the container
docker rm mcp-proxy

# View running containers
docker ps
```

### Environment Variables

The following environment variables can be configured in the `.env` file or passed directly:

- **`TRANSPORT`**: Transport protocol (`sse`, `http`, `stdio`) - Default: `sse`
- **`HOST`**: Host to bind to - Default: `0.0.0.0`
- **`PORT`**: Port number for the service - Default: `8000`
- **`TZ`**: Timezone - Default: `Etc/UTC`

### Quick Start Examples

```bash
# Default SSE on port 8000
docker-compose up

# HTTP on port 8001
TRANSPORT=http PORT=8001 docker-compose up

# Custom port
PORT=9000 docker-compose up

# Run in background
docker-compose up -d
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

The `servers.json` file is mounted as a volume, so changes take effect on container restart.

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
# Test SSE service
docker-compose up mcp-proxy-sse
curl http://localhost:8000/sse/

# Test HTTP service
docker-compose up mcp-proxy-http
curl http://localhost:8001/
```

### Testing MCP Servers

The proxy currently supports these MCP servers:

- **context7**: Document search and context retrieval (Node.js via `npx`)
- **fetch**: Web content fetching (Python via `uvx`)
- **time**: Time and timezone operations (Python via `uvx`)

All servers are automatically started by the proxy when needed.

---

## Production Deployment

### Docker Configuration Details

- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-alpine`
- **Optimized**: Small size, production-ready
- **Security**: Runs as non-root user
- **Environment**: Configurable via environment variables

### Best Practices

1. **Use environment variables** for configuration instead of modifying files
2. **Mount `servers.json` as a volume** for easy configuration updates
3. **Use Docker Compose** for consistent deployment
4. **Monitor logs** using `docker-compose logs -f`
5. **Use health checks** to ensure service availability

### Scaling

For high-availability deployment, consider:
- Using multiple replicas behind a load balancer
- Implementing proper logging and monitoring
- Using container orchestration (Kubernetes, Docker Swarm)

---

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 8000/8001 are not in use by other applications
2. **Container build issues**: Use `docker-compose down` and `docker-compose up --build` to force a clean rebuild
3. **Configuration errors**: Check `servers.json` syntax and ensure all required fields are present

### Monitoring

Check service health:
```bash
# View logs
docker-compose logs -f mcp-proxy-sse

# Check container status
docker-compose ps

# Access container shell (if needed)
docker-compose exec mcp-proxy-sse sh
```

---

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.

For development setup, please use the `dev` branch which includes development-optimized configurations.
