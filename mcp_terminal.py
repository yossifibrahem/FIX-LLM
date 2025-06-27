#!/usr/bin/env python3
"""
MCP Server with terminal commands tool
"""
import platform
import asyncio
from datetime import datetime
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Tool imports
from Python_tool.terminal import execute_terminal_command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Create server instance
server = Server("python-terminal-interpreter")




@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="terminal_command",
            description=f"Execute terminal/command line commands and return the results. the current os is {platform.system()}. Use for system commands, file operations, or shell scripts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The terminal command to execute (e.g., 'ls -la', 'dir', 'echo hello', 'python --version')"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to execute the command in"
                    }
                },
                "required": ["command"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle tool calls.
    """
    try:
        if name == "terminal_command":
            command = arguments.get("command", "")
            if not command:
                raise ValueError("Command parameter is required")
            
            timeout = arguments.get("timeout", 10)
            working_directory = arguments.get("working_directory")
            
            # Execute command in thread to avoid blocking
            result = await asyncio.to_thread(
                execute_terminal_command, 
                command, 
                timeout, 
                working_directory
            )
            
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [
            types.TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )
        ]

async def main():
    """
    Main function to run the MCP server
    """
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="python-terminal-interpreter",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())