#!/usr/bin/env python3
"""
MCP Server with Python, Web, Wiki, and YouTube tools
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Tool imports
from Python_tool.PythonExecutor_secure import execute_python_code as python
from web_tool.web_browsing import (
    text_search as web,
    webpage_scraper as URL,
    images_search as image,
)
from wiki_tool.search_wiki import fetch_wikipedia_content as wiki
from youtube_tool.youtube import (
    search_youtube as youtube,
    get_video_info as watch
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPToolServer:
    def __init__(self):
        self.server = Server("mcp-tool-server")
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup all MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
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
                Tool(
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
                        "required": ["query", "Key_words"]
                    }
                ),
                Tool(
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
                Tool(
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
                Tool(
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
                Tool(
                    name="youtube",
                    description="Search youtube videos and retrive the urls.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for vidoes"
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
                Tool(
                    name="watch",
                    description="get information about a youtube video (title, descrption and transcription)",
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

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "python":
                    code = arguments.get("code", "")
                    if not code:
                        return [TextContent(type="text", text="Error: No code provided")]
                    
                    result = await self._execute_python(code)
                    return [TextContent(type="text", text=str(result))]
                
                elif name == "web":
                    query = arguments.get("query", "")
                    keywords = arguments.get("Key_words", [query])
                    num_websites = arguments.get("number_of_websites", 4)
                    num_citations = arguments.get("number_of_citations", 4)
                    
                    if not query or not keywords:
                        return [TextContent(type="text", text="Error: Query and keywords are required")]
                    
                    result = await self._web_search(query, keywords, num_websites, num_citations)
                    return [TextContent(type="text", text=str(result))]
                
                elif name == "wiki":
                    query = arguments.get("query", "")
                    if not query:
                        return [TextContent(type="text", text="Error: Query is required")]
                    
                    result = await self._wiki_search(query)
                    return [TextContent(type="text", text=str(result))]
                
                elif name == "URL":
                    url = arguments.get("url", "")
                    if not url:
                        return [TextContent(type="text", text="Error: URL is required")]
                    
                    result = await self._scrape_url(url)
                    return [TextContent(type="text", text=str(result))]
                
                elif name == "image":
                    query = arguments.get("query", "")
                    num_images = arguments.get("number_of_images", 1)
                    
                    if not query:
                        return [TextContent(type="text", text="Error: Query is required")]
                    
                    result = await self._image_search(query, num_images)
                    return [TextContent(type="text", text=str(result))]
                
                elif name == "youtube":
                    query = arguments.get("query", "")
                    num_videos = arguments.get("number_of_videos", 1)
                    
                    if not query:
                        return [TextContent(type="text", text="Error: Query is required")]
                    
                    result = await self._youtube_search(query, num_videos)
                    return [TextContent(type="text", text=str(result))]
                
                elif name == "watch":
                    url = arguments.get("url", "")
                    if not url:
                        return [TextContent(type="text", text="Error: URL is required")]
                    
                    result = await self._watch_youtube(url)
                    return [TextContent(type="text", text=str(result))]
                
                else:
                    return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
                    
            except Exception as e:
                logger.error(f"Error in tool '{name}': {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _execute_python(self, code: str) -> Any:
        """Execute Python code using the imported function"""
        try:
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, python, code)
            return result
        except Exception as e:
            logger.error(f"Python execution error: {str(e)}")
            return f"Python execution error: {str(e)}"

    async def _web_search(self, query: str, keywords: List[str], num_websites: int, num_citations: int) -> Any:
        """Perform web search using the imported function"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                web, 
                query, 
                keywords, 
                num_websites, 
                num_citations
            )
            return result
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return f"Web search error: {str(e)}"

    async def _wiki_search(self, query: str) -> Any:
        """Search Wikipedia using the imported function"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, wiki, query)
            return result
        except Exception as e:
            logger.error(f"Wiki search error: {str(e)}")
            return f"Wiki search error: {str(e)}"

    async def _scrape_url(self, url: str) -> Any:
        """Scrape URL using the imported function"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, URL, url)
            return result
        except Exception as e:
            logger.error(f"URL scraping error: {str(e)}")
            return f"URL scraping error: {str(e)}"

    async def _image_search(self, query: str, num_images: int) -> Any:
        """Search for images using the imported function"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, image, query, num_images)
            return result
        except Exception as e:
            logger.error(f"Image search error: {str(e)}")
            return f"Image search error: {str(e)}"

    async def _youtube_search(self, query: str, num_videos: int) -> Any:
        """Search YouTube using the imported function"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, youtube, query, num_videos)
            return result
        except Exception as e:
            logger.error(f"YouTube search error: {str(e)}")
            return f"YouTube search error: {str(e)}"

    async def _watch_youtube(self, url: str) -> Any:
        """Get YouTube video info using the imported function"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, watch, url)
            return result
        except Exception as e:
            logger.error(f"YouTube watch error: {str(e)}")
            return f"YouTube watch error: {str(e)}"

async def main():
    """Main entry point for the MCP server"""
    tool_server = MCPToolServer()
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await tool_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-tool-server",
                server_version="1.0.0",
                capabilities=tool_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())