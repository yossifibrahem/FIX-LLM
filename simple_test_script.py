#!/usr/bin/env python3
"""
Simple test script for MCP server
Run this to verify your server works before integrating with clients
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🚀 Testing MCP Server...")
    print("=" * 50)
    
    try:
        # Import the server
        from mcp_servers import MCPToolServer
        server = MCPToolServer()
        print("✅ Server imported successfully")
        
        # Test 1: Python execution
        print("\n📝 Testing Python tool...")
        try:
            result = await server._execute_python("print('Hello MCP!'); result = 2 + 3; result")
            print(f"   Result: {result}")
            print("✅ Python tool working")
        except Exception as e:
            print(f"❌ Python tool failed: {e}")
        
        # Test 2: Wikipedia search
        print("\n📚 Testing Wikipedia tool...")
        try:
            result = await server._wiki_search("Python programming language")
            print(f"   Result length: {len(str(result))} characters")
            print("✅ Wikipedia tool working")
        except Exception as e:
            print(f"❌ Wikipedia tool failed: {e}")
        
        # Test 3: Web search
        print("\n🌐 Testing Web search tool...")
        try:
            result = await server._web_search(
                query="Python programming", 
                keywords=["Python", "programming"], 
                num_websites=2, 
                num_citations=2
            )
            print(f"   Result type: {type(result)}")
            print("✅ Web search tool working")
        except Exception as e:
            print(f"❌ Web search tool failed: {e}")
        
        # Test 4: URL scraping
        print("\n🔗 Testing URL scraping tool...")
        try:
            result = await server._scrape_url("https://httpbin.org/html")
            print(f"   Result length: {len(str(result))} characters")
            print("✅ URL scraping tool working")
        except Exception as e:
            print(f"❌ URL scraping tool failed: {e}")
        
        # Test 5: Image search
        print("\n🖼️ Testing Image search tool...")
        try:
            result = await server._image_search("python logo", 1)
            print(f"   Result type: {type(result)}")
            print("✅ Image search tool working")
        except Exception as e:
            print(f"❌ Image search tool failed: {e}")
        
        # Test 6: YouTube search
        print("\n📺 Testing YouTube search tool...")
        try:
            result = await server._youtube_search("Python tutorial", 1)
            print(f"   Result type: {type(result)}")
            print("✅ YouTube search tool working")
        except Exception as e:
            print(f"❌ YouTube search tool failed: {e}")
        
        # Test 7: YouTube watch
        print("\n👀 Testing YouTube watch tool...")
        try:
            # Using a popular Python tutorial video
            result = await server._watch_youtube("https://www.youtube.com/watch?v=_uQrJ0TkZlc")
            print(f"   Result type: {type(result)}")
            print("✅ YouTube watch tool working")
        except Exception as e:
            print(f"❌ YouTube watch tool failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 MCP Server testing complete!")
        print("\nNext steps:")
        print("1. If all tests passed, your server is ready!")
        print("2. Configure Claude Desktop with the MCP config")
        print("3. Or use MCP Inspector: npm install -g @modelcontextprotocol/inspector")
        print("4. Then run: mcp-inspector python mcp_servers.py")
        
    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        print("Make sure all your tool modules are available and properly installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

async def test_tool_imports():
    """Test that all tool modules can be imported"""
    print("\n🔍 Testing tool imports...")
    
    tools = [
        ("Python tool", "Python_tool.PythonExecutor_secure", "execute_python_code"),
        ("Web search", "web_tool.web_browsing", "text_search"),
        ("Web scraper", "web_tool.web_browsing", "webpage_scraper"),
        ("Image search", "web_tool.web_browsing", "images_search"),
        ("Wiki search", "wiki_tool.search_wiki", "fetch_wikipedia_content"),
        ("YouTube search", "youtube_tool.youtube", "search_youtube"),
        ("YouTube watch", "youtube_tool.youtube", "get_video_info"),
    ]
    
    for tool_name, module_name, function_name in tools:
        try:
            module = __import__(module_name, fromlist=[function_name])
            getattr(module, function_name)
            print(f"✅ {tool_name}: {module_name}.{function_name}")
        except ImportError as e:
            print(f"❌ {tool_name}: Import failed - {e}")
        except AttributeError as e:
            print(f"❌ {tool_name}: Function not found - {e}")

if __name__ == "__main__":
    # First test imports
    asyncio.run(test_tool_imports())
    
    # Then test server functionality
    asyncio.run(test_mcp_server())