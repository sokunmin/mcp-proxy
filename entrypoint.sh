#!/bin/sh
set -e

# Enable debug mode if DEBUG is set
if [ "$DEBUG" = "true" ]; then
    set -x
fi

# Default values
TRANSPORT=${TRANSPORT:-sse}
HOST=${HOST:-0.0.0.0}

# Set default port based on transport if not specified
if [ -z "$PORT" ]; then
    case "$TRANSPORT" in
        sse)
            PORT=8000
            ;;
        http)
            PORT=8001
            ;;
        stdio)
            PORT=""
            ;;
        *)
            echo "Error: Unsupported transport '$TRANSPORT'. Supported: sse, http, stdio"
            exit 1
            ;;
    esac
fi

# Verify runtime package managers are available (for lazy loading)
echo "Verifying runtime package managers..."
command -v python >/dev/null 2>&1 || { echo "Python not found"; exit 1; }
command -v npx >/dev/null 2>&1 || { echo "npx not found"; exit 1; }
command -v uvx >/dev/null 2>&1 || { echo "uvx not found"; exit 1; }

# Test servers.json exists and is valid JSON
if [ ! -f "servers.json" ]; then
    echo "Error: servers.json not found"
    exit 1
fi

# Validate JSON syntax
python -m json.tool servers.json > /dev/null 2>&1 || { echo "Error: Invalid JSON in servers.json"; exit 1; }

# Build command arguments
ARGS="$TRANSPORT"

# Add host and port for network transports (not stdio)
if [ "$TRANSPORT" != "stdio" ]; then
    ARGS="$ARGS --host $HOST --port $PORT"
fi

echo "Starting MCP proxy with transport: $TRANSPORT"
echo "Lazy loading enabled for: npx, uvx"
if [ "$TRANSPORT" != "stdio" ]; then
    echo "Server will be accessible at: http://$HOST:$PORT"
fi

# Execute the Python application with the constructed arguments
exec python mcp_proxy.py $ARGS