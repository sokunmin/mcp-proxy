# Project Memory & Context

## 1. Project Overview

This project is focused on the development of a **Model Context Protocol (MCP) proxy server**. The server is built using Python 3.12 and the **FastMCP** library. Its primary function is to act as an intermediary, proxying requests to other backend MCP servers. The architecture is designed to be deployable locally, within a Docker container, or on serverless platforms like Cloudflare.

## 2. Technical Stack & Dependencies

*   **Language**: Python 3.12
*   **Core Framework**: FastMCP
*   **Web Server**: Uvicorn (as seen in `requirements.txt`)
*   **Configuration**: Server definitions are externalized in a `servers.json` file.
*   **Package Management**: `uv` is the specified tool for managing the Python environment.
*   **Runtime Dependencies**:
    *   Python packages are defined in `requirements.txt`.
    *   **Node.js/npx**: This is a critical system-level dependency. The proxy server starts the `context7` MCP server using the `npx` command, so Node.js must be available in the execution environment.

## 3. Refactoring for Flexibility

The project was initially implemented with a hardcoded proxy configuration in `mcp_proxy.py`. To make the server more generic and flexible, the following refactoring was performed:

1.  **Externalized Configuration**: A `servers.json` file was created to store the list of MCP servers to be proxied. This allows for adding or modifying server definitions without changing the Python code.
2.  **Dynamic Loading**: The `mcp_proxy.py` script was modified to read and parse `servers.json` at startup, dynamically building the proxy configuration.

## 4. Development & Testing Environment (Docker)

To facilitate consistent and reproducible local development and testing, we have created a containerized environment using Docker.

### `Dockerfile`

A `Dockerfile` has been added to the project root. Its key characteristics are:

*   **Base Image**: It uses `ghcr.io/astral-sh/uv:python3.12-alpine`, which is a lightweight and efficient image that comes with Python and `uv` pre-installed.
*   **Dependency Installation**:
    *   It uses the `apk` package manager to install the `nodejs` and `npm` runtime dependencies.
    *   It uses `uv pip install` to install the Python packages from `requirements.txt`.
*   **Application Code**: It copies the application code, `requirements.txt`, and `servers.json` into the `/app` directory within the container.
*   **Execution**: It exposes port `8000` and sets the default command to start the server in SSE mode, listening on all network interfaces (`CMD ["python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]`).

### `docker-compose.yml`

To simplify the development workflow, a `docker-compose.yml` file was created. It defines a single service (`mcp-proxy`) with the following configuration:

*   **Build**: It builds the Docker image from the `Dockerfile` in the current directory.
*   **Port Mapping**: It maps port `8000` on the host machine to port `8000` in the container, making the server accessible at `http://localhost:8000`.
*   **Volume Mounting**: It mounts the local project directory (`.`) to the `/app` directory in the container. This is crucial for development, as it allows for **live code changes**.
*   **Timezone**: The `TZ` environment variable is set to `Etc/UTC` to ensure consistent timezone handling within the container.

## 5. Debugging History: The `mcp-server-time` Issue

After refactoring, the `time` MCP server was consistently failing to start within the Docker container.

*   **Initial Analysis**: The logs revealed that the server was crashing due to an inability to determine the local timezone, which triggered a secondary error (`AttributeError: 'str' object has no attribute 'message'`).
*   **Solution Attempt 1**: The `docker-compose.yml` file was updated to set the `TZ=Etc/UTC` environment variable. This did not resolve the issue because the container was not rebuilt.
*   **Solution Attempt 2 (Successful)**: A more direct solution was implemented by modifying `servers.json` to pass the timezone explicitly to the `mcp-server-time` command using the `--local-timezone` flag:
    ```json
    "args": ["mcp-server-time", "--local-timezone", "Etc/UTC"]
    ```
    This approach directly configures the application and is more robust than relying on an environment variable.

## 6. How to Run the Project

To build the Docker image and start the MCP proxy server, run the following command from the project root. The `--build` flag is important to ensure any changes to the `Dockerfile` or application code are included.

```bash
docker-compose up --build
```