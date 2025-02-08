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

### 1. Clone the Repository
```bash
git clone https://github.com/yossifibrahem/LLM-Tool-Calling-Web-Application.git
cd LLM-Tool-Calling-Web-Application
```

### 2. Install Dependencies
```bash
pip install numpy pandas sympy flask openai duckduckgo_search pytubefix youtube_transcript_api waitress crawl4ai
```

### 3. Set Environment Variables
```bash
# For Windows
set FLASK_ENV=production
set FLASK_DEBUG=0

# For Unix/MacOS
export FLASK_ENV=production
export FLASK_DEBUG=0
```

### post-installation setup for crawl4ai
```bash
# Run post-installation setup
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```

## 🚀 Running the Application

### Option 1: Using Python
```bash
python server.py
```

### Option 2: Using Batch File (Windows)
Double-click `serverstart.bat`

### Access the Application
Open your browser and navigate to `http://localhost:8080`

## 🛠️ Tools Supported

1. **Python Execution**
   - Execute Python code
   - Perform mathematical computations
   - Automate tasks

2. **Web Search**
   - Find relevant websites
   - Extract citations
   - Configurable search depth

3. **Wikipedia Search**
   - Fetch article introductions
   - Quick knowledge retrieval

4. **Web Scraping**
   - Extract content from specific URLs
   - Retrieve webpage information

5. **YouTube Integration**
   - Search videos
   - Retrieve video metadata
   - Get video transcriptions

6. **Image Search**
   - Find and display images
   - Configurable result count

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements
- [LM Studio](https://lmstudio.ai/)
- Open-source libraries and tools used in this project
- [crawl4ai](https://github.com/unclecode/crawl4ai)
- [azure-openai-function-calling](https://github.com/tankibaj/azure-openai-function-calling/tree/main)

## 📞 Support
For issues or questions, please open a GitHub issue or contact the maintainer.

*This README is written Anthropic's Claude*
