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

## 7. Dockerfile Optimization and Debugging History

This section details the process of optimizing the `Dockerfile` and the debugging steps taken to resolve various issues.

### Goal of Optimization: `Dockerfile.optimized`

The objective was to create a more efficient and robust `Dockerfile` (`Dockerfile.optimized`) by incorporating best practices such as multi-stage builds and optimized layer caching, aiming for a smaller final image and faster rebuilds.

### Problem 1: `npx` Not Found (Initial `Dockerfile.optimized` Failure)

**Description of `Dockerfile.optimized` (Version 1)**

The first attempt at `Dockerfile.optimized` aimed for a multi-stage build and virtual environment usage:

```dockerfile
# Stage 1: Build and install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
WORKDIR /app
RUN uv venv
COPY requirements.txt servers.json ./
RUN uv pip install --no-cache-dir -r requirements.txt
COPY . .

# Stage 2: Create the final, smaller image
FROM python:3.12-alpine
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app .
EXPOSE 8000
CMD ["/app/.venv/bin/python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

**Symptoms**

The container would build successfully but fail to start the application. The logs indicated that `npx` (used by `mcp_proxy.py` to start `context7`) could not be found.

**Root Cause**

The `ENV PATH="/app/.venv/bin:$PATH"` instruction was present in the `builder` stage but was **missing from the final runtime stage**. Although Python packages were installed into the virtual environment, the system's `PATH` environment variable in the final image did not include the virtual environment's `bin` directory. Consequently, when `mcp_proxy.py` attempted to execute `npx`, the shell could not locate it.

**Resolution (for Problem 1)**

The `ENV PATH="/app/.venv/bin:$PATH"` instruction was added to the final stage of `Dockerfile.optimized`. This ensured that the virtual environment's `bin` directory (containing `python` and other scripts) was correctly added to the `PATH` in the runtime environment.

### Problem 2: `ModuleNotFoundError: No module named 'fastmcp'` (Debugging `sh -c` Issue)

**Description of `Dockerfile.optimized` (Version 2 - with debugging)**

After resolving Problem 1, the `Dockerfile.optimized` was updated to include extensive debugging steps, particularly by wrapping the `CMD` instruction in `sh -c`:

```dockerfile
# ... (Stage 1 and initial parts of Stage 2 remain similar) ...

# Add the virtual environment's bin directory to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# --- BUILD-TIME DEBUGGING ---
RUN echo "--- Build-time debug info ---" && \
    echo "Listing /app directory:" && ls -la /app && \
    echo "PATH is: $PATH" && \
    echo "which python:" && which python && \
    echo "which npx:" && which npx && \
    echo "---------------------------"

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the app with runtime debugging
CMD ["sh", "-c", "echo '--- Runtime debug info ---' && echo 'User: $(whoami)' && echo 'PWD: $(pwd)' && echo 'PATH: $PATH' && echo 'which python: $(which python)' && echo 'which npx: $(which npx)' && echo '--- Starting application ---' && python mcp_proxy.py sse --host 0.0.0.0 --port 8000"]
```

**Symptoms**

The container would build, and the runtime debug messages would print, showing that `PATH` was correctly set and `which python` pointed to `/app/.venv/bin/python`. However, the application would then crash with:

```
ModuleNotFoundError: No module named 'fastmcp'
```

**Root Cause**

The issue stemmed from the `CMD ["sh", "-c", "..."]` wrapper. While this form allows for executing multiple commands and shell features, it creates a new shell process. In some Docker environments, this new shell process does not fully or correctly inherit the `PATH` environment variable in a way that allows the Python interpreter to find modules installed within the virtual environment. It effectively caused the `python` command within the `sh -c` string to fall back to a system-wide Python interpreter that did not have `fastmcp` installed, despite the `PATH` variable appearing correct in the debug output.

**Resolution (for Problem 2)**

The debugging `sh -c` wrapper was removed, and the `CMD` instruction was reverted to its "exec form" using the absolute path to the Python executable within the virtual environment. This is the most robust and reliable way to ensure the correct Python interpreter (from the virtual environment) is used, and that it can find all installed modules.

### Problem 3: Still Stuck at 'Attaching to mcp-proxy-1' (Virtual Environment Copy Issue)

**Description of `Dockerfile.optimized` (Version 3 - Virtual Environment Copy)**

After addressing Problem 2, the `Dockerfile.optimized` was structured to use a multi-stage build where a Python virtual environment was created and populated in the `builder` stage, and then copied to the final `python:3.12-alpine` image. The `CMD` instruction used the absolute path to the Python executable within this copied virtual environment.

```dockerfile
# Stage 1: Build and install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
WORKDIR /app
RUN uv venv
COPY requirements.txt servers.json ./
RUN . .venv/bin/activate && uv pip install --no-cache-dir -r requirements.txt
COPY . .

# Stage 2: Create the final, smaller image
FROM python:3.12-alpine
RUN apk add --no-cache nodejs npm
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["/app/.venv/bin/python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

**Symptoms**

The container would build successfully, but upon running, it would get stuck at `Attaching to mcp-proxy-1` with no further application logs. This indicated that the Python application was still not starting correctly.

**Root Cause**

The primary cause of this persistent issue is the unreliability of copying a Python virtual environment between different Docker build stages, especially when the base images might have subtle differences (even within the same distribution family). While theoretically sound, in practice, the internal paths within the virtual environment can become invalid or misaligned after being copied, preventing the Python interpreter from correctly locating its installed packages. This leads to the application failing silently or with obscure errors that prevent it from logging its startup.

**Resolution (for Problem 3)**

The strategy was revised to install Python dependencies directly into the final image's system Python environment, mirroring the successful approach of the original `Dockerfile`, while retaining the multi-stage build for Node.js/npm isolation.

### Current `Dockerfile.optimized` (Final, Optimized Version)

The `Dockerfile.optimized` has been updated to the following, which combines multi-stage building for Node.js/npm with direct system-wide Python package installation for maximum reliability:

```dockerfile
# Stage 1: Build for Node.js and npm
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

# Install nodejs and npm
RUN apk add --no-cache nodejs npm

# Stage 2: Create the final, smaller image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy npx and its dependencies from the builder stage
COPY --from=builder /usr/bin/npx /usr/bin/
COPY --from=builder /usr/lib/node_modules /usr/lib/node_modules

# Copy requirements and install Python dependencies system-wide
COPY requirements.txt servers.json ./
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the app
CMD ["python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

This version is expected to provide a lean, efficient, and correctly configured environment for the `mcp_proxy.py` application, resolving all previously encountered issues.

## 8. Recent Issues and Final Resolution (Latest Session)

### Issue: Context7 MCP Server Failure with Node.js Shared Library Dependencies

**Date**: 2025-07-03

**Problem**: The `Dockerfile.optimized` was failing when attempting to use the `context7` MCP server. The container would build successfully but fail at runtime with extensive Node.js shared library dependency errors.

**Error Symptoms**:
```
Error loading shared library libada.so.2: No such file or directory (needed by /usr/bin/node)
Error loading shared library libsimdjson.so.25: No such file or directory (needed by /usr/bin/node)
Error loading shared library libstdc++.so.6: No such file or directory (needed by /usr/bin/node)
Error relocating /usr/bin/node: nghttp2_submit_trailer: symbol not found
Error relocating /usr/bin/node: _ZN8simdjson25get_active_implementationEv: symbol not found
... (many more similar errors)
```

**Root Cause**: The multi-stage build approach was copying Node.js binaries between Docker stages without their required shared libraries. Node.js has complex dependencies on system libraries that are not automatically copied when copying just the binary files.

**Investigation Process**:
1. **Analyzed the server configuration**: `servers.json` showed the need for both `npx` (Node.js) and `uvx` (Python/uv) commands
2. **Identified the hybrid approach**: `uvx` copying works fine (Python tool), but `npx` copying is problematic (Node.js with shared libraries)
3. **Evaluated optimization trade-offs**: Compared image size vs. build performance vs. reliability

**Final Resolution**: 
- **Abandoned multi-stage approach for Node.js**: Install Node.js directly in the final stage to ensure all dependencies are properly resolved
- **Maintained optimization for Python tools**: Keep copying `uv` and `uvx` from builder stage
- **Applied build optimization techniques**: Added build cache mounts and layer caching

### Current Final `Dockerfile.dev` (Version 5)

```dockerfile
# Use the official Astral uv image with Python 3.12 on Alpine
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Install nodejs and npm for the npx command (runtime dependency for context7)
RUN apk add --no-cache nodejs npm

# Set the working directory
WORKDIR /app

# Enable bytecode compilation for better performance
ENV UV_COMPILE_BYTECODE=1

# Copy only requirements first for better layer caching
COPY requirements.txt servers.json ./

# Install Python dependencies using cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache-dir -r requirements.txt

# Copy the rest of the application code (this layer changes frequently)
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the app
CMD ["python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

### Key Lessons Learned

1. **Docker Multi-stage Complexity**: Multi-stage builds are not always better - they add complexity and can introduce dependency issues
2. **Shared Library Dependencies**: Copying binaries between stages can break shared library dependencies, especially for complex runtimes like Node.js
3. **Optimization Trade-offs**: Build-time optimizations (cache mounts, layer caching) don't always reduce final image size but improve development experience
4. **Context-Specific Solutions**: The "best" Docker approach depends on the specific use case (development vs. production)

### Current Status

- **Working Solution**: Both `Dockerfile` and `Dockerfile.dev` now work correctly
- **Use Case Differentiation**: 
  - `Dockerfile`: Optimal for production (smaller images, simpler)
  - `Dockerfile.dev`: Optimal for development (faster builds, better caching)
- **Performance Considerations**: `Dockerfile.dev` produces larger images (~20-30% due to bytecode compilation) but provides faster development iteration
- **File Management**: `Dockerfile2` was removed as it was not relevant to this project's architecture

### MCP Server Configuration

The project successfully proxies multiple MCP servers:
- **context7**: Uses `npx` to run `@upstash/context7-mcp` (Node.js-based)
- **fetch**: Uses `uvx` to run `mcp-server-fetch` (Python-based)  
- **time**: Uses `uvx` to run `mcp-server-time` with timezone configuration (Python-based)

All servers are now working correctly with the resolved Node.js dependency issues.
