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
from web_tool.web_browsing import (
    text_search_bs4 as web_search,
    webpage_scraper_bs4 as scrape_webpage,
    images_search as image_search,
)
from wiki_tool.search_wiki import fetch_wikipedia_content as wiki_search
from youtube_tool.youtube import (
    search_youtube as youtube_search,
    get_video_info as youtube_info,
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
            description=f"Perform a quick simple web search for relevant realtime information. the current date is {datetime.now().strftime('%Y-%m-%d')}.",
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
                    "full_context": {
                        "type": "boolean",
                        "description": "whether scraped web content full context for better understanding or only relevant citations",
                        "default": False
                    },
                    "number_of_chunks": {
                        "type": "integer",
                        "description": "Maximum citations to scrape",
                        "default": 4
                    }
                },
                "required": ["query", "Key_words"]
            }
        ),
        types.Tool(
            name="wiki_search",
            description="Search Wikipedia for the most relevant article introduction",
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
        ),
        types.Tool(
            name="scrape_webpage",
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
            name="youtube_info",
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
            keywords = arguments.get("Key_words", [query])
            num_websites = arguments.get("number_of_websites", 4)
            full_context = arguments.get("full_context", False)
            num_citations = arguments.get("number_of_chunks", 4)
            
            if not query:
                raise ValueError("Query parameter is required")
            if not keywords:
                raise ValueError("Key_words parameter is required")

            result = await asyncio.to_thread(
                web_search, query, keywords, full_context, num_websites, num_citations
            )
            return [
                types.TextContent(
                    type="text",
                    text=str(result)
                )
            ]
        
        elif name == "wiki_search":
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
        
        elif name == "scrape_webpage":
            url = arguments.get("url", "")
            if not url:
                raise ValueError("URL parameter is required")
            
            result = await asyncio.to_thread(scrape_webpage, url)
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
        
        elif name == "youtube_info":
            url = arguments.get("url", "")
            if not url:
                raise ValueError("URL parameter is required")
            
            result = await asyncio.to_thread(youtube_info, url)
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