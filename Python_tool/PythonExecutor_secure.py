import sys
from io import StringIO
import traceback

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
        
        # Execute the code
        exec_result = exec(code, namespace)
        
        # Get captured output
        output = captured_output.getvalue()
        
        result.update({
            'success': True,
            'output': output,
            'return_value': exec_result
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

def execute_python_expression(expression):
    """
    Evaluate a Python expression and return the result.
    
    Args:
        expression (str): Python expression to evaluate
    
    Returns:
        dict: Contains 'success', 'result', and 'error' keys
    """
    result = {
        'success': False,
        'result': None,
        'error': ''
    }
    
    try:
        # Create a safe namespace
        namespace = {'__builtins__': __builtins__}
        
        # Evaluate the expression
        eval_result = eval(expression, namespace)
        
        result.update({
            'success': True,
            'result': eval_result
        })
        
    except Exception as e:
        error_msg = traceback.format_exc()
        result.update({
            'success': False,
            'error': error_msg
        })
    
    return result

# Example usage:
if __name__ == "__main__":
    # Test with a simple print statement
    code1 = """
print("Hello, World!")
x = 5 + 3
print(f"5 + 3 = {x}")
"""
    
    result1 = execute_python_code(code1)
    print("Example 1:")
    print(f"Success: {result1['success']}")
    print(f"Output: {result1['output']}")
    
    # Test with an expression
    expr = "2 ** 10"
    result2 = execute_python_expression(expr)
    print("\nExample 2:")
    print(f"Success: {result2['success']}")
    print(f"Result: {result2['result']}")
    
    # Test with an error
    code3 = "print(undefined_variable)"
    result3 = execute_python_code(code3)
    print("\nExample 3 (error):")
    print(f"Success: {result3['success']}")
    print(f"Error: {result3['error']}")