#!/usr/bin/env python3
"""
MCP Server with Python execution, web browsing, Wikipedia, and YouTube tools
"""

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
from Python_tool.PythonExecutor_secure import execute_python_code as python_interpreter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Create server instance
server = Server("python-interpreter")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="python_interpreter",
            description="Execute Python code and return the execution results. Use for math problems or task automation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Complete Python script to execute. Must return a value."
                    }
                },
                "required": ["code"]
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
        if name == "python_interpreter":
            code = arguments.get("code", "")
            if not code:
                raise ValueError("Code parameter is required")
            
            result = await asyncio.to_thread(python_interpreter, code)
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
                server_name="python-interpreter",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())