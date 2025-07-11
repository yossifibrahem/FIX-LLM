#!/usr/bin/env python3
"""
MCP Server with web browsing, Wikipedia, and YouTube tools
"""

import asyncio
from datetime import datetime
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Tool imports
from wiki_tool.search_wiki import fetch_wikipedia_content as wiki_search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Create server instance
server = Server("wiki_server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="wiki_search",
            description="Search Wikipedia for the most relevant article. useful for getting information about a topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Wikipedia article"
                    },
                    "full_article": {
                        "type": "boolean",
                        "description": "If True, returns the full article content. If False, returns only the introduction.",
                        "default": False
                    }
                },
                "required": ["query"]
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
        if name == "wiki_search":
            query = arguments.get("query", "")
            full_article = arguments.get("full_article", False)
            if not query:
                raise ValueError("Query parameter is required")
            
            result = await asyncio.to_thread(wiki_search, query, full_article)
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
                server_name="wiki_server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())