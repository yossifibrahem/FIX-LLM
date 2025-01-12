from io import StringIO
import traceback
from typing import Dict, Optional, Tuple, Generator
import contextlib
import sys
import json
import threading
import ctypes
import re

class ThreadWithException(threading.Thread):
    """A Thread subclass that can be stopped by forcing an exception."""
    
    def _get_id(self):
        # Returns the thread ID
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                self._thread_id = id
                return id

    def raise_exception(self):
        """Raises KeyboardInterrupt in the thread to stop it."""
        thread_id = self._get_id()
        if thread_id is not None:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(thread_id),
                ctypes.py_object(KeyboardInterrupt)
            )
            if res > 1:
                # If more than one exception was raised, something went wrong
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    None
                )
                raise RuntimeError("Failed to stop thread")

class PythonExecutor:
    """
    A tool for safely executing Python code and capturing its output.
    Windows-compatible version with timeout support.
    """
    
    def __init__(self):
        self.global_state: Dict = {}
        self.execution_result = None
        self.blocked_imports = ["os", "sys", "subprocess", "shutil"]
        self.blocked_keywords = [
            "exec", "eval", "open", "os.system", "subprocess", "ctypes", "importlib" , "input"
        ]

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
        """Check if the provided code contains unsafe imports or keywords."""
        # Check for blocked imports
        for module in self.blocked_imports:
            if re.search(rf"\bimport\s+{module}\b|\bfrom\s+{module}\b", code):
                return False

        # Check for blocked keywords
        for keyword in self.blocked_keywords:
            if keyword in code:
                return False

        return True

    def _execute_code(self, code: str):
        """Execute code and store the result"""
        result = {
            'success': False,
            'output': '',
            'error': None,
            'result': None
        }

        # Security check
        if not self._is_code_safe(code):
            result['error'] = "SecurityError: Unsafe code detected"
            self.execution_result = result
            return
        
        with self._capture_output() as (out, err):
            try:
                # Execute the code within the global state
                exec_globals = {
                    '__builtins__': __builtins__,
                    **self.global_state
                }
                
                # Try to compile the code first to catch syntax errors
                compiled_code = compile(code, '<string>', 'exec')
                
                # Execute the code
                exec(compiled_code, exec_globals)
                
                # Update global state
                self.global_state.update(exec_globals)
                
                # Get output
                result['output'] = out.getvalue()
                result['success'] = True
                
                # Try to get the last expression result
                # Split by both newlines and semicolons
                lines = [line.strip() for line in re.split(r'[;\n]', code) if line.strip()]
                if lines:
                    try:
                        last_expr = compile(lines[-1], '<string>', 'eval')
                        result['result'] = eval(last_expr, exec_globals)
                    except:
                        pass
                    
            except KeyboardInterrupt:
                result['error'] = 'Execution timed out'
                result['output'] = out.getvalue()
            except Exception as e:
                result['error'] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                result['output'] = out.getvalue()

        if not is_json_serializable(result):
            result = make_json_serializable(result)
        self.execution_result = result
            
    def execute(self, code: str, timeout: Optional[int] = 10) -> Dict:
        """
        Execute Python code with timeout and return the results.
        
        Args:
            code: String containing Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary containing execution results
        """
        if timeout is None or timeout <= 0:
            timeout = float('inf')
        
        # Create and start execution thread
        execution_thread = ThreadWithException(target=self._execute_code, args=(code,))
        execution_thread.start()
        
        # Wait for completion or timeout
        execution_thread.join(timeout)
        
        # If thread is still alive after join, it's running too long
        if execution_thread.is_alive():
            execution_thread.raise_exception()
            execution_thread.join()
            return {
                'success': False,
                'output': '',
                'error': f'Execution timed out after {timeout} seconds',
                'result': None
            }
            
        return self.execution_result or {
            'success': False,
            'output': '',
            'error': 'Execution failed with no result',
            'result': None
        }
    
    def reset_state(self):
        """Clear the stored global state"""
        self.global_state = {}

# Example usage
def execute_python_code(code: str, timeout: int = 5) -> dict:
    """
    Execute Python code and return the execution results.
    
    Args:
        code: String containing the Python code to execute
        timeout: Maximum execution time in seconds (default: 5)
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if execution was successful
        - output: Captured stdout content
        - error: Error message if execution failed
        - result: Last evaluated expression result
    """
    executor = PythonExecutor()
    return executor.execute(code, timeout)

def is_json_serializable(data):
    try:
        json.dumps(data)
        return True
    except (TypeError, OverflowError):
        return False

import numpy as np
def make_json_serializable(data):
    """
    Convert non-JSON-serializable data to a JSON-serializable format.
    
    Args:
        data: The data to convert.
        
    Returns:
        The JSON-serializable data.
    """
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