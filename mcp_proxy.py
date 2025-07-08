
import asyncio
import argparse
import json
import logging
from fastmcp import FastMCP, Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Load server configuration from a JSON file
    with open('servers.json', 'r') as f:
        proxy_config = json.load(f)
    
    logger.info(f"Loaded configuration for {len(proxy_config['mcpServers'])} servers")
    
    # Create a FastMCP application instance that acts as a proxy
    # This preserves lazy loading - servers are started when first accessed
    proxy_client = Client(proxy_config)
    app = FastMCP.as_proxy(backend=proxy_client)
    
    # Add minimal health check endpoint for Smithery
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint"""
        return {"status": "healthy", "servers": list(proxy_config["mcpServers"].keys())}
        
except Exception as e:
    logger.error(f"Failed to initialize MCP proxy: {e}")
    raise

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

    logger.info(f"Starting proxy with {args.transport} transport (lazy loading enabled)...")

    try:
        if args.transport == "stdio":
            app.run(transport="stdio")
        elif args.transport == "sse":
            logger.info(f"Starting SSE server on {args.host}:{args.port}")
            app.run(transport="sse", port=args.port, host=args.host)
        elif args.transport == "http":
            logger.info(f"Starting HTTP server on {args.host}:{args.port}")
            app.run(transport="http", port=args.port, host=args.host)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
