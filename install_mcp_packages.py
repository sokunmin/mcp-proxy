#!/usr/bin/env python3
"""
Install MCP packages from servers.json configuration.

This script parses the servers.json file and pre-installs the required packages
for uvx (Python) and npx (Node.js) commands, making them available in the Docker image.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_servers_config(config_path: str) -> Dict[str, Any]:
    """Load and parse the servers configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('mcpServers', {})
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read {config_path}: {e}")
        sys.exit(1)


def extract_packages(servers_config: Dict[str, Any]) -> tuple[List[str], List[str]]:
    """Extract uvx and npx packages from the servers configuration."""
    uvx_packages = []
    npx_packages = []
    
    for server_name, server_config in servers_config.items():
        # Skip if server is disabled
        if not server_config.get('enabled', True) or server_config.get('disabled', False):
            print(f"Skipping disabled server: {server_name}")
            continue
            
        command = server_config.get('command', '')
        args = server_config.get('args', [])
        
        if not command:
            print(f"Warning: No command specified for server {server_name}")
            continue
            
        # Handle uvx commands (Python packages)
        if command == 'uvx':
            if args:
                package_name = args[0]
                uvx_packages.append(package_name)
                print(f"Found uvx package: {package_name} (from {server_name})")
            else:
                print(f"Warning: uvx command without package name for server {server_name}")
                
        # Handle npx commands (Node.js packages)
        elif command == 'npx':
            if args:
                # Skip npx flags like -y and get the actual package name
                package_args = [arg for arg in args if not arg.startswith('-')]
                if package_args:
                    package_name = package_args[0]
                    npx_packages.append(package_name)
                    print(f"Found npx package: {package_name} (from {server_name})")
                else:
                    print(f"Warning: npx command without package name for server {server_name}")
            else:
                print(f"Warning: npx command without arguments for server {server_name}")
        else:
            print(f"Info: Skipping non-package command '{command}' for server {server_name}")
    
    return uvx_packages, npx_packages


def install_uvx_packages(packages: List[str]) -> None:
    """Install Python packages using uv tool install."""
    if not packages:
        print("No uvx packages to install")
        return
        
    print(f"Installing {len(packages)} uvx packages...")
    for package in packages:
        try:
            print(f"Installing uvx package: {package}")
            subprocess.run(['uv', 'tool', 'install', package], check=True, capture_output=True, text=True)
            print(f"✓ Successfully installed uvx package: {package}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install uvx package {package}: {e}")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            # Continue with other packages instead of failing completely
        except Exception as e:
            print(f"✗ Unexpected error installing uvx package {package}: {e}")


def install_npx_packages(packages: List[str]) -> None:
    """Install Node.js packages using npm install -g."""
    if not packages:
        print("No npx packages to install")
        return
        
    print(f"Installing {len(packages)} npx packages...")
    for package in packages:
        try:
            print(f"Installing npx package: {package}")
            subprocess.run(['npm', 'install', '-g', package], check=True, capture_output=True, text=True)
            print(f"✓ Successfully installed npx package: {package}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install npx package {package}: {e}")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            # Continue with other packages instead of failing completely
        except Exception as e:
            print(f"✗ Unexpected error installing npx package {package}: {e}")


def main():
    """Main function to install MCP packages."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'servers.json'
    
    print(f"Installing MCP packages from {config_path}")
    print("=" * 50)
    
    # Load configuration
    servers_config = load_servers_config(config_path)
    
    if not servers_config:
        print("No servers found in configuration")
        return
    
    # Extract packages
    uvx_packages, npx_packages = extract_packages(servers_config)
    
    # Remove duplicates while preserving order
    uvx_packages = list(dict.fromkeys(uvx_packages))
    npx_packages = list(dict.fromkeys(npx_packages))
    
    print(f"\nFound {len(uvx_packages)} unique uvx packages: {uvx_packages}")
    print(f"Found {len(npx_packages)} unique npx packages: {npx_packages}")
    print()
    
    # Install packages
    install_uvx_packages(uvx_packages)
    print()
    install_npx_packages(npx_packages)
    
    print("\n" + "=" * 50)
    print("MCP package installation completed!")


if __name__ == '__main__':
    main()