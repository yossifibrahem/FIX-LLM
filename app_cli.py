"""
LLM Tool Calling Web Application
This module provides a chat interface with various tool-calling capabilities.
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Tuple, Any
from textwrap import fill

from openai import OpenAI
from colorama import init, Fore, Back, Style
# Custom Styles
CUSTOM_ORANGE = '\x1b[38;5;216m'
BOLD = '\033[1m'

# tool imports
from Python_tool.PythonExecutor_secure import execute_python_code as python
from web_tool.web_browsing import (
    text_search as web,
    webpage_scraper as URL,
    images_search as image
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

# Configuration
use_streaming = False  # Set to False for non-streaming mode
show_thinking = False  # Set to False to disable thinking mask

# Initialize OpenAI client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Initialize colorama
init()

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
            "description": f"Search the web for relevant realtime information. Current date and time: {datetime.now()}",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for websites"},
                    "citation_finder": {"type": "string", "description": "Used for finding relevant citations"},
                    "number_of_websites": {
                        "type": "integer",
                        "description": "Maximum websites to visit",
                        "default": 4,
                    },
                    "number_of_citations": {
                        "type": "integer",
                        "description": "Maximum citations to scrape",
                        "default": 5,
                    }
                },
                "required": ["query"]
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
    }
]

def get_terminal_width() -> int:
    """Get the current terminal width."""
    width, _ = shutil.get_terminal_size()
    return width

def create_centered_box(text: str, header: str = '', padding: int = 4, center_align: bool = False) -> str:
    """
    Create a centered box with dynamic width and centered header.
    
    Args:
        text (str): The text to be displayed in the box
        header (str): Optional header text to show at top of box
        padding (int): Number of spaces for padding on each side
        center_align (bool): Whether to center the text (True) or left-align it (False)
    
    Returns:
        str: Formatted box with the text
    """
    # Get terminal width
    width = get_terminal_width()
    
    # Create box characters
    TOP_LEFT = "╭"
    TOP_RIGHT = "╮"
    BOTTOM_LEFT = "╰"
    BOTTOM_RIGHT = "╯"
    HORIZONTAL = "─"
    VERTICAL = "│"
    
    # Calculate content width
    content_width = width - (2 * padding) - 2  # -2 for the vertical borders
    
    # Split text into lines that fit the content width
    lines = []
    for line in text.split('\n'):
        while len(line) > content_width:
            split_point = line[:content_width].rfind(' ')
            if split_point == -1:
                split_point = content_width
            lines.append(line[:split_point])
            line = line[split_point:].strip()
        if line:
            lines.append(line)
    
    # Create the box
    result = []
    
    # Top border with centered header if provided
    if header:
        header_text = f" {header} "
        header_length = len(header_text)
        left_padding = (width - header_length) // 2
        right_padding = width - left_padding - header_length
        top_border = (
            f"{TOP_LEFT}"
            f"{HORIZONTAL * (left_padding - 1)}"
            f"{header_text}"
            f"{HORIZONTAL * (right_padding - 1)}"
            f"{TOP_RIGHT}"
        )
        result.append(top_border)
    else:
        result.append(f"{TOP_LEFT}{HORIZONTAL * (width - 2)}{TOP_RIGHT}")
    
    # Content
    for line in lines:
        if center_align:
            # Center alignment
            padding_left = (content_width - len(line)) // 2
            padding_right = content_width - len(line) - padding_left
            padded_line = " " * padding_left + line + " " * padding_right
        else:
            # Left alignment
            padded_line = line + " " * (content_width - len(line))
        
        result.append(f"{VERTICAL}{' ' * padding}{padded_line}{' ' * padding}{VERTICAL}")
    
    # Bottom border
    result.append(f"{BOTTOM_LEFT}{HORIZONTAL * (width - 2)}{BOTTOM_RIGHT}")
    
    return "\n".join(result)

def process_stream(stream: Any, add_assistant_label: bool = True) -> Tuple[str, List[Dict]]:
    """
    Handle streaming responses from the API.
    
    Args:
        stream: The response stream from the API
        add_assistant_label: Whether to prefix output with 'Assistant:'
    
    Returns:
        Tuple containing collected text and tool calls
    """
    collected_text = ""
    tool_calls = []
    first_chunk = True

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Handle regular text output
        if delta.content:
            # Hide <think>...</think> if show_thinking is False
            content = delta.content
            while "<think>" in content and "</think>" in content and not show_thinking:
                start = content.find("<think>")
                end = content.find("</think>") + len("</think>")
                content = content[:start] + content[end:]
            if content:
                if first_chunk:
                    if add_assistant_label:
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

def process_non_stream(response: Any, add_assistant_label: bool = True) -> Tuple[str, List[Dict]]:
    """
    Handle non-streaming responses from the API.
    
    Args:
        response: The non-streaming response from the API
        add_assistant_label: Whether to prefix output with 'Assistant:'
    
    Returns:
        Tuple containing response text and tool calls
    """
    collected_text = ""
    tool_calls = []
    
    # print()
    
    # Extract content if present
    if response.choices[0].message.content:
        content = response.choices[0].message.content

        while "<think>" in content and "</think>" in content and not show_thinking:
            start = content.find("<think>")
            end = content.find("</think>") + len("</think>")
            content = content[:start] + content[end:]


        print(f"{Fore.WHITE}{BOLD}{create_centered_box(content, MODEL)}{Style.RESET_ALL}", end="", flush=True)
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
    width = get_terminal_width()
    
    print(f"\n{CUSTOM_ORANGE}{BOLD} Available Tools {Style.RESET_ALL}")
    print("─" * width)
    for tool in Tools:
        name = f"{CUSTOM_ORANGE}• {tool['function']['name']}{Style.RESET_ALL}"
        desc = tool['function']['description']
        wrapped_desc = fill(desc, width=width - len(name) + len(Fore.BLUE) + len(Style.RESET_ALL))
        print(f"{name}: {wrapped_desc}")
    
    print(f"\n{CUSTOM_ORANGE}{BOLD} Available Commands {Style.RESET_ALL}")
    print("─" * width)
    print(f"{CUSTOM_ORANGE}• clear{Style.RESET_ALL}: Clear the chat history")
    print(f"{CUSTOM_ORANGE}• help{Style.RESET_ALL}: Show this help message")


def display_welcome_banner() -> None:
    banner = """
 ██████╗██╗  ██╗ █████╗ ████████╗
██╔════╝██║  ██║██╔══██╗╚══██╔══╝
██║     ███████║███████║   ██║   
██║     ██╔══██║██╔══██║   ██║   
╚██████╗██║  ██║██║  ██║   ██║   
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   

Type 'help' to see available tools
Type 'clear' to start new chat
"""
    print(f"{CUSTOM_ORANGE}{BOLD}{create_centered_box(banner, center_align=True)}{Style.RESET_ALL}")

def chat_loop() -> None:
    """Main chat interaction loop."""
    messages: List[Dict] = []

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
            os.system('cls' if os.name == "nt" else 'clear')
            display_welcome_banner()
            continue
        if user_input.lower() == "help":
            show_help()
            continue

        # Show user input in a box
        if not use_streaming:
            print(f"{CUSTOM_ORANGE}{BOLD}{create_centered_box(user_input, 'You')}{Style.RESET_ALL}")

        # Process user input
        messages.append({"role": "user", "content": user_input})
        continue_tool_execution = True

        while continue_tool_execution:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=Tools,
                stream=use_streaming,
                temperature=0.7
            )
            
            if use_streaming:
                response_text, tool_calls = process_stream(response)
            else:
                response_text, tool_calls = process_non_stream(response)

            if not tool_calls:
                # print()
                continue_tool_execution = False

            text_in_response = len(response_text) > 0
            if text_in_response:
                messages.append({"role": "assistant", "content": response_text})

            # Handle tool calls
            if tool_calls:
                tool_name = tool_calls[0]["function"]["name"]
                width = get_terminal_width()
                
                
                # Execute tool calls
                for tool_call in tool_calls:
                    message = tool_call["function"]["name"] + tool_call["function"]["arguments"]
                    # print(f"{Fore.YELLOW}{create_centered_box(message, 'Tool Call')}{Style.RESET_ALL}")
                    arguments = json.loads(tool_call["function"]["arguments"])
                    tool_name = tool_call["function"]["name"]
                    
                    if tool_name == "python":
                        result = python(arguments["code"])
                    
                    elif tool_name == "web":
                        result = web(
                            arguments["query"],
                            arguments.get("embedding_matcher", arguments["query"]),
                            arguments.get("number_of_websites", 3),
                            arguments.get("number_of_citations", 5)
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
                    
                    messages.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call["id"]
                        })
                    # print(f"{Fore.YELLOW}{create_centered_box(str(result), 'Tool Call Result')}{Style.RESET_ALL}")
            
                # Continue checking for more tool calls after tool execution
                continue_tool_execution = True
            else:
                continue_tool_execution = False

if __name__ == "__main__":
    try:
        chat_loop()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
