"""
LLM Tool Calling Web Application
This module provides a chat interface with various tool-calling capabilities.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Any

from openai import OpenAI
from colorama import init, Fore, Back, Style

from utilities import LoadingAnimation, create_centered_box, system_message

# Custom Styles
CUSTOM_ORANGE = '\x1b[38;5;216m'
BOLD = '\033[1m'
# Initialize colorama
init()

# tool imports
from Python_tool.PythonExecutor_secure import execute_python_code as python
from web_tool.web_browsing import (
    text_search as web,
    webpage_scraper as URL,
    images_search as image,
    deep_search
)
from wiki_tool.search_wiki import fetch_wikipedia_content as wiki
from youtube_tool.youtube import (
    search_youtube as youtube,
    get_video_info as watch
)

# Constants
MODEL = "qwen3-0.6b"
BASE_URL = "http://127.0.0.1:1234/v1"
API_KEY = "dummy_key"

# Initialize OpenAI client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Configuration
show_stream = False  # Set to False for non-streaming mode
show_thinking = False  # Set to False to disable thinking mask
show_tool_calls = True  # Set to False to disable tool call display
show_LLM_label = False  # Set to False to disable assistant label in streaming mode

Tools = [
    {
        "type": "function",
        "function": {
            "name": "python",
            "description": "Execute Python code and return the execution results. Use for math problems or task automation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Complete Python code to execute. Must return a value."}
                },
                "required": ["code"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "web",
            "description": f"Perform a quick web search for relevant realtime information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for websites"},
                    "Key_words": {"type": "list", "description": "list of Key word used for finding relevant citations"},
                    "number_of_websites": {
                        "type": "integer",
                        "description": "Maximum websites to visit",
                        "default": 4,
                    },
                    "number_of_citations": {
                        "type": "integer",
                        "description": "Maximum citations to scrape",
                        "default": 4,
                    }
                },
                "required": ["query", "Key_words"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "wiki",
            "description": "Search Wikipedia for the most relevant article introduction",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for Wikipedia article"}
                },
                "required": ["query"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "URL",
            "description": "Scrape a website for its content",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL of the website to scrape"}
                },
                "required": ["url"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "image",
            "description": f"Search the web for images.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for images"},
                    "number_of_images": {
                        "type": "integer",
                        "description": "Maximum images to get",
                        "default": 1,
                    },
                },
                "required": ["query"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "youtube",
            "description": f"Search youtube videos and retrive the urls.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for vidoes"},
                    "number_of_videos": {
                        "type": "integer",
                        "description": "Maximum videos to get",
                        "default": 1,
                    },
                },
                "required": ["query"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "watch",
            "description": "get information about a youtube video (title, descrption and transcription)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL of the youtube video"},
                },
                "required": ["url"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "deep_search",
            "description": "Perform a deep web search for content with detailed summaries of search results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for web search"},
                    "prompt": {"type": "string", "description": "Explain the what the user is looking for"},
                    "number_of_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to analyze",
                        "default": 5,
                        "minimum": 3,
                        "maximum": 10
                    }
                },
                "required": ["query", "prompt"]
            }
        }
    }
]

def process_stream(stream: Any) -> Tuple[str, List[Dict]]:
    """
    Handle streaming responses from the API.
    
    Args:
        stream: The response stream from the API

    Returns:
        Tuple containing collected text and tool calls
    """
    collected_text = ""
    tool_calls = []
    first_chunk = True
    thinking_buffer = ""
    in_thinking = False

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Handle regular text output
        if delta.content:
            content = delta.content
            
            # Check for opening think tag
            if "<think>" in content:
                in_thinking = True
                content = content.split("<think>")[0]
            
            # Check for closing think tag
            if "</think>" in content:
                in_thinking = False
                content = content.split("</think>")[1]
            
            # Only process content if we're not in thinking mode
            if not in_thinking and content:
                if first_chunk:
                    if show_LLM_label:
                        print(f"{Fore.LIGHTRED_EX}{MODEL}:{Style.RESET_ALL}", end=" ", flush=True)
                    else:
                        print(f"{Fore.LIGHTRED_EX}Assistant:{Style.RESET_ALL}", end=" ", flush=True)
                    first_chunk = False
                print(content, end="", flush=True)
                collected_text += content

        # Handle tool calls
        elif delta.tool_calls:
            for tc in delta.tool_calls:
                if len(tool_calls) <= tc.index:
                    tool_calls.append({
                        "id": "", "type": "function",
                        "function": {"name": "", "arguments": ""}
                    })
                tool_calls[tc.index] = {
                    "id": (tool_calls[tc.index]["id"] + (tc.id or "")),
                    "type": "function",
                    "function": {
                        "name": (tool_calls[tc.index]["function"]["name"] + (tc.function.name or "")),
                        "arguments": (tool_calls[tc.index]["function"]["arguments"] + (tc.function.arguments or ""))
                    }
                }
    return collected_text, tool_calls

def process_non_stream(response: Any) -> Tuple[str, List[Dict]]:
    """
    Handle non-streaming responses from the API.
    
    Args:
        response: The non-streaming response from the API
    
    Returns:
        Tuple containing response text and tool calls
    """
    collected_text = ""
    tool_calls = []
        
    # Extract content if present
    if response.choices[0].message.content:
        content = response.choices[0].message.content

        while "<think>" in content and "</think>" in content and not show_thinking:
            start = content.find("<think>")
            end = content.find("</think>") + len("</think>")
            content = content[:start] + content[end:]

        if show_LLM_label:
            print(f"{Fore.WHITE}{BOLD}{create_centered_box(content, MODEL)}{Style.RESET_ALL}", end="", flush=True)
        else:
            print(f"{Fore.WHITE}{BOLD}{create_centered_box(content, 'Assistant')}{Style.RESET_ALL}", end="", flush=True)
        collected_text = content
    
    # Extract tool calls if present
    if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
        for tc in response.choices[0].message.tool_calls:
            tool_calls.append({
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            })
    
    return collected_text, tool_calls

def show_help() -> None:
    """Display available tools and commands."""
    
    help_text = ''
    for tool in Tools:
        name = f"• {tool['function']['name']}"
        desc = tool['function']['description']
        help_text += f"{name}: {desc}\n"
    print(f"{BOLD}{create_centered_box(help_text, 'Available Tools')}{Style.RESET_ALL}")

def display_welcome_banner() -> None:
    banner = """
███████╗██╗██╗  ██╗    ██╗     ███╗   ███╗
 ██╔════╝██║╚██╗██╔╝    ██║     ████╗ ████║
 █████╗  ██║ ╚███╔╝     ██║     ██╔████╔██║
 ██╔══╝  ██║ ██╔██╗     ██║     ██║╚██╔╝██║
 ██║     ██║██╔╝ ██╗    ███████╗██║ ╚═╝ ██║
 ╚═╝     ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝     ╚═╝

Type 'help' to see available tools
Type 'clear' to start new chat
"""
    print(f"{CUSTOM_ORANGE}{BOLD}{create_centered_box(banner, center_align=True)}{Style.RESET_ALL}")

def chat_loop() -> None:
    """Main chat interaction loop."""
    messages: List[Dict] = []
    messages.append({"role": "system", "content": system_message.format(current_datetime=datetime.now())})
    thinking = LoadingAnimation("Thinking")
    loading = LoadingAnimation("Executing Tool")

    os.system('cls' if os.name == "nt" else 'clear')
    display_welcome_banner()
    while True:
        print(f"\n{CUSTOM_ORANGE}➤ {Style.RESET_ALL} ", end="")
        user_input = input().strip()
        if not user_input:
            continue
        
        # Handle commands
        if user_input.lower() == "clear":
            messages = []
            messages.append({"role": "system", "content": system_message.format(current_datetime=datetime.now())})
            os.system('cls' if os.name == "nt" else 'clear')
            display_welcome_banner()
            continue
        if user_input.lower() == "help":
            show_help()
            continue

        # Show user input in a box
        if not show_stream:
            print(f"{CUSTOM_ORANGE}{BOLD}{create_centered_box(user_input, 'You')}{Style.RESET_ALL}")

        # Process user input
        messages.append({"role": "user", "content": user_input})
        continue_tool_execution = True

        while continue_tool_execution:
            thinking.start() if not show_stream else None
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=Tools,
                stream=show_stream,
                temperature=0.7
            )
            thinking.stop() if not show_stream else None
            if show_stream:
                response_text, tool_calls = process_stream(response)
            else:
                response_text, tool_calls = process_non_stream(response)

            if not tool_calls:
                continue_tool_execution = False

            text_in_response = len(response_text) > 0
            if text_in_response:
                messages.append({"role": "assistant", "content": response_text})

            # Handle tool calls
            if tool_calls:                
                # Execute tool calls
                for tool_call in tool_calls:
                    arguments = json.loads(tool_call["function"]["arguments"])
                    tool_name = tool_call["function"]["name"]
                    print(f"{Fore.YELLOW}{create_centered_box(str(arguments), (str(tool_name)).upper(), center_align=True)}{Style.RESET_ALL}")
                    loading.start()
                    if tool_name == "python":
                        result = python(arguments["code"])
                    
                    elif tool_name == "web":
                        result = web(
                            arguments["query"],
                            arguments.get("Key_words", arguments["query"]),
                            arguments.get("number_of_websites", 3),
                            arguments.get("number_of_citations", 5)
                        )

                    elif tool_name == "deep_search":
                        result = deep_search(
                            arguments["query"],
                            arguments["prompt"],
                            arguments.get("number_of_results", 10),
                            client,
                            MODEL
                        )
                    
                    elif tool_name == "wiki":
                        result = wiki(arguments["query"])

                    elif tool_name == "URL":
                        result = URL(arguments["url"])

                    elif tool_name == "image":
                        result = image(arguments["query"], arguments.get("number_of_images", 1))
                        
                    elif tool_name == "youtube":
                        result = youtube(arguments["query"], arguments.get("number_of_videos", 1))
                        
                    elif tool_name == "watch":
                        result = watch(arguments["url"])
                    else:
                        result = f"Unknown tool: {tool_name}"
                    
                    messages.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call["id"]
                        })
                    loading.stop()
                    if show_tool_calls: print(f"{Fore.GREEN}{create_centered_box(str(result), 'Tool Call Result')}{Style.RESET_ALL}")
                    
                # Continue checking for more tool calls after tool execution
                continue_tool_execution = True
            else:
                continue_tool_execution = False

if __name__ == "__main__":
    try:
        chat_loop()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        chat_loop()
        print(f"\n\n{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Application restarted{Style.RESET_ALL}")
