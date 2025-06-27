import subprocess
import shlex
import os
import sys
from typing import Dict, List, Optional, Union
import json
import time

class TerminalExecutor:
    """
    A secure terminal command executor designed for LLM function calling.
    Provides controlled command execution with proper error handling and security measures.
    """
    
    def __init__(self, 
                 timeout: int = 30,
                 max_output_size: int = 10000,
                 allowed_commands: Optional[List[str]] = None,
                 blocked_commands: Optional[List[str]] = None,
                 working_directory: Optional[str] = None):
        """
        Initialize the terminal executor.
        
        Args:
            timeout: Maximum execution time in seconds
            max_output_size: Maximum output size in characters
            allowed_commands: List of allowed command prefixes (whitelist)
            blocked_commands: List of blocked command prefixes (blacklist)
            working_directory: Working directory for command execution
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.allowed_commands = allowed_commands or []
        self.blocked_commands = blocked_commands or [
            'rm -rf', 'sudo rm', 'del /f', 'format', 'fdisk',
            'mkfs', 'dd if=', 'shutdown', 'reboot', 'halt',
            'poweroff', 'init 0', 'init 6', 'killall', 'pkill -9'
        ]
        self.working_directory = working_directory or os.getcwd()
    
    def execute_command(self, command: str, 
                       capture_output: bool = True,
                       shell: bool = None,
                       env: Optional[Dict[str, str]] = None) -> Dict[str, Union[str, int, bool]]:
        """
        Execute a terminal command and return the result.
        
        Args:
            command: The command to execute
            capture_output: Whether to capture stdout and stderr
            shell: Whether to use shell execution
            env: Environment variables to set
            
        Returns:
            Dictionary containing execution results
        """
        try:
            # Security check
            if not self._is_command_allowed(command):
                return {
                    'success': False,
                    'stdout': '',
                    'stderr': f'Command blocked for security reasons: {command}',
                    'return_code': -1,
                    'execution_time': 0
                }
            
            # Auto-detect if shell is needed
            if shell is None:
                shell = self._needs_shell(command)
            
            # Prepare command
            if shell:
                cmd = command
            else:
                cmd = shlex.split(command)
            
            # Prepare environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            start_time = time.time()
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout,
                shell=shell,
                cwd=self.working_directory,
                env=exec_env
            )
            
            execution_time = time.time() - start_time
            
            # Truncate output if too large
            stdout = result.stdout or ''
            stderr = result.stderr or ''
            
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + '\n... (output truncated)'
            
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + '\n... (error output truncated)'
            
            return {
                'success': result.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'return_code': result.returncode,
                'execution_time': round(execution_time, 3)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {self.timeout} seconds',
                'return_code': -1,
                'execution_time': self.timeout
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'stdout': e.stdout or '',
                'stderr': e.stderr or str(e),
                'return_code': e.returncode,
                'execution_time': 0
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'return_code': -1,
                'execution_time': 0
            }
    
    def _needs_shell(self, command: str) -> bool:
        """Determine if a command needs shell execution."""
        # Commands that are shell built-ins or need shell features
        shell_commands = [
            'echo', 'cd', 'dir', 'type', 'copy', 'move', 'del', 'md', 'rd',
            'set', 'if', 'for', 'while', 'export', 'alias', 'history',
            'source', 'which', 'whereis'
        ]
        
        # Check for shell operators
        shell_operators = ['|', '>', '<', '>>', '&&', '||', ';', '&']
        
        command_lower = command.lower().strip()
        first_word = command_lower.split()[0] if command_lower.split() else ''
        
        # Check if first word is a shell built-in
        if first_word in shell_commands:
            return True
        
        # Check for shell operators
        for operator in shell_operators:
            if operator in command:
                return True
        
        # On Windows, check for .bat, .cmd files or if it contains quotes with spaces
        if sys.platform.startswith('win'):
            if any(ext in command_lower for ext in ['.bat', '.cmd']):
                return True
            # Complex quoting often needs shell
            if '"' in command and ' ' in command:
                return True
        
        return False
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed based on security rules."""
        command_lower = command.lower().strip()
        
        # Check blocked commands
        for blocked in self.blocked_commands:
            if blocked.lower() in command_lower:
                return False
        
        # Check allowed commands (if whitelist is defined)
        if self.allowed_commands:
            for allowed in self.allowed_commands:
                if command_lower.startswith(allowed.lower()):
                    return True
            return False
        
        return True
    
    def get_current_directory(self) -> str:
        """Get the current working directory."""
        return self.working_directory
    
    def change_directory(self, path: str) -> Dict[str, Union[str, bool]]:
        """Change the working directory."""
        try:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                self.working_directory = abs_path
                return {
                    'success': True,
                    'message': f'Changed directory to: {abs_path}',
                    'current_directory': abs_path
                }
            else:
                return {
                    'success': False,
                    'message': f'Directory does not exist: {path}',
                    'current_directory': self.working_directory
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error changing directory: {str(e)}',
                'current_directory': self.working_directory
            }


# Function calling interface functions
def execute_terminal_command(command: str, 
                           timeout: int = 30,
                           working_directory: Optional[str] = None,
                           shell: bool = None) -> str:
    """
    Execute a terminal command - designed for LLM function calling.
    
    Args:
        command: The terminal command to execute
        timeout: Maximum execution time in seconds
        working_directory: Directory to execute the command in
        shell: Whether to use shell (auto-detected if None)
        
    Returns:
        JSON string containing the execution result
    """
    executor = TerminalExecutor(
        timeout=timeout,
        working_directory=working_directory
    )
    
    result = executor.execute_command(command, shell=shell)
    return json.dumps(result, indent=2)


# # Example usage and testing
# if __name__ == "__main__":
#     # Example 1: Basic usage
#     print("=== Basic Command Execution ===")
#     result = execute_terminal_command('echo "Hello, World!"')
#     print(result)
    
#     # Example 2: Using the class directly
#     print("\n=== Class Usage Example ===")
#     executor = TerminalExecutor(timeout=10)
    
#     # Execute multiple commands
#     if sys.platform.startswith('win'):
#         commands = ["cd", "dir", 'echo "Python version:"', "python --version"]
#     else:
#         commands = ["pwd", "ls", "echo 'Python version:'", "python --version"]
    
#     for cmd in commands:
#         print(f"\nExecuting: {cmd}")
#         result = executor.execute_command(cmd)
#         print(f"Success: {result['success']}")
#         print(f"Output: {result['stdout']}")
#         if result['stderr']:
#             print(f"Error: {result['stderr']}")