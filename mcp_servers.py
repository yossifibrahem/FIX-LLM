#!/usr/bin/env python3
"""
MCP Server with Python execution, web browsing, Wikipedia, and YouTube tools
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Tool imports
from Python_tool.PythonExecutor_secure import execute_python_code as python
from web_tool.web_browsing import (
    text_search_bs4 as web,
    webpage_scraper_bs4 as URL,
    images_search as image,
)
from wiki_tool.search_wiki import fetch_wikipedia_content as wiki
from youtube_tool.youtube import (
    search_youtube as youtube,
    get_video_info as watch
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Create server instance
server = Server("multi-tool-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="python",
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
        ),
        types.Tool(
            name="web",
            description="Perform a quick simple web search for relevant realtime information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for websites"
                    },
                    "Key_words": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "list of Key word used for finding relevant citations"
                    },
                    "number_of_websites": {
                        "type": "integer",
                        "description": "Maximum websites to visit",
                        "default": 4
                    },
                    "number_of_citations": {
                        "type": "integer",
                        "description": "Maximum citations to scrape",
                        "default": 4
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="wiki",
            description="Search Wikipedia for the most relevant article introduction",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Wikipedia article"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="URL",
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
            name="image",
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
            name="youtube",
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
            name="watch",
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
        if name == "python":
            code = arguments.get("code", "")
            if not code:
                raise ValueError("Code parameter is required")
            
            result = await asyncio.to_thread(python, code)
            return [
                types.TextContent(
                    type="text",
                    text=f"Python execution result:\n{result}"
                )
            ]
        
        elif name == "web":
            query = arguments.get("query", "")
            keywords = arguments.get("Key_words", [query])
            num_websites = arguments.get("number_of_websites", 4)
            num_citations = arguments.get("number_of_citations", 4)
            
            if not query:
                raise ValueError("Query parameter is required")

            
            result = await asyncio.to_thread(
                web, query, keywords, num_websites, num_citations
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Web search results:\n{result}"
                )
            ]
        
        elif name == "wiki":
            query = arguments.get("query", "")
            if not query:
                raise ValueError("Query parameter is required")
            
            result = await asyncio.to_thread(wiki, query)
            return [
                types.TextContent(
                    type="text",
                    text=f"Wikipedia content:\n{result}"
                )
            ]
        
        elif name == "URL":
            url = arguments.get("url", "")
            if not url:
                raise ValueError("URL parameter is required")
            
            result = await asyncio.to_thread(URL, url)
            return [
                types.TextContent(
                    type="text",
                    text=f"Website content:\n{result}"
                )
            ]
        
        elif name == "image":
            query = arguments.get("query", "")
            num_images = arguments.get("number_of_images", 1)
            
            if not query:
                raise ValueError("Query parameter is required")
            
            result = await asyncio.to_thread(image, query, num_images)
            return [
                types.TextContent(
                    type="text",
                    text=f"Image search results:\n{result}"
                )
            ]
        
        elif name == "youtube":
            query = arguments.get("query", "")
            num_videos = arguments.get("number_of_videos", 1)
            
            if not query:
                raise ValueError("Query parameter is required")
            
            result = await asyncio.to_thread(youtube, query, num_videos)
            return [
                types.TextContent(
                    type="text",
                    text=f"YouTube search results:\n{result}"
                )
            ]
        
        elif name == "watch":
            url = arguments.get("url", "")
            if not url:
                raise ValueError("URL parameter is required")
            
            result = await asyncio.to_thread(watch, url)
            return [
                types.TextContent(
                    type="text",
                    text=f"YouTube video info:\n{result}"
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
                server_name="multi-tool-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())