import os
import uuid
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_from_directory
from openai import OpenAI
from utilities.utilities import system_message

# Tool imports
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

# --- Flask App Setup ---
app = Flask(__name__)
app.static_folder = "templates"

# --- OpenAI Client Setup ---
def get_openai_client():
    return OpenAI(
        base_url=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
        api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio")
    )

MODEL = os.getenv("LMSTUDIO_MODEL", "qwen3-8b")

# --- Tool Definitions ---
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
            "description": f"Perform a quick simple web search for relevant realtime information.",
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
            "description": "Perform a deep and smart web search for content with detailed summaries of search results",
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

system_message = {"role": "system", "content": system_message.format(current_datetime=datetime.now())}

# --- Conversation Storage ---
CONVERSATIONS_DIR = os.path.expanduser("~/.conversations")
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# --- State Management ---
current_conversation_id = None
chat_messages = [system_message]
interrupt_flag = False

# --- Utility Functions ---
def conversation_file_path(conversation_id):
    return os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")

def save_conversation(rename=True):
    if not current_conversation_id:
        return
    conversation_data = {
        "id": current_conversation_id,
        "last_updated": datetime.now().isoformat(),
        "messages": chat_messages,
        "name": get_conversation_name(chat_messages, rename) if chat_messages else "New Conversation"
    }
    with open(conversation_file_path(current_conversation_id), "w") as f:
        json.dump(conversation_data, f, indent=2)

def load_conversation(conversation_id):
    try:
        with open(conversation_file_path(conversation_id), "r") as f:
            return json.load(f)["messages"]
    except Exception:
        return []

def get_all_conversations():
    conversations = []
    for filename in os.listdir(CONVERSATIONS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CONVERSATIONS_DIR, filename), "r") as f:
                data = json.load(f)
                conversations.append({
                    "id": data["id"],
                    "last_updated": data["last_updated"],
                    "name": data.get("name", "Unnamed Conversation"),
                    "preview": data["messages"][0]["content"] if data["messages"] else "Empty conversation"
                })
    return sorted(conversations, key=lambda x: x["last_updated"], reverse=True)

def get_conversation_name(messages, rename=True):
    messages = [msg for msg in messages if msg["role"] == "user" or msg["role"] == "assistant" and "content" in msg]
    if len(messages) > 4 or not rename:
        try:
            with open(conversation_file_path(current_conversation_id), "r") as f:
                return json.load(f)["name"]
        except Exception:
            print("Error loading conversation name")
            print(Exception)
            return "New Conversation"
    
    conv = str(messages)
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specializing in creating concise conversation titles. "
                        "Create a brief, relevant title (maximum 25 characters) for this conversation "
                        "based on the 1-3 user messages and assistant responses. "
                        "Return only the title, no quotes or extra text."
                        "/no_think" if MODEL[:5] == "qwen3" else ""
                    )
                },
                {"role": "user", "content": conv}
            ],
            temperature=1
        )
        return response.choices[0].message.content.strip()[:50]
    except Exception as e:
        print(f"Error generating conversation name: {e}")
        return "New Conversation"

# --- Flask Routes ---
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/style.css')
def serve_css():
    return send_from_directory('templates', 'style.css')
@app.route('/script.js')
def serve_js():
    return send_from_directory('templates', 'script.js')

@app.route('/chat', methods=['POST'])
def chat():
    global current_conversation_id, chat_messages, interrupt_flag
    user_message = request.json.get('message')
    chat_messages.append({"role": "user", "content": str(user_message)})
    if not current_conversation_id:
        current_conversation_id = str(uuid.uuid4())
    client = get_openai_client()

    def generate_response():
        continue_tool_execution = True
        while continue_tool_execution:
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=chat_messages,
                    tools=Tools,
                    stream=True,
                    temperature=0.7,
                )
                current_message = ""
                tool_calls = []
                for chunk in response:
                    if interrupt_flag:
                        continue_tool_execution = False
                        break
                    delta = chunk.choices[0].delta
                    if delta.content is not None:
                        current_message += delta.content
                        yield f"data: {json.dumps({'type': 'content', 'content': delta.content})}\n\n"
                    elif delta.tool_calls:
                        for tc in delta.tool_calls:
                            if tc.function and tc.function.name == "python":
                                yield f"data: {json.dumps({'type': 'tool-start', 'name': 'coding', 'args': {'code': 'Writing code...'}})}\n\n"
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
                if current_message:
                    chat_messages.append({"role": "assistant", "content": current_message})
                if tool_calls:
                    chat_messages.append({"role": "assistant", "tool_calls": tool_calls})
                    for tool_call in tool_calls:
                        arguments = json.loads(tool_call["function"]["arguments"])
                        tool_name = tool_call["function"]["name"]
                        yield f"data: {json.dumps({'type': 'tool-start', 'name': tool_name, 'args': arguments})}\n\n"
                        # Tool execution
                        if tool_name == "python":
                            result = python(arguments["code"])
                        elif tool_name == "web":
                            result = web(
                                arguments["query"],
                                arguments.get("Key_word", [arguments["query"]]),
                                arguments.get("number_of_websites", 3),
                                arguments.get("number_of_citations", 5)
                            )
                        elif tool_name == "deep_search":
                            result = deep_search(
                                arguments["query"],
                                arguments["prompt"],
                                arguments.get("number_of_results", 5),
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
                            result = {"error": "Unknown tool"}
                        chat_messages.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call["id"]
                        })
                        yield f"data: {json.dumps({'type': 'tool', 'name': tool_name, 'content': result, 'args': arguments})}\n\n"
                    continue_tool_execution = True
                else:
                    continue_tool_execution = False
            except Exception as e:
                print(f"Error in generate_response: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                continue_tool_execution = False
        yield "data: [DONE]\n\n"
        save_conversation()

    return Response(stream_with_context(generate_response()), mimetype='text/event-stream')

@app.route('/conversations', methods=['GET'])
def list_conversations():
    return jsonify(get_all_conversations())

@app.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    global current_conversation_id, chat_messages
    current_conversation_id = conversation_id
    chat_messages = load_conversation(conversation_id)
    return jsonify({"status": "success", "messages": chat_messages})

@app.route('/new', methods=['POST'])
def new_conversation():
    global current_conversation_id, chat_messages
    current_conversation_id = str(uuid.uuid4())
    chat_messages = [system_message]
    return jsonify({
        "status": "success",
        "conversation_id": current_conversation_id,
        "name": "New Conversation"
    })

@app.route('/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    try:
        file_path = conversation_file_path(conversation_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            global current_conversation_id, chat_messages
            if current_conversation_id == conversation_id:
                current_conversation_id = None
                chat_messages = [system_message]
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Conversation not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/interrupt', methods=['POST'])
def interrupt():
    global interrupt_flag
    interrupt_flag = True
    time.sleep(0.1)
    # Re-initialize OpenAI client to clear state
    interrupt_flag = False
    return jsonify({"status": "success"})

@app.route('/messages', methods=['GET'])
def get_messages():
    formatted_messages = []
    current_tool_results = []
    current_tool_args = {}
    for msg in chat_messages:
        if msg["role"] == "user":
            formatted_messages.append({
                "isUser": True,
                "content": msg["content"]
            })
        elif msg["role"] == "assistant":
            if "tool_calls" in msg:
                current_tool_results = msg["tool_calls"]
                current_tool_args = {
                    tc["id"]: json.loads(tc["function"]["arguments"])
                    for tc in msg["tool_calls"]
                }
            formatted_messages.append({
                "isUser": False,
                "content": msg.get("content", ""),
                "tool_calls": current_tool_results
            })
        elif msg["role"] == "tool":
            if formatted_messages and not formatted_messages[-1]["isUser"]:
                if "tool_results" not in formatted_messages[-1]:
                    formatted_messages[-1]["tool_results"] = []
                tool_call = next((tc for tc in current_tool_results
                                  if tc["id"] == msg["tool_call_id"]), None)
                if tool_call:
                    tool_name = tool_call["function"]["name"]
                    try:
                        content = eval(msg["content"])
                    except Exception:
                        content = msg["content"]
                    formatted_messages[-1]["tool_results"].append({
                        "name": tool_name,
                        "content": content,
                        "args": current_tool_args.get(msg["tool_call_id"], {})
                    })
    return jsonify(formatted_messages)

@app.route('/delete-last', methods=['POST'])
def delete_last_message():
    global chat_messages
    if len(chat_messages) >= 2:
        last_user_index = next((i for i in range(len(chat_messages) - 1, -1, -1)
                                if chat_messages[i]["role"] == "user"), None)
        if last_user_index is not None:
            chat_messages = chat_messages[:last_user_index]
            save_conversation(rename=False)
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No messages to delete"}), 400

@app.route('/regenerate', methods=['POST'])
def regenerate_response():
    global chat_messages
    if len(chat_messages) >= 1:
        last_user_message = None
        messages_to_remove = 0
        for msg in reversed(chat_messages):
            messages_to_remove += 1
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        if last_user_message:
            chat_messages = chat_messages[:-messages_to_remove]
            save_conversation(rename=False)
            return jsonify({"status": "success", "message": last_user_message})
    return jsonify({"status": "error", "message": "No message to regenerate"}), 400

if __name__ == '__main__':
    app.run(debug=True)