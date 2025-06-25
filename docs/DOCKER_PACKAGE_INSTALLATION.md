# Docker Package Installation

This document explains how the mcp-proxy Docker image automatically installs MCP server packages based on the `servers.json` configuration.

## Overview

The Docker build process now automatically parses `servers.json` and pre-installs all required MCP packages during the build stage. This means:

- **No runtime downloads**: Packages are available immediately when the container starts
- **Flexible configuration**: Add new packages to `servers.json` without changing any code
- **Faster startup**: No waiting for package downloads when containers start
- **Offline capability**: Containers work without internet access for package installation

## How It Works

### Build Process

1. **Parse Configuration**: The `install_mcp_packages.py` script reads `servers.json`
2. **Extract Packages**: Identifies uvx (Python) and npx (Node.js) packages from enabled servers
3. **Install Packages**: Pre-installs packages using `uv tool install` and `npm install -g`
4. **Copy to Final Image**: Installed packages are copied to the final container image

### Supported Package Types

- **uvx packages**: Python packages installed via `uv tool install`
  - Example: `mcp-server-fetch`, `mcp-server-time`
- **npx packages**: Node.js packages installed via `npm install -g`
  - Example: `@playwright/mcp@latest`, `@modelcontextprotocol/server-github`

## Configuration Format

### servers.json Structure

```json
{
  "mcpServers": {
    "server-name": {
      "enabled": true,
      "command": "uvx|npx",
      "args": ["package-name", "additional-args"],
      "transportType": "stdio"
    }
  }
}
```

### Example Configuration

```json
{
  "mcpServers": {
    "fetch": {
      "enabled": true,
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "transportType": "stdio"
    },
    "playwright": {
      "enabled": true,
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "transportType": "stdio"
    },
    "disabled-server": {
      "enabled": false,
      "command": "uvx",
      "args": ["some-package"]
    }
  }
}
```

## Adding New MCP Servers

### Step-by-Step Process

1. **Update servers.json**: Add your new server configuration
2. **Rebuild Docker image**: The build process will automatically install the new package
3. **Deploy**: Use the new image with the pre-installed packages

### Example: Adding a New Server

```json
{
  "mcpServers": {
    "existing-server": {
      "enabled": true,
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "new-server": {
      "enabled": true,
      "command": "npx",
      "args": ["@new/mcp-server-package"]
    }
  }
}
```

After updating `servers.json`, simply rebuild:

```bash
docker build -t mcp-proxy .
```

The new package will be automatically installed during the build.

## Server Control

### Enabling/Disabling Servers

Servers can be controlled using either:

- `"enabled": true/false` - Standard format
- `"disabled": true/false` - Alternative format

Disabled servers are skipped during package installation.

### Runtime vs Build Time

- **Build time**: Packages are installed based on `servers.json`
- **Runtime**: Servers are started/stopped based on the same configuration

## Troubleshooting

### Build Issues

If package installation fails during Docker build:

```bash
# Build with verbose output
docker build --progress=plain --no-cache .
```

Look for output from `install_mcp_packages.py` to see which packages failed.

### Verifying Installed Packages

Check what packages are installed in a container:

```bash
# Start container with shell
docker run -it mcp-proxy sh

# Check uvx packages
uvx list

# Check npm packages  
npm list -g --depth=0
```

### Common Issues

1. **Package not found**: Ensure the package name is correct in `servers.json`
2. **Permission errors**: The build process handles permissions automatically
3. **Network issues**: Package installation happens during build, ensure build environment has internet access

## Testing

### Test Package Installation Script

Use the provided test script to verify the installation logic:

```bash
python3 test_package_installation.py
```

### Manual Testing

Test with a custom configuration:

```bash
python3 install_mcp_packages.py your-test-config.json
```

## Performance Benefits

### Before (Runtime Installation)
- Container starts
- Downloads packages on first use
- Slower startup time
- Requires internet access

### After (Build-time Installation)
- Packages pre-installed in image
- Immediate availability
- Faster startup
- Works offline

## Security Considerations

- Packages are installed during build in a controlled environment
- Final container runs as non-root user
- Pre-installed packages reduce attack surface (no runtime downloads)
- Package versions are locked at build time

## Future Enhancements

Potential improvements to consider:

- **Version pinning**: Support for specific package versions in `servers.json`
- **Dependency optimization**: Smart dependency resolution to minimize image size
- **Build caching**: Better caching strategies for package installations
- **Multi-arch support**: Ensure packages work across different architectures