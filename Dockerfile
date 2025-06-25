# Build stage with explicit platform specification
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS uv

# Install the project into /app
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Install Node.js and npm for npx package installation during build
RUN apk add --no-cache nodejs npm

# Copy the MCP package installation script and servers.json
COPY install_mcp_packages.py servers.json ./

# Pre-install MCP packages based on servers.json configuration
# This makes uvx and npx packages available without runtime downloads
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.npm \
    python3 install_mcp_packages.py servers.json

# Final stage with explicit platform specification
FROM python:3.12-alpine

# Install Node.js and npm for npx support, plus wget for health checks
RUN apk add --no-cache nodejs npm wget

# Install uv for uvx support
RUN python3 -m ensurepip && pip install --no-cache-dir uv

# Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

# Copy the virtual environment and pre-installed packages from build stage
COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Copy uv tools (pre-installed uvx packages) from build stage
COPY --from=uv --chown=app:app /root/.local /home/app/.local

# Copy global npm packages from build stage
COPY --from=uv --chown=app:app /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=uv --chown=app:app /usr/local/bin /usr/local/bin

# Copy servers.json configuration
COPY --chown=app:app servers.json /app/servers.json

# Place executables in the environment at the front of the path
# Include uv tools path for pre-installed uvx packages
ENV PATH="/app/.venv/bin:/home/app/.local/bin:$PATH" \
    UV_PYTHON_PREFERENCE=only-system

# Switch to app user
USER app

# Set working directory
WORKDIR /app

ENTRYPOINT ["mcp-proxy"]
