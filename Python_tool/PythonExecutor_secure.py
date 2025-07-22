import sys
import os
import platform
from io import StringIO
import traceback
import threading
import time
from contextlib import contextmanager

# Check if we're on a Unix-like system
IS_UNIX = platform.system() != 'Windows'

if IS_UNIX:
    import signal

@contextmanager
def timeout_handler(seconds):
    """Cross-platform context manager for handling timeouts"""
    
    if IS_UNIX:
        # Unix-like systems: use signal-based timeout
        def timeout_signal(signum, frame):
            raise TimeoutError(f"Code execution timed out after {seconds} seconds")
        
        # Set the signal handler
        old_handler = signal.signal(signal.SIGALRM, timeout_signal)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            # Restore the old handler and cancel the alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    else:
        # Windows: use thread-based timeout
        result = [None]
        exception = [None]
        completed = [False]
        
        def execute_with_timeout():
            try:
                # This will be overridden by the actual execution
                pass
            except Exception as e:
                exception[0] = e
            finally:
                completed[0] = True
        
        # We'll use this context manager differently for Windows
        # The actual execution will be handled in the calling functions
        yield
        
        # For Windows, timeout handling is done in individual functions

def execute_with_thread_timeout(func, timeout, *args, **kwargs):
    """Execute a function with timeout using threading (Windows-compatible)"""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        # Note: We can't actually kill the thread, but we can timeout
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]

def _execute_code_core(code, namespace):
    """Core execution function for threading"""
    return exec(code, namespace)

def _evaluate_expression_core(expression, namespace):
    """Core evaluation function for threading"""
    return eval(expression, namespace)

def execute_python_code(code, timeout=10):
    """
    Execute Python code dynamically and return the result.
    
    Args:
        code (str): Python code to execute
        timeout (int): Execution timeout in seconds (default: 10)
    
    Returns:
        dict: Contains 'success', 'output', 'error', and 'return_value' keys
    """
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    result = {
        'success': False,
        'output': '',
        'error': '',
        'return_value': None
    }
    
    try:
        # Create a namespace for execution
        namespace = {'__builtins__': __builtins__}
        
        if IS_UNIX:
            # Unix: use signal-based timeout
            with timeout_handler(timeout):
                exec_result = exec(code, namespace)
        else:
            # Windows: use thread-based timeout
            exec_result = execute_with_thread_timeout(_execute_code_core, timeout, code, namespace)
        
        # Get captured output
        output = captured_output.getvalue()
        
        result.update({
            'success': True,
            'output': output,
            'return_value': exec_result
        })
        
    except TimeoutError as e:
        # Handle timeout specifically
        result.update({
            'success': False,
            'error': str(e),
            'output': captured_output.getvalue()
        })
        
    except Exception as e:
        # Capture the error
        error_msg = traceback.format_exc()
        result.update({
            'success': False,
            'error': error_msg,
            'output': captured_output.getvalue()
        })
        
    finally:
        # Restore stdout
        sys.stdout = old_stdout
    
    return result

def execute_python_expression(expression, timeout=5):
    """
    Evaluate a Python expression and return the result.
    
    Args:
        expression (str): Python expression to evaluate
        timeout (int): Evaluation timeout in seconds (default: 5)
    
    Returns:
        dict: Contains 'success', 'result', and 'error' keys
    """
    result = {
        'success': False,
        'result': None,
        'error': ''
    }
    
    try:
        if IS_UNIX:
            # Unix: use signal-based timeout
            with timeout_handler(timeout):
                # Create a safe namespace
                namespace = {'__builtins__': __builtins__}
                eval_result = eval(expression, namespace)
        else:
            # Windows: use thread-based timeout
            namespace = {'__builtins__': __builtins__}
            eval_result = execute_with_thread_timeout(_evaluate_expression_core, timeout, expression, namespace)
        
        result.update({
            'success': True,
            'result': eval_result
        })
        
    except TimeoutError as e:
        result.update({
            'success': False,
            'error': str(e)
        })
        
    except Exception as e:
        error_msg = traceback.format_exc()
        result.update({
            'success': False,
            'error': error_msg
        })
    
    return result

# # Example usage:
# if __name__ == "__main__":
#     print(f"Running on: {platform.system()}")
#     print(f"Using {'signal-based' if IS_UNIX else 'thread-based'} timeout\n")
    
#     # Test with a simple print statement
#     code1 = """
# print("Hello, World!")
# x = 5 + 3
# print(f"5 + 3 = {x}")
# """
    
#     result1 = execute_python_code(code1)
#     print("Example 1:")
#     print(f"Success: {result1['success']}")
#     print(f"Output: {result1['output']}")
    
#     # Test with an expression
#     expr = "2 ** 10"
#     result2 = execute_python_expression(expr)
#     print("\nExample 2:")
#     print(f"Success: {result2['success']}")
#     print(f"Result: {result2['result']}")
    
#     # Test with an error
#     code3 = "print(undefined_variable)"
#     result3 = execute_python_code(code3)
#     print("\nExample 3 (error):")
#     print(f"Success: {result3['success']}")
#     print(f"Error: {result3['error']}")
    
#     # Test with timeout
#     code4 = """
# import time
# print("Starting long operation...")
# time.sleep(15)
# print("This shouldn't print due to timeout")
# """
    
#     result4 = execute_python_code(code4, timeout=3)
#     print("\nExample 4 (timeout):")
#     print(f"Success: {result4['success']}")
#     print(f"Error: {result4['error']}")
#     print(f"Output: {result4['output']}")
    
#     # Test expression timeout (might be too fast to timeout on some systems)
#     print("\nExample 5 (expression timeout test):")
#     try:
#         expr_slow = "sum(range(10**7))"  # Reduced size for reliable timeout
#         result5 = execute_python_expression(expr_slow, timeout=1)
#         print(f"Success: {result5['success']}")
#         if not result5['success']:
#             print(f"Error: {result5['error']}")
#         else:
#             print(f"Result: {result5['result']}")
#     except Exception as e:
#         print(f"Test failed: {e}")
    
#     # Platform-specific timeout behavior note
#     if not IS_UNIX:
#         print("\nNote: On Windows, thread-based timeouts may not interrupt")
#         print("certain blocking operations as effectively as signal-based timeouts on Unix.")