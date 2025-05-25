import sys
import threading
import itertools
import time
import shutil

system_message = """
You are an AI assistant with access to powerful tools that help you perform various tasks efficiently. Your purpose is to assist users with their questions and requests through conversation.

## Core Identity and Capabilities

- You are helpful, respectful, and informative.
- You can access real-time information using various tools to provide the most current and accurate responses.
- Your responses should be concise but thorough, focusing on directly addressing the user's needs.
- Current date and time: {current_datetime}

## Response Guidelines

- Be truthful and acknowledge when you don't know something.
- When using tools, explain what you're doing and why.
- Format your responses for readability using appropriate formatting.
- If a question is ambiguous, ask for clarification before using tools.
- When providing code, explain how it works.
- When searching the web or other sources, cite your sources appropriately.

## Ethical Guidelines

- Do not generate harmful, illegal, unethical or deceptive content.
- Respect user privacy and confidentiality.
- Do not execute code that could be harmful or malicious.
- Avoid making definitive claims in areas requiring professional expertise (medical, legal, financial).
- If asked to perform tasks beyond your capabilities, explain your limitations clearly.

## Interaction Style

- Maintain a conversational, friendly tone.
- Be concise but thorough in your responses.
- Use plain language when possible, but technical language when appropriate.
- Adapt your communication style to the user's needs and preferences.
- Use examples to illustrate complex concepts.

Remember that your primary goal is to provide valuable assistance to the user through accurate information and helpful tools.
"""

class LoadingAnimation:
    """Display a custom animation while processing."""
    def __init__(self, message):
        self._running = False
        self._thread = None
        self._frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._message = message

    def start(self):
        """Start the animation."""
        self._running = True
        self._thread = threading.Thread(target=self._animate)
        self._thread.start()

    def stop(self):
        """Stop the animation."""
        self._running = False
        if self._thread:
            self._thread.join()
        # Clear the animation line
        sys.stdout.write("\r" + " " * 50 + "\r")  # Increased clearing space for longer messages
        sys.stdout.flush()

    def _animate(self):
        """Animation loop."""
        for frame in itertools.cycle(self._frames):
            if not self._running:
                break
            sys.stdout.write(f"\r{self._message} {frame}")
            sys.stdout.flush()
            time.sleep(0.1)


def get_terminal_width() -> int:
    """Get the current terminal width."""
    width, _ = shutil.get_terminal_size()
    return width

def create_centered_box(text: str, header: str = '', padding: int = 2, center_align: bool = False) -> str:
    """
    Create a centered box with dynamic width and centered header.
    
    Args:
        text (str): The text to be displayed in the box
        header (str): Optional header text to show at top of box
        padding (int): Number of spaces for padding on each side
        center_align (bool): Whether to center the text (True) or left-align it (False)
    
    Returns:
        str: Formatted box with the text
    """
    # Get terminal width
    width = get_terminal_width()
    
    # Create box characters
    TOP_LEFT = "╭"
    TOP_RIGHT = "╮"
    BOTTOM_LEFT = "╰"
    BOTTOM_RIGHT = "╯"
    HORIZONTAL = "─"
    VERTICAL = "│"
    
    # Calculate content width
    content_width = width - (2 * padding) - 2  # -2 for the vertical borders
    
    # Split text into lines that fit the content width
    lines = []
    for line in text.split('\n'):
        while len(line) > content_width:
            split_point = line[:content_width].rfind(' ')
            if split_point == -1:
                split_point = content_width
            lines.append(line[:split_point])
            line = line[split_point:].strip()
        if line:
            lines.append(line)
    
    # Create the box
    result = []
    
    # Top border with centered header if provided
    if header:
        header_text = f" {header} "
        header_length = len(header_text)
        left_padding = (width - header_length) // 2
        right_padding = width - left_padding - header_length
        top_border = (
            f"{TOP_LEFT}"
            f"{HORIZONTAL * (left_padding - 1)}"
            f"{header_text}"
            f"{HORIZONTAL * (right_padding - 1)}"
            f"{TOP_RIGHT}"
        )
        result.append(top_border)
    else:
        result.append(f"{TOP_LEFT}{HORIZONTAL * (width - 2)}{TOP_RIGHT}")
    
    # Content
    for line in lines:
        if center_align:
            # Center alignment
            padding_left = (content_width - len(line)) // 2
            padding_right = content_width - len(line) - padding_left
            padded_line = " " * padding_left + line + " " * padding_right
        else:
            # Left alignment
            padded_line = line + " " * (content_width - len(line))
        
        result.append(f"{VERTICAL}{' ' * padding}{padded_line}{' ' * padding}{VERTICAL}")
    
    # Bottom border
    result.append(f"{BOTTOM_LEFT}{HORIZONTAL * (width - 2)}{BOTTOM_RIGHT}")
    
    return "\n".join(result)