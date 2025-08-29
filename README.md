# LLM Tool Calling Web Application 🤖💬

## Overview
This is a web application that enables a Large Language Model (LLM) to interact with multiple tools and perform tasks using function calling. Built with Flask and with LM Studio server, this application provides an interactive chat experience with multi-tool support.

## 🌟 Key Features

### Multi-Tool Integration
- 🐍 **Python Code Execution**: Run and analyze Python code directly in the chat
- 🌐 **Web Search**: Perform real-time web searches and extract citations
- 📚 **Wikipedia Lookup**: Instantly retrieve Wikipedia article introductions
- 🖼️ **Image Search**: Find and display images related to your queries
- 🎥 **YouTube Search**: Search and retrieve YouTube video information
- 🔗 **Web Scraping**: Extract content from specific websites
- 🔍 **Deep Search**: Perform a smart deep web search to extract most Information

### Advanced Conversation Management
- 💬 **Persistent Conversations**: Save and load chat histories
- ♻️ **Conversation Regeneration**: Easily regenerate or delete last messages
- 🏷️ **Automatic Conversation Naming**: Smart, context-aware conversation titles
- 📜 **Conversation Listing**: Browse and manage your chat history

### User Experience
- 🎨 **Responsive Design**: Clean, modern UI with Tailwind CSS
- </> **Code Highlighting**: Syntax highlighting with Prism.js
- 📊 **Markdown & Math Support**: Render markdown and mathematical equations
- 🌈 **Tool Results Visualization**: Interactive, collapsible tool result sections

## 🖥️ Screenshots

<img width="400" alt="python" src="https://github.com/user-attachments/assets/01762e23-575d-454c-8533-a1d10dc4c0cb" />
<img width="400" alt="web and image" src="https://github.com/user-attachments/assets/e1772634-064e-4592-9ae6-757281b45cd4" />
<img width="400" alt="YT" src="https://github.com/user-attachments/assets/cfa6d63e-fea8-4c2e-b5de-e16abfdbda24" />
<img width="400" alt="urls" src="https://github.com/user-attachments/assets/322db552-7f1a-4678-9039-46420f8e87ab" />
<img width="400" alt="wikipidia" src="https://github.com/user-attachments/assets/be587034-a76e-4785-bcb8-ab9573b5aa35" />
<img width="400" alt="history" src="https://github.com/user-attachments/assets/8cd972d2-b816-4588-8826-dcb82f1aa8ba" />

## 🔧 Prerequisites
- Python 3.8+
- [LM Studio](https://lmstudio.ai/)
- Recommended Model: [Qwen2.5 7B Instruct](https://huggingface.co/lmstudio-community/Qwen2.5-7B-Instruct-GGUF)

## 📦 Installation
Ensure LM Studio is running on your machine with the server running.
### Clone the Repository

- Download the zip file for the repo by clicking [here](https://github.com/yossifibrahem/FIX-LLM/archive/refs/tags/v0.1.1.zip)
- unzip the file
- move to the project directory
```bash
cd LLM-Tool-Calling-Web-Application
```

## 🚀 Running the Application

### 🐳 Option 1: Using Docker
<details>
<summary>Click here</summary>
  
1. Install [Docker](https://www.docker.com/) on your machine (if you haven't already)

2. Build the docker container with 
```bash
docker build -t llm_tool_app .
```

3. If on **Windows/MacOS** run

```bash
docker run --name Tools-UI -p 8080:8080 --add-host=host.docker.internal:host-gateway -e LMSTUDIO_BASE_URL="http://host.docker.internal:1234/v1" -e LMSTUDIO_API_KEY="lm-studio" -e LMSTUDIO_MODEL="lmstudio-community/qwen2.5-7b-instruct" llm_tool_app
```

Otherwise if you are on **Linux** run:

```bash
docker run --name Tools-UI -p 8080:8080 -e LMSTUDIO_BASE_URL="http://host.docker.internal:1234/v1" -e LMSTUDIO_API_KEY="lm-studio" -e LMSTUDIO_MODEL="lmstudio-community/qwen2.5-7b-instruct" llm_tool_app
```
If your LMSTUDIO_BASE_URL, LMSTUDIO_API_KEY and/or LMSTUDIO_MODEL values are different on your setup, change that in the docker run command.
</details>

### 🐍 Option 2: Using Python
<details>
<summary>Click here</summary>
  
1. Install Dependencies

```bash
pip install -r requirements.txt
```

2. post-installation setup

**Setup crawl4ai**
```bash
# Run post-installation setup
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```

**Set Environment Variables**
```bash
# For Windows
set FLASK_ENV=production
set FLASK_DEBUG=0

# For Unix/MacOS
export FLASK_ENV=production
export FLASK_DEBUG=0
```

**(optional)** If you need to change the server host, port, LM Studio URL, API key, or model, set the following environment variables to the desired values like so:

```bash
# For Windows
set LMSTUDIO_BASE_URL=YOUR_VALUE_HERE
set LMSTUDIO_API_KEY=YOUR_VALUE_HERE
set LMSTUDIO_MODEL=YOUR_VALUE_HERE

# For Unix/MacOS
export LMSTUDIO_BASE_URL=YOUR_VALUE_HERE
export LMSTUDIO_API_KEY=YOUR_VALUE_HERE
export LMSTUDIO_MODEL=YOUR_VALUE_HERE
```

Run the server using
```bash
python server.py
```
or Double-click `serverstart.bat`
</details>

## How to use the MCP servers
Add these MCP server config to claude desktop config file, LM Studio or any other client
```json
{
    "mcpServers": {
        "Web": {
            "command": "python",
            "args": [
                "path/to/FIX-LLM/mcp_web.py"
            ]
        },
        "code-interpreter": {
            "command": "python",
            "args": [
                "path/to/FIX-LLM/mcp_python.py"
            ]
        }
    }  
}
```
### Access the Application
Open your browser and navigate to http://localhost:8080

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [LM Studio](https://lmstudio.ai/)
- Open-source libraries and tools used in this project
- [crawl4ai](https://github.com/unclecode/crawl4ai)
- [azure-openai-function-calling](https://github.com/tankibaj/azure-openai-function-calling/tree/main)

## 📞 Support
For issues or questions, please open a GitHub issue or contact the maintainer.

*This README is written by Anthropic's Claude*
