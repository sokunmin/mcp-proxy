# Plan to Implement Lazy Loading in MCP-Proxy

The goal is to modify the `mcp-proxy` server to support lazy loading of named servers. This will address the timeout issue when deploying to Smithery.

## 1. Introduce a `LazyServerProvider` Class

I will create a new class called `LazyServerProvider` in `src/mcp_proxy/mcp_server.py`. This class will be responsible for:

*   Holding the configurations for all named servers.
*   Keeping track of which server processes are currently running.
*   Spawning a server process only when it's requested for the first time.
*   Caching the running server instance for subsequent requests.
*   Using a locking mechanism to prevent race conditions when starting servers.

## 2. Refactor `run_mcp_server`

I will modify the `run_mcp_server` function in `src/mcp_proxy/mcp_server.py` to use the `LazyServerProvider`. The changes will include:

*   Instead of iterating through the named servers and starting them all at once, the server will instantiate the `LazyServerProvider`.
*   The server will then create a dynamic "app factory" for each named server. This factory will be a function that Starlette can call to get the application for a specific server.
*   When a request for a named server comes in, the app factory will use the `LazyServerProvider` to get the corresponding application. If the application isn't running, the provider will start it.

## 3. Add `asyncio` Import

I will add `import asyncio` at the top of `src/mcp_proxy/mcp_server.py` to support the asynchronous locking mechanism in the `LazyServerProvider`.

This plan will ensure that the `mcp-proxy` server starts up almost instantly, as it will no longer wait for all the underlying servers to start. This should resolve the timeout error from Smithery.