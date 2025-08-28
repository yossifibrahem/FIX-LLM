#!/usr/bin/env python3
"""
MCP Server with web browsing and YouTube tools
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
from web_tool.web_browsing import (
    text_search as web_search,
    webpage_scraper as web_scrape,
    images_search as image_search,
)
from youtube_tool.youtube import (
    search_youtube as youtube_search,
    get_video_info as youtube_scrape,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Create server instance
server = Server("Web")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="web_search",
            description=f"Perform a web search for realtime information, the current date is {datetime.now().strftime('%Y-%m-%d')}.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for relevant web results"
                    },
                    "number_of_results": {
                        "type": "integer",
                        "description": "number of urls to return.",
                        "default": 10
                    },
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="web_scrape",
            description="Scrape a website for its content",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the website to scrape"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="image_search",
            description="Search the web for images.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for images"
                    },
                    "number_of_images": {
                        "type": "integer",
                        "description": "Maximum images to get",
                        "default": 1
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="youtube_search",
            description="Search youtube videos and retrieve the urls.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for videos"
                    },
                    "number_of_videos": {
                        "type": "integer",
                        "description": "Maximum videos to get",
                        "default": 1
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="youtube_scrape",
            description="Get information about a youtube video (title, description and transcription)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the youtube video"
                    }
                },
                "required": ["url"]
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
        if name == "web_search":
            query = arguments.get("query", "")
            num_websites = arguments.get("number_of_results", 10)
            
            if not query:
                raise ValueError("Query parameter is required")

            result = await asyncio.to_thread(web_search, query, num_websites)
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        
        elif name == "web_scrape":
            url = arguments.get("url", "")
            if not url:
                raise ValueError("URL parameter is required")
            
            result = await asyncio.to_thread(web_scrape, url)
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        
        elif name == "image_search":
            query = arguments.get("query", "")
            num_images = arguments.get("number_of_images", 1)
            
            if not query:
                raise ValueError("Query parameter is required")
            
            result = await asyncio.to_thread(image_search, query, num_images)
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        
        elif name == "youtube_search":
            query = arguments.get("query", "")
            num_videos = arguments.get("number_of_videos", 1)
            
            if not query:
                raise ValueError("Query parameter is required")
            
            result = await asyncio.to_thread(youtube_search, query, num_videos)
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        
        elif name == "youtube_scrape":
            url = arguments.get("url", "")
            if not url:
                raise ValueError("URL parameter is required")
            
            result = await asyncio.to_thread(youtube_scrape, url)
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
                server_name="Web",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())