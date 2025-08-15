#!/usr/bin/env python3
"""
MCP Agent Script - Cross-Platform Version
This script demonstrates using MCP tools with Strands Agent outside of Jupyter
Compatible with Windows, macOS, and Linux using multiple fallback methods
"""

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient
import os
import sys
import subprocess
from pathlib import Path


def get_venv_path():
    """Detect virtual environment path from various sources."""
    # Check VIRTUAL_ENV environment variable first
    if venv_env := os.environ.get('VIRTUAL_ENV'):
        venv_path = Path(venv_env)
    else:
        # Fall back to sys.prefix
        venv_path = Path(sys.prefix)
    
    # Determine scripts directory based on platform
    if sys.platform == "win32":
        scripts_path = venv_path / "Scripts"
    else:
        scripts_path = venv_path / "bin"
    
    return scripts_path


def get_mcp_executable():
    """Get the platform-specific MCP server executable path."""
    venv_scripts_path = get_venv_path()
    
    # Determine executable name based on platform
    if sys.platform == "win32":
        executable_name = "awslabs.aws-documentation-mcp-server.exe"
    else:
        executable_name = "awslabs.aws-documentation-mcp-server"
    
    return venv_scripts_path / executable_name


def create_mcp_client():
    """Create MCP client with multiple fallback methods for maximum compatibility."""
    
    # Method 1: Try installed executable (platform-specific)
    print("Method 1: Trying installed executable...")
    try:
        mcp_exe = get_mcp_executable()
        if mcp_exe.exists():
            client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command=str(mcp_exe),
                        args=[]
                    )
                )
            )
            # Test the client
            with client:
                client.list_tools_sync()
            print(f"✓ Successfully connected using installed executable: {mcp_exe}")
            return client, "executable"
        else:
            print(f"✗ Executable not found at: {mcp_exe}")
    except Exception as e:
        print(f"✗ Executable method failed: {e}")
    
    # Method 2: Try pip install and then use executable
    print("Method 2: Trying to install MCP server...")
    try:
        print("Installing awslabs.aws-documentation-mcp-server...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "awslabs.aws-documentation-mcp-server"
        ], check=True, capture_output=True)
        
        mcp_exe = get_mcp_executable()
        if mcp_exe.exists():
            client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command=str(mcp_exe),
                        args=[]
                    )
                )
            )
            # Test the client
            with client:
                client.list_tools_sync()
            print(f"✓ Successfully installed and connected to: {mcp_exe}")
            return client, "installed"
        else:
            print(f"✗ Installation completed but executable not found at: {mcp_exe}")
    except Exception as e:
        print(f"✗ Installation method failed: {e}")
    
    # If all methods fail
    raise RuntimeError(
        "All connection methods failed. Please try:\n"
        "1. Install MCP server: pip install awslabs.aws-documentation-mcp-server\n"
        "2. Check your Python environment and network connectivity"
    )

def main():
    print("Creating MCP client for AWS Documentation Server...")
    print("Attempting multiple connection methods for maximum compatibility...\n")
    
    try:
        # Try to create MCP client with fallback methods
        mcp_client, method = create_mcp_client()
        print(f"\n✓ Successfully connected using method: {method}")
    except RuntimeError as e:
        print(f"\n✗ Failed to connect to any MCP server:")
        print(str(e))
        return
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return

    print("\nConnecting to MCP server and listing tools...")
    
    # Create an agent with MCP tools
    with mcp_client:
        # Get the tools from the MCP server
        tools = mcp_client.list_tools_sync()
        # Tools are MCPAgentTool objects, not dicts
        tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
        print(f"Found {len(tools)} tools: {tool_names}")
        
        # Create an agent with these tools
        agent = Agent(
            model="apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
            tools=tools
        )
        
        print("\nAsking agent about Amazon Bedrock pricing...")
        response = agent("What is Amazon Bedrock pricing model. Be concise.")
        print(f"\nAgent response:\n{response}")
        
        # You can ask more questions
        print("\n" + "="*50)
        print("You can now interact with the agent. Type 'quit' to exit.")
        print("="*50 + "\n")
        
        try:
            while True:
                user_input = input("Your question: ")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                response = agent(user_input)
                print(f"\nAgent response:\n{response}\n")
        except EOFError:
            print("\nNo interactive input available. Exiting...")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
    
    print("Disconnected from MCP server.")


if __name__ == "__main__":
    main()