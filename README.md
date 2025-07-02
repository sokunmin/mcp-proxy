# FastMCP Proxy Server

This project provides a simple and flexible proxy server built with **FastMCP**. It is designed to expose one or more underlying MCP (Model Context Protocol) servers over various transport protocols, making them accessible to a wider range of clients.

The server is containerized using Docker for easy and consistent deployment.

## Features

- **Multiple Transports**: Expose MCP servers over `stdio`, `sse` (Server-Sent Events), or `http`.
- **Flexible Configuration**: Easily configure which MCP servers to proxy by editing the `servers.json` file.
- **Lightweight & Fast**: Built on the efficient FastMCP library and runs in a small Alpine Linux container.
- **Containerized**: Docker and Docker Compose files are provided for a one-command setup.

## Requirements

- Docker and Docker Compose

---

## How to Run

This project is designed to be run with Docker. This is the easiest and most consistent way to run the server, as it handles all dependencies for you.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mcp-proxy
    ```

2.  **Build and Run the Server:**
    The default command will start the server in `sse` mode.
    ```bash
    docker-compose up --build
    ```
    The `--build` flag is important to ensure any changes to the `Dockerfile` or your source code are applied.

    The server will be accessible at `http://localhost:8000`. Because the project files are mounted as a volume, you can edit the `servers.json` file on your local machine, and the changes will be reflected the next time you restart the container.

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

## How to Test

You can test the running proxy using any MCP-compliant client or a tool like `curl`.

```bash
# Test the SSE endpoint
curl http://localhost:8000/

# Test the HTTP endpoint (if running)
curl http://localhost:8001/
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.
