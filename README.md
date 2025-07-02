
# FastMCP Proxy

This project provides a simple and flexible proxy server built with FastMCP. It is designed to expose one or more underlying MCP (Model Context Protocol) servers over various transport protocols, making them accessible to a wider range of clients.

## Features

- **Multiple Transports**: Expose MCP servers over `stdio`, `sse` (Server-Sent Events), or `http`.
- **Flexible Configuration**: Easily configure which MCP servers to proxy by editing the `proxy_config` dictionary in `mcp_proxy.py`.
- **Lightweight**: Built on the efficient and powerful FastMCP library.

## Requirements

- Python 3.12+
- `fastmcp>=2.9.0`

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd mcp-proxy
    ```

2.  **Install the required dependencies:**

    It is highly recommended to use a virtual environment.

    ```bash
    # Create and activate a virtual environment (optional but recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install dependencies
    pip install -r requirements.txt
    ```

## Configuration

To configure the proxy, edit the `proxy_config` dictionary in the `mcp_proxy.py` file. You can add, remove, or modify the MCP servers that you want to expose.

By default, the proxy is configured to expose the `time` MCP server, but this can be easily changed to any other server, such as `context7`.

```python
# Define the MCP server(s) we want to proxy
proxy_config = {
    "mcpServers": {
        # Example: context7 server
        # "context7": {
        #     "transport": "stdio",
        #     "command": "npx",
        #     "args": ["-y", "@upstash/context7-mcp"]
        # },

        # Example: time server (currently active)
        "time": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-time"]
        }
    }
}
```

## Usage

Run the proxy from your terminal by specifying the desired transport protocol. The server will start and begin listening for connections.

### Stdio Transport

For direct, local communication between processes.

```bash
python mcp_proxy.py stdio
```

### SSE (Server-Sent Events) Transport

For web clients that need a persistent, one-way connection from the server.

```bash
# Run on the default port (8000)
python mcp_proxy.py sse

# Run on a custom port
python mcp_proxy.py sse --port 8080
```

### HTTP Transport

For standard request-response interactions with web clients.

```bash
# Run on the default port (8001)
python mcp_proxy.py http

# Run on a custom port
python mcp_proxy.py http --port 8081
```

## How to Test

You can test the proxy using the `fastmcp` command-line tool or any other MCP-compliant client.

### Testing with `fastmcp`

To test the `stdio` transport, you can use a configuration file to tell the `fastmcp` client how to connect.

1.  **Create a configuration file** (e.g., `client_config.json`):

    ```json
    {
        "mcpServers": {
            "my-proxy": {
                "transport": "stdio",
                "command": "python",
                "args": ["/path/to/your/mcp_proxy.py", "stdio"]
            }
        }
    }
    ```

    *Make sure to replace `/path/to/your/mcp_proxy.py` with the actual absolute path to the script.*

2.  **Run the client**:

    ```bash
    fastmcp run --config client_config.json list-tools
    ```

    This command will start the proxy, connect to it, and list the available tools from the proxied server.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.
