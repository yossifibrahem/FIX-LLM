"""
LLM Tool Calling Web Application
This module provides a chat interface with various tool-calling capabilities.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional

from openai import OpenAI
from colorama import init, Fore, Back, Style

from utilities.utilities import LoadingAnimation, create_centered_box, system_message

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
show_llm_label = False  # Set to False to disable assistant label in streaming mode

Tools = [
    {
        "type": "function",
        "function": {
            "name": "python",
            "description": "Execute Python code and return the execution results. Use for math problems or task automation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Complete Python script to execute. Must return a value."}
                },
                "required": ["code"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "web",
            "description": "Perform a web search for realtime information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for websites"},
                    "number_of_websites": {
                        "type": "integer",
                        "description": "Maximum websites to visit",
                        "default": 4,
                    },
                    "full_context": {
                        "type": "boolean",
                        "description": "Whether to return full context from the websites or only relevant citations. set to true for detailed information. or false for concise information.",
                        "default": False
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}, 
                        "description": "if full_context is false, list of Key word used for finding relevant citations"
                    },
                    "number_of_citations": {
                        "type": "integer",
                        "description": "if full_context is false, number of chunks to return",
                        "default": 4,
                    }
                },
                "required": ["query"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "wiki",
            "description": "Search Wikipedia for the most relevant article. useful for getting information about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for Wikipedia article"},
                    "full_article": {
                        "type": "boolean",
                        "description": "If True, returns the full article content. If False, returns only the introduction.",
                        "default": False
                    }
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
            "description": "Search the web for images.",
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
            "description": "Search youtube videos and retrieve the urls.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for videos"},
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
            "description": "get information about a youtube video (title, description and transcription)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL of the youtube video"},
                },
                "required": ["url"]
            }
        }
    },
]

def remove_thinking_tags(content: str) -> str:
    """Remove thinking tags from content efficiently."""
    if not show_thinking and "<think>" in content and "</think>" in content:
        while "<think>" in content and "</think>" in content:
            start = content.find("<think>")
            end = content.find("</think>") + len("</think>")
            content = content[:start] + content[end:]
    return content

def display_response(content: str, label: str) -> None:
    """Common function for displaying responses."""
    print(f"{Fore.WHITE}{BOLD}{create_centered_box(content, label)}{Style.RESET_ALL}", end="", flush=True)

def display_tool_call(arguments: dict, tool_name: str) -> None:
    """Common function for displaying tool calls."""
    print(f"{Fore.YELLOW}{create_centered_box(str(arguments), tool_name.upper(), center_align=True)}{Style.RESET_ALL}")

def display_tool_result(result: str) -> None:
    """Common function for displaying tool results."""
    print(f"{Fore.GREEN}{create_centered_box(str(result), 'Tool Call Result')}{Style.RESET_ALL}")

def process_stream(stream: Any) -> Tuple[str, List[Dict]]:
    """
    Handle streaming responses from the API.
    
    Args:
        stream: The response stream from the API

    Returns:
        Tuple containing collected text and tool calls
    """
    text_parts = []
    tool_calls = []
    first_chunk = True
    in_thinking = False

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Handle regular text output
        if delta.content:
            content = delta.content
            
            # Check for thinking tags
            if "<think>" in content:
                in_thinking = True
                content = content.split("<think>")[0]
            
            if "</think>" in content:
                in_thinking = False
                content = content.split("</think>")[1]
            
            # Only process content if we're not in thinking mode or if thinking is enabled
            if (not in_thinking or show_thinking) and content:
                if first_chunk:
                    label = MODEL if show_llm_label else "Assistant"
                    print(f"{Fore.LIGHTRED_EX}{label}:{Style.RESET_ALL}", end=" ", flush=True)
                    first_chunk = False
                print(content, end="", flush=True)
                text_parts.append(content)

        # Handle tool calls
        elif delta.tool_calls:
            for tc in delta.tool_calls:
                # Ensure tool_calls list is large enough
                while len(tool_calls) <= tc.index:
                    tool_calls.append({
                        "id": "", "type": "function",
                        "function": {"name": "", "arguments": ""}
                    })
                
                # Build tool call incrementally
                current_call = tool_calls[tc.index]
                current_call["id"] = current_call["id"] + (tc.id or "")
                current_call["function"]["name"] = current_call["function"]["name"] + (tc.function.name or "")
                current_call["function"]["arguments"] = current_call["function"]["arguments"] + (tc.function.arguments or "")
    
    collected_text = ''.join(text_parts)
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
        content = remove_thinking_tags(content)
        
        if content.strip():  # Only display if there's actual content
            label = MODEL if show_llm_label else "Assistant"
            display_response(content, label)
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

def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Execute a tool with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments for the tool
        
    Returns:
        Result of the tool execution
    """
    try:
        if tool_name == "python":
            return python(arguments["code"])
        
        elif tool_name == "web":
            return web(
                arguments["query"],
                arguments.get("keywords", [arguments["query"]]),
                arguments.get("full_context", False),
                arguments.get("number_of_websites", 3),
                arguments.get("number_of_citations", 5)
            )
        
        elif tool_name == "wiki":
            return wiki(arguments["query"], arguments.get("full_article", False))

        elif tool_name == "URL":
            return URL(arguments["url"])

        elif tool_name == "image":
            return image(arguments["query"], arguments.get("number_of_images", 1))
            
        elif tool_name == "youtube":
            return youtube(arguments["query"], arguments.get("number_of_videos", 1))
            
        elif tool_name == "watch":
            return watch(arguments["url"])
        else:
            return f"Unknown tool: {tool_name}"
            
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"


def show_help() -> None:
    """Display available tools and commands."""
    help_text = ""
    for tool in Tools:
        name = f"• {tool['function']['name']}"
        desc = tool['function']['description']
        help_text += f"{name}: {desc}\n"
    
    help_text += "\nCommands:\n"
    help_text += "• help: Show this help message\n"
    help_text += "• clear: Start a new chat session\n"
    help_text += "• exit/quit: Exit the application\n"
    
    print(f"{BOLD}{create_centered_box(help_text, 'Available Tools & Commands')}{Style.RESET_ALL}")

def display_welcome_banner() -> None:
    """Display the welcome banner."""
    banner = """
███████╗██╗██╗  ██╗    ██╗     ███╗   ███╗
 ██╔════╝██║╚██╗██╔╝    ██║     ████╗ ████║
 █████╗  ██║ ╚███╔╝     ██║     ██╔████╔██║
 ██╔══╝  ██║ ██╔██╗     ██║     ██║╚██╔╝██║
 ██║     ██║██╔╝ ██╗    ███████╗██║ ╚═╝ ██║
 ╚═╝     ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝     ╚═╝

Type 'help' to see available tools
Type 'clear' to start new chat
Type 'exit' or 'quit' to quit
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
        try:
            print(f"\n{CUSTOM_ORANGE}➤ {Style.RESET_ALL} ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                break
                
            if user_input.lower() == "clear":
                messages = []
                messages.append({"role": "system", "content": system_message.format(current_datetime=datetime.now())})
                os.system('cls' if os.name == "nt" else 'clear')
                display_welcome_banner()
                continue
                
            if user_input.lower() == "help":
                show_help()
                continue

            # Show user input in a box for non-streaming mode
            if not show_stream:
                print(f"{CUSTOM_ORANGE}{BOLD}{create_centered_box(user_input, 'You')}{Style.RESET_ALL}")

            # Process user input
            messages.append({"role": "user", "content": user_input})
            
            continue_tool_execution = True

            while continue_tool_execution:
                # Start thinking animation for non-streaming mode
                if not show_stream:
                    thinking.start()
                    
                try:
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=messages,
                        tools=Tools,
                        stream=show_stream,
                        temperature=0.7
                    )
                except Exception as e:
                    if not show_stream:
                        thinking.stop()
                    print(f"\n{Fore.RED}Error communicating with model: {e}{Style.RESET_ALL}")
                    continue_tool_execution = False
                    continue
                    
                if not show_stream:
                    thinking.stop()
                    
                # Process response
                if show_stream:
                    response_text, tool_calls = process_stream(response)
                else:
                    response_text, tool_calls = process_non_stream(response)

                # Add assistant response to messages if there's text content
                if response_text and response_text.strip():
                    messages.append({"role": "assistant", "content": response_text})

                # Handle tool calls
                if tool_calls:
                    for tool_call in tool_calls:
                        try:
                            arguments = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError as e:
                            print(f"\n{Fore.RED}Invalid JSON in tool call: {e}{Style.RESET_ALL}")
                            continue
                        
                        tool_name = tool_call["function"]["name"]
                        
                        # Display tool call
                        display_tool_call(arguments, tool_name)
                        
                        # Execute tool
                        loading.start()
                        try:
                            result = execute_tool(tool_name, arguments)
                        except Exception as e:
                            result = f"Error executing {tool_name}: {str(e)}"
                        finally:
                            loading.stop()
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call["id"]
                        })
                        
                        # Display tool result
                        if show_tool_calls:
                            display_tool_result(result)
                    
                    # Continue to process any follow-up responses
                    continue_tool_execution = True
                else:
                    continue_tool_execution = False
                    
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Continuing...{Style.RESET_ALL}")

if __name__ == "__main__":
    chat_loop()