# LLMs Tool Calls Using LM Studio Server
**Give the LLM the ability to:**
* Write and run python code
* Fetch introduction from Wikipedia
* Search websites for relevant Information (Thanks to [tankibaj](https://github.com/tankibaj/azure-openai-function-calling/tree/main))
* Open URL for websites and get information
* Search Youtube for videos
* Open Youtube URL and get Information
* Search Images and get URL and Thumbnails
* Simple Chat UI with basic chat functions and Chat history

<img src="https://github.com/user-attachments/assets/27387bb0-dedd-4905-9faf-5157887d7a30" alt="Screenshot 2025-01-13 194654" width="400"/>
<img src="https://github.com/user-attachments/assets/26d6e05b-bcbf-4ac4-991c-ab32410bfa82" alt="Screenshot 2025-01-13 194115" width="400"/>
<img src="https://github.com/user-attachments/assets/b96ae1cb-a2cc-4699-bc44-e7bbf798000d" alt="Screenshot 2025-01-13 194110" width="400"/>
<img src="https://github.com/user-attachments/assets/39fde852-df06-43c7-b759-17da8711af0d" alt="Screenshot 2025-01-13 194104" width="400"/>
<img src="https://github.com/user-attachments/assets/1bdf82d0-33a2-4f53-b847-07fac2ab73d4" alt="Screenshot 2025-01-13 194057" width="400"/>
<img src="https://github.com/user-attachments/assets/5ba6af6d-86fa-4712-8838-cc64523b6dfb" alt="Screenshot 2025-01-13 194050" width="400"/>

# Flask Chat Application Analysis

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

# Here's how to set up your server:
## Requirments
- [Install LM Studio](https://lmstudio.ai/)
- [Recommended model Qwen2.5 7B](https://huggingface.co/lmstudio-community/Qwen2.5-7B-Instruct-GGUF)

1. install Python

2. install required libraries using pip
```bash
pip install numpy pandas sympy flask openai duckduckgo_search pytubefix youtube_transcript_api waitress
```

3. Environment Variables:
```bash
set FLASK_ENV=production
set FLASK_DEBUG=0
```

4. To run the server:
```bash
python server.py
```
OR double-click the batch file ***serverstart.bat*** to run the server.
