#!/usr/bin/env python3
"""
MCP Server with Python execution tool
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
from Python_tool.PythonExecutor_secure import execute_python_code, execute_python_expression

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
            name="execute_python_code",
            description="This function executes Python code dynamically and returns structured results including output, errors, and success status." \
            " It captures print statements and provides detailed error tracebacks when code execution fails.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Complete Python script to execute. can be multiple lines of code."
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 10)."
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="execute_python_expression",
            description="Evaluates a single Python expression and returns the computed value.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python expression to evaluate. can only be a single line of code."
                    }
                },
                "required": ["expression"]
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
        if name == "execute_python_code":
            code = arguments.get("code", "")
            if not code:
                raise ValueError("Code parameter is required")
            
            result = await asyncio.to_thread(execute_python_code, code, arguments.get("timeout", 10))
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        elif name == "execute_python_expression":
            expression = arguments.get("expression", "")
            if not expression:
                raise ValueError("Expression parameter is required")
            
            result = await asyncio.to_thread(execute_python_expression, expression)
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