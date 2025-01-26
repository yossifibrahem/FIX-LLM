# LM Studio Chat Application

## Overview

This is a powerful, multi-functional chat application that leverages local language models to provide advanced conversational capabilities with integrated tool calling. Built using Flask and OpenAI's function calling API, the application allows users to interact with an AI assistant that can perform a wide range of tasks through specialized tools.

## Key Features

### Integrated Tools
The application provides seven powerful tools for enhanced interaction:

1. **Python Code Execution**: Run and analyze Python code directly within the chat
2. **Web Search**: Perform live web searches and extract relevant citations
3. **Wikipedia Search**: Quickly retrieve article introductions
4. **Website Scraping**: Extract content from specific web URLs
5. **Image Search**: Find and display relevant images
6. **YouTube Video Search**: Search and retrieve video information
7. **YouTube Video Metadata**: Get detailed information about specific videos

### Additional Capabilities
- Streaming response generation
- Conversation history management
- Tool call interruption
- Markdown and math rendering
- Code syntax highlighting
- Responsive web interface

## Screenshots

<img src="https://github.com/user-attachments/assets/5ba6af6d-86fa-4712-8838-cc64523b6dfb" alt="Screenshot 2025-01-13 194050" width="300"/>
<img src="https://github.com/user-attachments/assets/77ad52ee-5ac2-41e9-8afb-040a73c34c0d" alt="Screenshot 2025-01-13 194115" width="300"/>
<img src="https://github.com/user-attachments/assets/eb73d09b-5ee1-4145-9421-ec31743f15fa" alt="Screenshot 2025-01-13 194057" width="300"/>
<img src="https://github.com/user-attachments/assets/b96ae1cb-a2cc-4699-bc44-e7bbf798000d" alt="Screenshot 2025-01-13 194110" width="300"/>
<img src="https://github.com/user-attachments/assets/39fde852-df06-43c7-b759-17da8711af0d" alt="Screenshot 2025-01-13 194104" width="300"/>
<img src="https://github.com/user-attachments/assets/27387bb0-dedd-4905-9faf-5157887d7a30" alt="Screenshot 2025-01-13 194654" width="300"/>

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
git clone https://github.com/yossifibrahem/Tools_GUI.git
cd Tools_GUI
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

### Production Server
```bash
python server.py
```

The application will be accessible at `http://localhost:8080`

## Configuration

- Modify the OpenAI client configuration in `app.py` to point to your local LM Studio server
- Adjust model selection as needed
- Customize tool configurations in the `Tools` list

## Technology Stack

- **Backend**: Flask
- **Frontend**: HTML5, Tailwind CSS
- **Language Model**: LM Studio (local inference)
- **Additional Libraries**: 
  - Marked.js (Markdown rendering)
  - Prism.js (Code highlighting)
  - KaTeX (Math rendering)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [LM Studio](https://lmstudio.ai/) for providing local inference capabilities
- Open-source libraries used in the project

## Disclaimer

This project is a demonstration of local AI tool calling and should be used responsibly.
