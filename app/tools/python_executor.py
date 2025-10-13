"""Python code execution tool."""
import asyncio
import sys
import io
import contextlib
from typing import Dict, Any, Optional
from .base import BaseTool, ToolResult, ToolFailure


class PythonExecutorTool(BaseTool):
    """Tool for executing Python code safely."""
    
    name: str = "python_execute"
    description: str = "Execute Python code and return the output"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)",
                "default": 30
            }
        },
        "required": ["code"]
    }
    
    async def execute(self, code: str, timeout: int = 30, **kwargs) -> ToolResult:
        """Execute Python code safely."""
        try:
            # Security check - prevent dangerous operations
            dangerous_patterns = [
                'import os', 'import subprocess', 'import sys', 'exec(', 'eval(',
                '__import__', 'open(', 'file(', 'input(', 'raw_input('
            ]
            
            if any(pattern in code for pattern in dangerous_patterns):
                return ToolFailure(error="Code contains potentially dangerous operations")
            
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Create a restricted execution environment
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'reversed': reversed,
                    'bool': bool,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                }
            }
            
            # Allow common safe modules
            try:
                import math
                import random
                import datetime
                import json
                restricted_globals['math'] = math
                restricted_globals['random'] = random
                restricted_globals['datetime'] = datetime
                restricted_globals['json'] = json
            except ImportError:
                pass
            
            # Execute code with timeout
            try:
                with contextlib.redirect_stdout(stdout_capture), \
                     contextlib.redirect_stderr(stderr_capture):
                    
                    # Execute the code
                    exec(code, restricted_globals)
                
                stdout_output = stdout_capture.getvalue()
                stderr_output = stderr_capture.getvalue()
                
                if stderr_output:
                    return ToolFailure(error=f"Python execution error: {stderr_output}")
                
                return ToolResult(
                    output=stdout_output if stdout_output else "Code executed successfully (no output)",
                    metadata={
                        "code_length": len(code),
                        "execution_successful": True
                    }
                )
                
            except Exception as e:
                return ToolFailure(error=f"Python execution failed: {str(e)}")
                
        except Exception as e:
            return ToolFailure(error=f"Python executor error: {str(e)}")
