"""Create a local SSE server that proxies requests to a stdio MCP server."""

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

import uvicorn
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.server import Server as MCPServerSDK  # Renamed to avoid conflict
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute, Mount, Route
from starlette.types import Receive, Scope, Send

from .proxy_server import create_proxy_server

logger = logging.getLogger(__name__)


@dataclass
class MCPServerSettings:
    """Settings for the MCP server."""

    bind_host: str
    port: int
    stateless: bool = False
    allow_origins: list[str] | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


# To store last activity for multiple servers if needed, though status endpoint is global for now.
_global_status: dict[str, Any] = {
    "api_last_activity": datetime.now(timezone.utc).isoformat(),
    "server_instances": {},  # Could be used to store per-instance status later
}


def _update_global_activity() -> None:
    _global_status["api_last_activity"] = datetime.now(timezone.utc).isoformat()


async def _handle_status(_: Request) -> Response:
    """Global health check and service usage monitoring endpoint."""
    return JSONResponse(_global_status)


def create_single_instance_routes(
    mcp_server_instance: MCPServerSDK[object],
    *,
    stateless_instance: bool,
) -> tuple[list[BaseRoute], StreamableHTTPSessionManager]:  # Return the manager itself
    """Create Starlette routes and the HTTP session manager for a single MCP server instance."""
    logger.debug(
        "Creating routes for a single MCP server instance (stateless: %s)",
        stateless_instance,
    )

    sse_transport = SseServerTransport("/messages/")
    http_session_manager = StreamableHTTPSessionManager(
        app=mcp_server_instance,
        event_store=None,
        json_response=True,
        stateless=stateless_instance,
    )

    async def handle_sse_instance(request: Request) -> None:
        async with sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            _update_global_activity()
            await mcp_server_instance.run(
                read_stream,
                write_stream,
                mcp_server_instance.create_initialization_options(),
            )

    async def handle_streamable_http_instance(scope: Scope, receive: Receive, send: Send) -> None:
        _update_global_activity()
        await http_session_manager.handle_request(scope, receive, send)

    routes = [
        Mount("/mcp", app=handle_streamable_http_instance),
        Route("/sse", endpoint=handle_sse_instance),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
    return routes, http_session_manager


class LazyServerProvider:
    """Manages the on-demand startup of named MCP server instances."""

    def __init__(
        self,
        server_params: dict[str, StdioServerParameters],
        exit_stack: contextlib.AsyncExitStack,
        stateless: bool,
    ) -> None:
        self._server_params = server_params
        self._exit_stack = exit_stack
        self._stateless = stateless
        self._proxies: dict[str, MCPServerSDK[object]] = {}
        self._apps: dict[str, Starlette] = {}
        self._locks: dict[str, asyncio.Lock] = {name: asyncio.Lock() for name in server_params}

    async def get_app(self, name: str) -> Starlette | None:
        """Get a Starlette application for a named server, creating it on first request."""
        if name not in self._server_params:
            return None

        if name in self._apps:
            return self._apps[name]

        async with self._locks[name]:
            if name in self._apps:
                return self._apps[name]

            params = self._server_params[name]
            logger.info(
                "Lazily starting named server '%s': %s %s",
                name,
                params.command,
                " ".join(params.args),
            )
            try:
                stdio_streams = await self._exit_stack.enter_async_context(stdio_client(params))
                session = await self._exit_stack.enter_async_context(ClientSession(*stdio_streams))
                proxy = await create_proxy_server(session)
                self._proxies[name] = proxy

                instance_routes, http_manager = create_single_instance_routes(
                    proxy,
                    stateless_instance=self._stateless,
                )
                await self._exit_stack.enter_async_context(http_manager.run())

                app = Starlette(routes=instance_routes)
                self._apps[name] = app
                _global_status["server_instances"][name] = "running"
                return app
            except Exception:
                logger.exception("Failed to lazily start server '%s'", name)
                _global_status["server_instances"][name] = "failed"
                return None


async def run_mcp_server(
    mcp_settings: MCPServerSettings,
    default_server_params: StdioServerParameters | None = None,
    named_server_params: dict[str, StdioServerParameters] | None = None,
) -> None:
    """Run stdio client(s) and expose an MCP server with multiple possible backends."""
    if named_server_params is None:
        named_server_params = {}

    all_routes: list[BaseRoute] = [
        Route("/status", endpoint=_handle_status),
    ]

    async with contextlib.AsyncExitStack() as stack:

        @contextlib.asynccontextmanager
        async def combined_lifespan(_app: Starlette) -> AsyncIterator[None]:
            logger.info("Main application lifespan starting...")
            yield
            logger.info("Main application lifespan shutting down...")

        if default_server_params:
            logger.info(
                "Setting up default server: %s %s",
                default_server_params.command,
                " ".join(default_server_params.args),
            )
            stdio_streams = await stack.enter_async_context(stdio_client(default_server_params))
            session = await stack.enter_async_context(ClientSession(*stdio_streams))
            proxy = await create_proxy_server(session)
            instance_routes, http_manager = create_single_instance_routes(
                proxy, stateless_instance=mcp_settings.stateless
            )
            await stack.enter_async_context(http_manager.run())
            all_routes.extend(instance_routes)
            _global_status["server_instances"]["default"] = "running"

        lazy_server_provider = LazyServerProvider(
            named_server_params,
            stack,
            mcp_settings.stateless,
        )

        if named_server_params:

            async def app_factory(scope: Scope, receive: Receive, send: Send) -> None:
                path_parts = scope["path"].split("/")
                if len(path_parts) > 2:
                    server_name = path_parts[2]
                    app = await lazy_server_provider.get_app(server_name)
                    if app:
                        # Adjust the scope to be relative to the mounted app
                        original_path = scope["path"]
                        scope["path"] = original_path.split(f"/servers/{server_name}", 1)[-1]
                        await app(scope, receive, send)
                        scope["path"] = original_path  # Restore for safety
                    else:
                        response = JSONResponse(
                            {"error": f"Server '{server_name}' not available or failed to start."},
                            status_code=503,
                        )
                        await response(scope, receive, send)
                else:
                    # Handle case where /servers/ is accessed without a server name
                    response = JSONResponse(
                        {"error": "Please specify a server name, e.g., /servers/my-server"},
                        status_code=404,
                    )
                    await response(scope, receive, send)

            all_routes.append(Mount("/servers", app=app_factory))
            for name in named_server_params:
                _global_status["server_instances"][name] = "available"

        if not default_server_params and not named_server_params:
            logger.error("No servers configured to run.")
            return

        middleware = (
            [
                Middleware(
                    CORSMiddleware,
                    allow_origins=mcp_settings.allow_origins,
                    allow_methods=["*"],
                    allow_headers=["*"],
                )
            ]
            if mcp_settings.allow_origins
            else []
        )

        starlette_app = Starlette(
            debug=(mcp_settings.log_level == "DEBUG"),
            routes=all_routes,
            middleware=middleware,
            lifespan=combined_lifespan,
        )

        logger.info("Starlette app created. Starting Uvicorn server...")

        config = uvicorn.Config(
            starlette_app,
            host=mcp_settings.bind_host,
            port=mcp_settings.port,
            log_level=mcp_settings.log_level.lower(),
        )
        http_server = uvicorn.Server(config)

        logger.info("Uvicorn server configured. Starting to serve...")

        base_url = f"http://{mcp_settings.bind_host}:{mcp_settings.port}"
        sse_urls = [f"{base_url}/sse"] if default_server_params else []
        sse_urls.extend([f"{base_url}/servers/{name}/sse" for name in named_server_params])

        if sse_urls:
            logger.info("Serving MCP Servers via SSE:")
            for url in sse_urls:
                logger.info("  - %s", url)

        logger.debug(
            "Serving incoming MCP requests on %s:%s",
            mcp_settings.bind_host,
            mcp_settings.port,
        )
        await http_server.serve()
