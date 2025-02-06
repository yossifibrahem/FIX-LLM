from io import StringIO
import os
import traceback
from typing import Dict, Optional, Tuple, Generator
import contextlib
import sys
import json
import threading
import ctypes
import re
import resource
import signal
import ast
from functools import wraps
import numpy as np

Base_Dir = os.path.expanduser("~/.conversations/python")
if not os.path.exists(Base_Dir):
    os.makedirs(Base_Dir)
os.chdir(Base_Dir)

# Memory limit in bytes (default: 100MB)
DEFAULT_MEMORY_LIMIT = 100 * 1024 * 1024
DEFAULT_TIMEOUT = 5

def limit_memory(max_memory):
    """Set memory limit using resource module"""
    try:
        resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
    except ValueError as e:
        print(f"Warning: Could not set memory limit: {e}")

class MemoryError(Exception):
    """Custom exception for memory limit violations"""
    pass

class SecurityError(Exception):
    """Custom exception for security violations"""
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

class ThreadWithException(threading.Thread):
    """A Thread subclass that can be stopped by forcing an exception."""
    
    def _get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                self._thread_id = id
                return id

    def raise_exception(self):
        thread_id = self._get_id()
        if thread_id is not None:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(thread_id),
                ctypes.py_object(KeyboardInterrupt)
            )
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    None
                )
                raise RuntimeError("Failed to safely stop thread execution")

class PythonExecutor:
    """
    A tool for safely executing Python code with memory and timeout limits.
    """
    
    def __init__(self, memory_limit: int = DEFAULT_MEMORY_LIMIT):
        self.global_state: Dict = {}
        self.execution_result = None
        self.memory_limit = memory_limit
        
        # Expanded blocked imports for better security
        self.blocked_imports = [
            "os", "sys", "subprocess", "shutil", "socket", "requests",
            "urllib", "ftplib", "telnetlib", "poplib", "smtplib",
            "ctypes", "multiprocessing", "threading"
        ]
        
        # Expanded blocked keywords for better security
        self.blocked_keywords = [
            "exec", "eval", "compile", "open", "file", "os.system",
            "subprocess", "ctypes", "importlib", "input", "__import__",
            "globals", "locals", "dir", "getattr", "setattr"
        ]
        
        # Add unsafe built-in functions
        self.blocked_builtins = [
            "globals", "locals", "dir", "vars", "getattr", "setattr",
            "delattr", "hasattr", "__import__"
        ]

    def _create_safe_globals(self) -> Dict:
        """Create a restricted globals dictionary for safe execution"""
        safe_builtins = dict(__builtins__)
        for func in self.blocked_builtins:
            if func in safe_builtins:
                del safe_builtins[func]
        
        return {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            **self.global_state
        }

    def _check_ast_security(self, tree: ast.AST) -> bool:
        """Analyze AST for potentially unsafe operations"""
        for node in ast.walk(tree):
            # Check for import statements
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = []
                if isinstance(node, ast.Import):
                    names = [n.name for n in node.names]
                else:
                    if node.module in self.blocked_imports:
                        return False
                    names = [f"{node.module}.{n.name}" for n in node.names]
                
                if any(name.split('.')[0] in self.blocked_imports for name in names):
                    return False
            
            # Check for calls to blocked built-ins
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.blocked_keywords:
                        return False
        
        return True

    @contextlib.contextmanager
    def _capture_output(self) -> Generator[Tuple[StringIO, StringIO], None, None]:
        """Capture stdout and stderr"""
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def _is_code_safe(self, code: str) -> bool:
        """Enhanced security check for code safety"""
        try:
            tree = ast.parse(code)
            return self._check_ast_security(tree)
        except SyntaxError:
            return False

    def _execute_code(self, code: str):
        """Execute code with memory limits and store the result"""
        result = {
            'success': False,
            'output': '',
            'error': None,
            'result': None
        }

        if not self._is_code_safe(code):
            result['error'] = "SecurityError: Unsafe code detected - possible security violation"
            self.execution_result = result
            return

        # Set memory limit
        limit_memory(self.memory_limit)
        
        with self._capture_output() as (out, err):
            try:
                # Create restricted globals
                exec_globals = self._create_safe_globals()
                
                # Compile and execute code
                compiled_code = compile(code, '<string>', 'exec')
                exec(compiled_code, exec_globals)
                
                # Update global state with safe values only
                self.global_state.update({
                    k: v for k, v in exec_globals.items()
                    if k not in self.blocked_keywords and not k.startswith('__')
                })
                
                result['output'] = out.getvalue()
                result['success'] = True
                
                # Get last expression result
                lines = [line.strip() for line in re.split(r'[;\n]', code) if line.strip()]
                if lines:
                    try:
                        last_expr = compile(lines[-1], '<string>', 'eval')
                        result['result'] = eval(last_expr, exec_globals)
                    except Exception:
                        pass
                    
            except MemoryError:
                result['error'] = f"MemoryError: Exceeded memory limit of {self.memory_limit/1024/1024:.1f}MB"
            except KeyboardInterrupt:
                result['error'] = 'ExecutionError: Code execution timed out'
            except Exception as e:
                result['error'] = (
                    f"{type(e).__name__}: {str(e)}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
                result['output'] = out.getvalue()

        if not is_json_serializable(result):
            result = make_json_serializable(result)
        self.execution_result = result

    def execute(self, code: str, timeout: Optional[int] = DEFAULT_TIMEOUT) -> Dict:
        """
        Execute Python code with timeout and memory limits.
        
        Args:
            code: String containing Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary containing execution results
        """
        if timeout is None or timeout <= 0:
            timeout = DEFAULT_TIMEOUT
        
        # Set up timeout handler
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            execution_thread = ThreadWithException(target=self._execute_code, args=(code,))
            execution_thread.start()
            execution_thread.join(timeout)
            
            if execution_thread.is_alive():
                execution_thread.raise_exception()
                execution_thread.join()
                return {
                    'success': False,
                    'output': '',
                    'error': f'ExecutionError: Code timed out after {timeout} seconds',
                    'result': None
                }
        finally:
            signal.alarm(0)
            
        return self.execution_result or {
            'success': False,
            'output': '',
            'error': 'ExecutionError: Code execution failed with no result',
            'result': None
        }
    
    def reset_state(self):
        """Clear the stored global state"""
        self.global_state = {}

def execute_python_code(code: str, timeout: int = DEFAULT_TIMEOUT, memory_limit: int = DEFAULT_MEMORY_LIMIT) -> dict:
    """
    Execute Python code with security, memory, and timeout limits.
    
    Args:
        code: String containing the Python code to execute
        timeout: Maximum execution time in seconds (default: 5)
        memory_limit: Maximum memory usage in bytes (default: 100MB)
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if execution was successful
        - output: Captured stdout content
        - error: Error message if execution failed
        - result: Last evaluated expression result
    """
    executor = PythonExecutor(memory_limit=memory_limit)
    return executor.execute(code, timeout)

# Helper functions remain unchanged
def is_json_serializable(data):
    try:
        json.dumps(data)
        return True
    except (TypeError, OverflowError):
        return False

def make_json_serializable(data):
    if isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (set,)):
        return list(data)
    elif isinstance(data, (bytes, bytearray)):
        return data.decode('utf-8')
    elif isinstance(data, (complex,)):
        return [data.real, data.imag]
    elif isinstance(data, (np.generic,)):
        return data.item()
    elif isinstance(data, (dict,)):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [make_json_serializable(item) for item in data]
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    else:
        return str(data)
    
    