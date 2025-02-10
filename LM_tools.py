# Standard library imports
import json
from datetime import datetime
from datetime import datetime

# Third-party imports
from openai import OpenAI

from Python_tool.PythonExecutor_secure import execute_python_code as python
from web_tool.web_browsing import text_search as web
from wiki_tool.search_wiki import fetch_wikipedia_content as wiki
from web_tool.web_browsing import webpage_scraper as web_url
from web_tool.web_browsing import images_search as image
from youtube_tool.youtube  import search_youtube as video
from youtube_tool.youtube import get_video_info as yt_url


client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "lmstudio-community/qwen2.5-7b-instruct"

Tools = [{
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
        "description": f"Search the web for relevant information. Current timestamp: {datetime.now()}",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for websites"},
                "embedding_matcher": {"type": "string", "description": "Used for finding relevant citations"},
                "number_of_websites": {
                    "type": "integer",
                    "description": "Maximum websites to visit",
                    "default": 4,
                },
                "number_of_citations": {
                    "type": "integer",
                    "description": "Maximum citations to scrape (250 words each)",
                    "default": 5,
                }
            },
            "required": ["query", "embedding_matcher"]
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
        "name": "web_url",
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
                    "default": 3,
                },
            },
            "required": ["query"]
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "video",
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
        "name": "yt_url",
        "description": "get information about a youtube video (title and descrption)",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL of the youtube video"},
            },
            "required": ["url"]
        }
    }
}]

def process_stream(stream, add_assistant_label=True):
    """Handle streaming responses from the API"""
    collected_text = ""
    tool_calls = []
    first_chunk = True

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Handle regular text output
        if delta.content:
            if first_chunk:
                print()
                if add_assistant_label:
                    print("Assistant:", end=" ", flush=True)
                first_chunk = False
            print(delta.content, end="", flush=True)
            collected_text += delta.content

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

def chat_loop():
    messages = []
    print("Assistant: What can I help you with?")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        continue_tool_execution = True

        while continue_tool_execution:
            # Get response
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=Tools,
                stream=True,
                temperature=0.2
            )
            response_text, tool_calls = process_stream(response)

            if not tool_calls:
                print()
                continue_tool_execution = False

            text_in_response = len(response_text) > 0
            if text_in_response:
                messages.append({"role": "assistant", "content": response_text})

            # Handle tool calls if any
            if tool_calls:
                tool_name = tool_calls[0]["function"]["name"]
                print()
                if not text_in_response:
                    print("Assistant:", end=" ", flush=True)
                print(f"Calling Tool: {tool_name}")
                messages.append({"role": "assistant", "tool_calls": tool_calls})

                # Execute tool calls
                for tool_call in tool_calls:
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

                    elif tool_name == "web_url":
                        result = web_url(arguments["url"])

                    elif tool_name == "image":
                        result = image(arguments["query"], arguments.get("number_of_images", 1))
                        

                    elif tool_name == "video":
                        result = video(arguments["query"], arguments.get("number_of_videos", 1))
                        
                    elif tool_name == "yt_url":
                        result = yt_url(arguments["url"])
                    
                    messages.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call["id"]
                        })

                # Continue checking for more tool calls after tool execution
                continue_tool_execution = True
            else:
                continue_tool_execution = False

if __name__ == "__main__":
    chat_loop()