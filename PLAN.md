# Deployment Plan for mcp-proxy on Smithery

## 1. Context

*   **Goal:** To deploy the `mcp-proxy` application on Smithery, enabling it to run and expose multiple Model Context Protocol (MCP) servers as defined in the `servers.json` configuration file.
*   **Current `Dockerfile`:** Your `Dockerfile` is designed to create a "fat" Docker image. This image includes:
    *   The `mcp-proxy` application and its Python dependencies.
    *   Node.js and npm.
    *   The `uv` tool.
    *   Pre-installed `uvx` (Python) and `npx` (Node.js) packages, based on the `servers.json` file, using the `install_mcp_packages.py` script.
    *   The `servers.json` file itself, copied into the image at `/app/servers.json`.
*   **`mcp-proxy` Capability:** The `mcp-proxy` application, as confirmed by its `README.md`, supports exposing multiple named MCP servers via a single HTTP port when started with the `--named-server-config <FILE_PATH>` argument.
*   **Smithery Deployment Model:** Smithery supports deploying custom Docker containers (`runtime: container`). For such deployments, Smithery expects the container to expose an HTTP server that listens on a port specified by the `PORT` environment variable.

## 2. Problem Statement

The existing `smithery.yaml` file is configured for a `stdio` type `startCommand` and expects a single `commandOrUrl` argument. This configuration is incompatible with your `Dockerfile`'s design, which aims to run `mcp-proxy` as an HTTP server managing multiple internal MCP servers from `servers.json`.

## 3. Plan

The plan is to leverage your existing "fat" Docker image and modify the `smithery.yaml` to correctly instruct Smithery on how to run it.

### Step 1: Keep the `Dockerfile` As Is

*   **Action:** No changes are required for your current `Dockerfile`.
*   **Reasoning:** Your `Dockerfile` already correctly builds the necessary "fat" image. It includes all the components (`mcp-proxy`, `uv`, `npm`, pre-installed `uvx`/`npx` packages, and `servers.json`) required for `mcp-proxy` to manage multiple internal servers.

### Step 2: Modify `smithery.yaml`

*   **Action:** Update the `smithery.yaml` file to configure Smithery for a custom container deployment that exposes an HTTP server.
*   **Details of Modification:**

    1.  **Set `runtime` to `container`:** This tells Smithery that you are providing a Docker container for deployment.
    2.  **Add `build` section:** Specify the `dockerfile` path and `dockerBuildPath` to instruct Smithery on how to build your Docker image.
    3.  **Set `startCommand.type` to `http`:** This is crucial. It informs Smithery that your container will expose an HTTP server, which is the mode `mcp-proxy` operates in when managing named servers.
    4.  **Update `commandFunction`:** This function will define the exact command Smithery uses to start your `mcp-proxy` container. It will be configured to:
        *   Launch `mcp-proxy`.
        *   Instruct `mcp-proxy` to listen on the port provided by Smithery via the `PORT` environment variable (`--port=` + `process.env.PORT`).
        *   Set the host to `0.0.0.0` to ensure accessibility within the container (`--host=0.0.0.0`).
        *   Crucially, tell `mcp-proxy` to load its server configurations from the `servers.json` file that is already present in your Docker image (`--named-server-config /app/servers.json`).
        *   The `commandOrUrl` parameter from Smithery's `config` will be effectively ignored by `mcp-proxy`'s startup command, as we are explicitly using `servers.json`.

*   **Proposed `smithery.yaml` content:**

    ```yaml
    # smithery.yaml
    runtime: container
    build:
      dockerfile: Dockerfile # Assuming your Dockerfile is named Dockerfile in the root
      dockerBuildPath: .     # Build context is the current directory
    startCommand:
      type: http # This tells Smithery to expect an HTTP server
      configSchema:
        # JSON Schema defining the configuration options for the MCP.
        type: object
        required:
          - commandOrUrl # This is still required by Smithery's schema, but we'll ignore it in commandFunction
        properties:
          commandOrUrl:
            type: string
            description: The MCP server SSE endpoint URL or the command to start the local
              stdio server.
          apiAccessToken:
            type: string
            description: Optional access token for Authorization header.
          ssePort:
            type: number
            description: Optional port for SSE server. Defaults to a random port.
          sseHost:
            type: string
            description: Optional host for SSE server. Defaults to 127.0.0.1.
          env:
            type: object
            description: Additional environment variables for the stdio server.
      commandFunction:
        # A function that produces the CLI command to start the MCP on stdio.
        |-
        (config) => {
          let command = ['mcp-proxy', '--port=' + process.env.PORT, '--host=0.0.0.0', '--named-server-config', '/app/servers.json'];
          if (config.apiAccessToken) {
            command.push('--headers', 'Authorization', 'Bearer ' + config.apiAccessToken);
          }
          // Add other config parameters if needed, but for named-server-config, they might be redundant
          return { command: command[0], args: command.slice(1), env: config.env };
        }
    ```
