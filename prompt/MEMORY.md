# Project Memory & Context

## 1. Project Overview

This project is focused on the development of a **Model Context Protocol (MCP) proxy server**. The server is built using Python 3.12 and the **FastMCP** library. Its primary function is to act as an intermediary, proxying requests to other backend MCP servers (like `context7`, `fetch`, and `time`). The architecture is designed to be deployable locally, within a Docker container, or on serverless platforms like Cloudflare.

## 2. Technical Stack & Dependencies

*   **Language**: Python 3.12
*   **Core Framework**: FastMCP
*   **Web Server**: Uvicorn (as seen in `requirements.txt`)
*   **Package Management**: `uv` is the specified tool for managing the Python environment.
*   **Runtime Dependencies**:
    *   Python packages are defined in `requirements.txt`.
    *   **Node.js/npx**: This is a critical system-level dependency. The proxy server starts the `context7` MCP server using the `npx` command, so Node.js must be available in the execution environment.

## 3. Development & Testing Environment (Docker)

To facilitate consistent and reproducible local development and testing, we have created a containerized environment using Docker.

### `Dockerfile`

A `Dockerfile` has been added to the project root. Its key characteristics are:

*   **Base Image**: It uses `ghcr.io/astral-sh/uv:python3.12-alpine`, which is a lightweight and efficient image that comes with Python and `uv` pre-installed.
*   **Dependency Installation**:
    *   It uses the `apk` package manager to install the `nodejs` and `npm` runtime dependencies.
    *   It uses `uv pip install` to install the Python packages from `requirements.txt`.
*   **Application Code**: It copies the entire project directory into the `/app` directory within the container.
*   **Execution**: It exposes port `8000` and sets the default command to start the server in SSE mode, listening on all network interfaces (`CMD ["python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]`).

### `docker-compose.yml`

To simplify the development workflow, a `docker-compose.yml` file was created. It defines a single service (`mcp-proxy`) with the following configuration:

*   **Build**: It builds the Docker image from the `Dockerfile` in the current directory.
*   **Port Mapping**: It maps port `8000` on the host machine to port `8000` in the container, making the server accessible at `http://localhost:8000`.
*   **Volume Mounting**: It mounts the local project directory (`.`) to the `/app` directory in the container. This is crucial for development, as it allows for **live code changes**. Any modifications made to the local files will be immediately reflected in the running container without needing to rebuild the image.

## 4. How to Run the Project

To build the Docker image and start the MCP proxy server, run the following command from the project root:

```bash
docker-compose up
```

## 5. Session History

The current state was reached after the user requested a way to run and test the server locally. The plan was to use Docker. We analyzed `mcp_proxy.py` to understand its runtime dependencies (specifically `npx`) and startup commands. Based on this, a `Dockerfile` and `docker-compose.yml` were drafted. The initial `Dockerfile` was improved upon the user's suggestion to use the more efficient `ghcr.io/astral-sh/uv:python3.12-alpine` base image. The final files were then written to the project directory.
