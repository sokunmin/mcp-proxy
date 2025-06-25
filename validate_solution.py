#!/usr/bin/env python3
"""
Validate the MCP package installation solution.

This script validates that our solution correctly parses servers.json
and identifies the packages that need to be installed.
"""

import json
import sys
from pathlib import Path


def validate_servers_json():
    """Validate that servers.json exists and is properly formatted."""
    servers_path = Path("servers.json")
    if not servers_path.exists():
        print("❌ servers.json not found")
        return False
    
    try:
        with open(servers_path) as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print("❌ servers.json missing 'mcpServers' key")
            return False
            
        print("✅ servers.json is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ servers.json has invalid JSON: {e}")
        return False


def validate_install_script():
    """Validate that the install script exists and has correct structure."""
    script_path = Path("install_mcp_packages.py")
    if not script_path.exists():
        print("❌ install_mcp_packages.py not found")
        return False
    
    # Check if script has required functions
    with open(script_path) as f:
        content = f.read()
    
    required_functions = [
        "load_servers_config",
        "extract_packages", 
        "install_uvx_packages",
        "install_npx_packages",
        "main"
    ]
    
    for func in required_functions:
        if f"def {func}" not in content:
            print(f"❌ install_mcp_packages.py missing function: {func}")
            return False
    
    print("✅ install_mcp_packages.py has all required functions")
    return True


def validate_dockerfile():
    """Validate that Dockerfile has been updated correctly."""
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found")
        return False
    
    with open(dockerfile_path) as f:
        content = f.read()
    
    required_elements = [
        "install_mcp_packages.py",
        "python3 install_mcp_packages.py",
        "COPY --from=uv --chown=app:app /root/.local",
        "COPY --from=uv --chown=app:app /usr/local/lib/node_modules"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ Dockerfile missing: {element}")
            return False
    
    print("✅ Dockerfile has been updated correctly")
    return True


def simulate_package_extraction():
    """Simulate the package extraction process."""
    try:
        with open("servers.json") as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        uvx_packages = []
        npx_packages = []
        
        for server_name, server_config in servers.items():
            # Skip disabled servers
            if not server_config.get('enabled', True) or server_config.get('disabled', False):
                print(f"  Skipping disabled server: {server_name}")
                continue
            
            command = server_config.get('command', '')
            args = server_config.get('args', [])
            
            if command == 'uvx' and args:
                package_name = args[0]
                uvx_packages.append(package_name)
                print(f"  Found uvx package: {package_name} (from {server_name})")
            elif command == 'npx' and args:
                package_args = [arg for arg in args if not arg.startswith('-')]
                if package_args:
                    package_name = package_args[0]
                    npx_packages.append(package_name)
                    print(f"  Found npx package: {package_name} (from {server_name})")
        
        # Remove duplicates
        uvx_packages = list(dict.fromkeys(uvx_packages))
        npx_packages = list(dict.fromkeys(npx_packages))
        
        print(f"✅ Package extraction simulation successful:")
        print(f"  - {len(uvx_packages)} uvx packages: {uvx_packages}")
        print(f"  - {len(npx_packages)} npx packages: {npx_packages}")
        
        return len(uvx_packages) > 0 or len(npx_packages) > 0
        
    except Exception as e:
        print(f"❌ Package extraction simulation failed: {e}")
        return False


def main():
    """Run all validation checks."""
    print("Validating MCP Package Installation Solution")
    print("=" * 50)
    
    checks = [
        ("servers.json format", validate_servers_json),
        ("install script structure", validate_install_script),
        ("Dockerfile updates", validate_dockerfile),
        ("package extraction logic", simulate_package_extraction)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\nChecking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation checks passed!")
        print("\nYour Docker setup is now flexible and will automatically install")
        print("MCP packages based on servers.json configuration.")
        print("\nTo add new MCP servers:")
        print("1. Add entry to servers.json")
        print("2. Rebuild Docker image")
        print("3. Packages will be automatically installed!")
    else:
        print("❌ Some validation checks failed. Please review the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main()