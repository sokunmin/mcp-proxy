#!/usr/bin/env python3
"""
Test script to verify MCP package installation works correctly.

This script can be used to test the install_mcp_packages.py script
with different server configurations.
"""

import json
import tempfile
from pathlib import Path
import subprocess
import sys


def create_test_config(servers_config: dict) -> str:
    """Create a temporary test configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"mcpServers": servers_config}, f, indent=2)
        return f.name


def test_basic_config():
    """Test with a basic configuration similar to servers.json."""
    print("Testing basic configuration...")
    
    config = {
        "fetch": {
            "enabled": True,
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        },
        "time": {
            "enabled": True,
            "command": "uvx", 
            "args": ["mcp-server-time"]
        },
        "playwright": {
            "enabled": True,
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        }
    }
    
    config_file = create_test_config(config)
    try:
        # Run the installation script in dry-run mode (just parsing)
        result = subprocess.run([
            sys.executable, 'install_mcp_packages.py', config_file
        ], capture_output=True, text=True)
        
        print(f"Exit code: {result.returncode}")
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
            
    finally:
        Path(config_file).unlink()


def test_disabled_servers():
    """Test with disabled servers."""
    print("\nTesting disabled servers...")
    
    config = {
        "enabled-server": {
            "enabled": True,
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        },
        "disabled-server": {
            "enabled": False,
            "command": "uvx",
            "args": ["some-package"]
        },
        "disabled-server-2": {
            "disabled": True,
            "command": "npx",
            "args": ["some-npm-package"]
        }
    }
    
    config_file = create_test_config(config)
    try:
        result = subprocess.run([
            sys.executable, 'install_mcp_packages.py', config_file
        ], capture_output=True, text=True)
        
        print(f"Exit code: {result.returncode}")
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
            
    finally:
        Path(config_file).unlink()


def test_invalid_config():
    """Test with invalid configuration."""
    print("\nTesting invalid configuration...")
    
    config = {
        "no-command": {
            "enabled": True,
            "args": ["some-package"]
        },
        "empty-args": {
            "enabled": True,
            "command": "uvx",
            "args": []
        },
        "unknown-command": {
            "enabled": True,
            "command": "unknown",
            "args": ["some-package"]
        }
    }
    
    config_file = create_test_config(config)
    try:
        result = subprocess.run([
            sys.executable, 'install_mcp_packages.py', config_file
        ], capture_output=True, text=True)
        
        print(f"Exit code: {result.returncode}")
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
            
    finally:
        Path(config_file).unlink()


if __name__ == '__main__':
    print("Testing MCP package installation script...")
    print("=" * 50)
    
    test_basic_config()
    test_disabled_servers()
    test_invalid_config()
    
    print("\n" + "=" * 50)
    print("Test completed!")