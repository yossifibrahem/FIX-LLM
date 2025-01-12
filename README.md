# LLMs Tool Calls Using LM Studio Server
* Write and run python code
* Fetch introduction from Wikipedia
* Search websites for relevant Information
* Open URL for websites and get information
* Search Youtube for videos
* Open Youtube URL and get Information
* Search Images and get URL and Thumbnails
* Simple Chat UI with basic chat functions and Chat history

<img src="https://github.com/user-attachments/assets/1b6e3afe-c594-4f74-a29a-017c216bb992" alt="Screenshot 2025-01-12 073601" width="400"/>
<img src="https://github.com/user-attachments/assets/84dcb994-78fb-4a1a-bab8-5c5f8ab7bda9" alt="Screenshot 2025-01-12 073433" width="400"/>
<img src="https://github.com/user-attachments/assets/da741804-63e1-4177-8c7a-9009609d9ba9" alt="Screenshot 2025-01-12 071140" width="400"/>
<img src="https://github.com/user-attachments/assets/98c1fba3-72d6-4793-963b-4cb2f483dd71" alt="Screenshot 2025-01-12 072949" width="400"/>
<img src="https://github.com/user-attachments/assets/feab74bc-2380-443b-9a4d-0062dd6454eb" alt="Screenshot 2025-01-12 072154" width="400"/>

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

```bash
pip install numpy pandas sympy flask openai duckduckgo_search pytubefix youtube_transcript_api
```

1. First, install Waitress:
```bash
pip install waitress
```

2. Environment Variables:
```bash
set FLASK_ENV=production
set FLASK_DEBUG=0
```

3. To run the server:
```bash
python server.py
```

4. Create a batch file (*serverstart.bat*): (optional)
double-click the batch file to run the server.
