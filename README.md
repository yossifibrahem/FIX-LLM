**LLMs Tool Calls Using LM Studio Server**
* Write and run python code
* Fetch introduction from Wikipedia
* Search websites for relevant Information
* Open URL for websites and get information
* Search Youtube for videos
* Open Youtube URL and get Information
* Search Images and get URL and Thumbnails
* Simple Chat UI with basic chat functions and Chat history

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

# Here's how to set up your production server:

1. First, install Waitress:
```bash
pip install waitress
```

2. To run the server:
```bash
python server.py
```

3. Environment Variables:
```bash
set FLASK_ENV=production
set FLASK_DEBUG=0
```
