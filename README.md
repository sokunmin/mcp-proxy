# FastMCP Proxy Server

This project provides a simple and flexible proxy server built with **FastMCP**. It is designed to expose one or more underlying MCP (Model Context Protocol) servers over various transport protocols, making them accessible to a wider range of clients.

The server is containerized using Docker for easy and consistent deployment, with optimized configurations for both production and development environments.

## Features

- **Multiple Transports**: Expose MCP servers over `stdio`, `sse` (Server-Sent Events), or `http`.
- **Flexible Configuration**: Easily configure which MCP servers to proxy by editing the `servers.json` file.
- **Lightweight & Fast**: Built on the efficient FastMCP library and runs in a small Alpine Linux container.
- **Dual Docker Configurations**: Optimized Dockerfiles for both production and development workflows.
- **MCP Server Support**: Supports both Node.js (`npx`) and Python (`uvx`) based MCP servers.

## Requirements

- Docker and Docker Compose

---

## How to Run

This project provides two Docker configurations:

- **`Dockerfile`** - Production-optimized (smaller images, simpler)
- **`Dockerfile.dev`** - Development-optimized (faster builds, better caching)

### Production Mode (Recommended)

For production deployment or when you want the smallest possible image:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mcp-proxy
    ```

2.  **Build and Run the Server:**
    ```bash
    docker-compose up --build
    ```
    The `--build` flag ensures any changes to the `Dockerfile` or source code are applied.

    The server will be accessible at `http://localhost:8000`.

### Development Mode

For active development with faster rebuild times:

1.  **Use the development Dockerfile:**
    ```bash
    docker-compose -f docker-compose.yml up --build
    ```
    Or modify `docker-compose.yml` to use `Dockerfile.dev`:
    ```yaml
    build:
      context: .
      dockerfile: Dockerfile.dev
    ```

2.  **Benefits of development mode:**
    - Faster rebuilds (only application code layer rebuilds when you change code)
    - Build cache optimization for dependencies
    - Better development iteration speed

**Note**: The project files are mounted as a volume, so you can edit the `servers.json` file on your local machine, and changes will be reflected when you restart the container.

### Running Different Transports

To run the server with a different transport (`http` or `stdio`), you can override the default command in the `docker-compose.yml` file or directly with `docker-compose run`.

*   **To run with HTTP transport:**
    ```bash
    # This starts the service on port 8001
    docker-compose run --rm --service-ports mcp-proxy python mcp_proxy.py http --host 0.0.0.0 --port 8001
    ```

*   **To run with Stdio transport:**
    ```bash
    # This starts the service and attaches your terminal to its stdio
    docker-compose run --rm mcp-proxy python mcp_proxy.py stdio
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

### Development Dockerfile (`Dockerfile.dev`)
- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-alpine`
- **Size**: Larger (~20-30% due to bytecode compilation)
- **Build Time**: Faster (with build cache and layer optimization)
- **Features**:
  - Build cache mounts for faster dependency installation
  - Layer caching for efficient rebuilds
  - Bytecode compilation for better runtime performance
- **Use Case**: Active development, frequent code changes

---

## How to Test

You can test the running proxy using any MCP-compliant client or a tool like `curl`.

```bash
# Test the SSE endpoint
curl http://localhost:8000/sse/

# Check server health
curl http://localhost:8000/

# Test the HTTP endpoint (if running on port 8001)
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
- The `servers.json` file is mounted as a volume, so changes take effect on container restart

---

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.

For development setup, use the development Docker configuration for faster build times and better debugging experience.
