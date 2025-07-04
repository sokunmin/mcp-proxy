
import asyncio
import argparse
import json
from fastmcp import FastMCP, Client

# Load server configuration from a JSON file
with open('servers.json', 'r') as f:
    proxy_config = json.load(f)

# Create a FastMCP application instance that acts as a proxy
# FastMCP.as_proxy() handles the internal creation and mounting of clients
proxy_client = Client(proxy_config)
app = FastMCP.as_proxy(backend=proxy_client)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastMCP proxy server.")
    subparsers = parser.add_subparsers(dest="transport", required=True, help="Transport protocol to use")

    # Stdio transport
    parser_stdio = subparsers.add_parser("stdio", help="Run with stdio transport")

    # SSE (Server-Sent Events) transport
    parser_sse = subparsers.add_parser("sse", help="Run with SSE transport")
    parser_sse.add_argument("--port", type=int, default=8000, help="Port to run the SSE server on")
    parser_sse.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the SSE server to")

    # Streamable HTTP transport
    parser_http = subparsers.add_parser("http", help="Run with Streamable HTTP transport")
    parser_http.add_argument("--port", type=int, default=8001, help="Port to run the HTTP server on")
    parser_http.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the HTTP server to")

    args = parser.parse_args()

    print(f"Starting proxy with {args.transport} transport...")

    if args.transport == "stdio":
        # Run the server over standard input/output
        app.run(transport="stdio")
    elif args.transport == "sse":
        # Run the server with Server-Sent Events
        app.run(transport="sse", port=args.port, host=args.host)
    elif args.transport == "http":
        # Run the server with streamable HTTP
        app.run(transport="http", port=args.port, host=args.host)
