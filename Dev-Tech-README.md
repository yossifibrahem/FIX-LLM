# LM Studio Chat Application

## Overview

This is a powerful, multi-functional chat application that leverages local language models to provide advanced conversational capabilities with integrated tool calling. Built using Flask and OpenAI's function calling API, the application allows users to interact with an AI assistant that can perform a wide range of tasks through specialized tools.

## Core Components

### 1. Application Setup
- Flask application with static folder set to "templates"
- Uses OpenAI client configured to connect to a local LM Studio instance (port 1234)
- Uses Qwen 2.5 7B Instruct model

### 2. Available Tools
The application provides 7 core tools:
- `python`: Executes Python code securely
- `web`: Performs web searches and extracts citations
- `wiki`: Searches Wikipedia articles
- `web_url`: Scrapes content from specific URLs
- `image`: Searches for images
- `video`: Searches YouTube videos
- `yt_url`: Retrieves YouTube video metadata

### 3. Conversation Management
- Conversations are stored in a "conversations" directory as JSON files
- Each conversation has:
  - Unique UUID
  - Last updated timestamp
  - Message history
  - Auto-generated name based on content

### 4. Key Routes
- `/`: Home page
- `/chat`: Main chat endpoint (POST)
- `/conversations`: List all conversations (GET)
- `/conversation/<id>`: Get/Delete specific conversation (GET/DELETE)
- `/new`: Create new conversation (POST)
- `/interrupt`: Stop current processing (POST)
- `/messages`: Get formatted message history (GET)
- `/delete-last`: Remove last message (POST)
- `/regenerate`: Regenerate last response (POST)

### 5. Chat Processing Features
- Streaming response generation
- Tool execution pipeline
- Message history tracking
- Error handling
- Conversation auto-saving
- Message formatting for frontend display

## Notable Implementation Details

### Tool Execution Flow
1. Receives user message
2. Streams response from model
3. Detects tool calls in response
4. Executes tools as needed
5. Streams results back to client
6. Continues conversation if more tool calls needed

### Safety Features
- Secure Python code execution (via separate executor)
- Error handling throughout
- Development server warning
- Interrupt capability for long-running operations

### Data Management
- Persistent storage of conversations
- Automatic conversation naming
- Message history formatting
- Tool results tracking

## Prerequisites

### Software Requirements
- Python 3.8+
- LM Studio
- pip (Python package manager)

### Recommended Model
- [Qwen2.5 7B Instruct GGUF](https://huggingface.co/lmstudio-community/Qwen2.5-7B-Instruct-GGUF)

## Installation

1. Clone the repository
```bash
git clone https://github.com/yossifibrahem/LLM-Tool-Calling-Web-Application.git
cd LLM-Tool-Calling-Web-Application
```

2. Install required Python libraries
```bash
pip install numpy pandas sympy flask openai duckduckgo_search pytubefix youtube_transcript_api waitress
```

3. Set Environment Variables
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
```

## Running the Application

### Development Server
```bash
python app.py
```

The application will be accessible at `http://localhost:5000`

## Configuration

- Modify the OpenAI client configuration in `app.py` to point to your local LM Studio server
- Adjust model selection as needed
- Customize tool configurations in the `Tools` list

## Technology Stack

- ## Tech Stack
- **Model**: Qwen2.5 7B Instruct (via LM Studio)
- **Backend**: Flask, Python
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Libraries**: 
  - OpenAI API
  - Marked.js
  - Prism.js
  - KaTeX

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [LM Studio](https://lmstudio.ai/) for providing local inference capabilities
- [tankibaj](https://github.com/tankibaj/azure-openai-function-calling/tree/main) for web function
- Open-source libraries used in the project

## Disclaimer

This project is a demonstration of local AI tool calling and should be used responsibly.

*This README is written Anthropic's Claude*
