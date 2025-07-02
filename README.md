# FastMCP Proxy Server

This project provides a simple and flexible proxy server built with **FastMCP**. It is designed to expose one or more underlying MCP (Model Context Protocol) servers over various transport protocols, making them accessible to a wider range of clients.

The server is containerized using Docker for easy and consistent deployment, but can also be run locally with Python.

## Features

- **Multiple Transports**: Expose MCP servers over `stdio`, `sse` (Server-Sent Events), or `http`.
- **Flexible Configuration**: Easily configure which MCP servers to proxy by editing the `proxy_config` dictionary in `mcp_proxy.py`.
- **Lightweight & Fast**: Built on the efficient FastMCP library and runs in a small Alpine Linux container.
- **Containerized**: Docker and Docker Compose files are provided for a one-command setup.

## Requirements

- **Recommended**: Docker and Docker Compose
- **Alternative**: Python 3.12+ and Node.js (for `npx`)

---

## How to Run (Using Docker - Recommended)

This is the easiest and most consistent way to run the server, as it handles all dependencies for you.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mcp-proxy-dev
    ```

2.  **Build and Run the Server:**
    The default command will start the server in `sse` mode.
    ```bash
    docker-compose up
    ```
    The server will be accessible at `http://localhost:8000`. Because the project files are mounted as a volume, you can edit the Python code on your local machine, and the server inside the container will update automatically.

### Running Different Transports with Docker

To run the server with a different transport (`http` or `stdio`), you can override the default command directly with `docker-compose run`.

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

## How to Run (Locally with Python)

If you prefer not to use Docker, you can run the server directly.

1.  **Install Dependencies:**
    Make sure you have Python 3.12+ and Node.js installed.
    ```bash
    # It is highly recommended to use a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install Python packages
    pip install -r requirements.txt
    ```

2.  **Run the Server:**
    Run the proxy from your terminal by specifying the desired transport protocol.

    *   **For Stdio Transport:**
        ```bash
        python mcp_proxy.py stdio
        ```

    *   **For SSE Transport:**
        ```bash
        # Run on the default port (8000)
        python mcp_proxy.py sse

        # Run on a custom port
        python mcp_proxy.py sse --port 8080
        ```

    *   **For HTTP Transport:**
        ```bash
        # Run on the default port (8001)
        python mcp_proxy.py http

        # Run on a custom port
        python mcp_proxy.py http --port 8081
        ```

---

## Configuration

To configure the proxy, edit the `proxy_config` dictionary in the `mcp_proxy.py` file. You can add, remove, or modify the MCP servers that you want to expose.

```python
# Define the MCP server(s) we want to proxy
proxy_config = {
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
            "args": ["mcp-server-time"]
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