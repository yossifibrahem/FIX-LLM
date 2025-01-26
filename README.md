# LLM Tool Calling Web Application 🤖💬

## Overview
This is a powerful, flexible web application that enables an Large Language Model (LLM) to interact with multiple tools and perform complex tasks using function calling. Built with Flask and integrated with LM Studio, this application provides a rich, interactive chat experience with multi-tool support.

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
<img src="https://github.com/user-attachments/assets/5ba6af6d-86fa-4712-8838-cc64523b6dfb" alt="Screenshot 2025-01-13 194050" width="300"/>
<img src="https://github.com/user-attachments/assets/77ad52ee-5ac2-41e9-8afb-040a73c34c0d" alt="Screenshot 2025-01-13 194115" width="300"/>
<img src="https://github.com/user-attachments/assets/eb73d09b-5ee1-4145-9421-ec31743f15fa" alt="Screenshot 2025-01-13 194057" width="300"/>
<img src="https://github.com/user-attachments/assets/b96ae1cb-a2cc-4699-bc44-e7bbf798000d" alt="Screenshot 2025-01-13 194110" width="300"/>
<img src="https://github.com/user-attachments/assets/39fde852-df06-43c7-b759-17da8711af0d" alt="Screenshot 2025-01-13 194104" width="300"/>
<img src="https://github.com/user-attachments/assets/27387bb0-dedd-4905-9faf-5157887d7a30" alt="Screenshot 2025-01-13 194654" width="300"/>

## 🔧 Prerequisites
- Python 3.8+
- [LM Studio](https://lmstudio.ai/)
- Recommended Model: [Qwen2.5 7B Instruct](https://huggingface.co/lmstudio-community/Qwen2.5-7B-Instruct-GGUF)

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yossifibrahem/Tools_GUI.git
cd Tools_GUI
```

### 2. Install Dependencies
```bash
pip install numpy pandas sympy flask openai duckduckgo_search pytubefix youtube_transcript_api waitress
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

## 📞 Support
For issues or questions, please open a GitHub issue or contact the maintainer.

*This README is written Anthropic's Claude*