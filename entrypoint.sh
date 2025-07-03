#!/bin/sh
set -e

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

# Build command arguments
ARGS="$TRANSPORT"

# Add host and port for network transports (not stdio)
if [ "$TRANSPORT" != "stdio" ]; then
    ARGS="$ARGS --host $HOST --port $PORT"
fi

echo "Starting MCP proxy with transport: $TRANSPORT"
if [ "$TRANSPORT" != "stdio" ]; then
    echo "Server will be accessible at: http://$HOST:$PORT"
fi

# Execute the Python application with the constructed arguments
exec python mcp_proxy.py $ARGS