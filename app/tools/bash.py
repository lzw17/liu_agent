"""Bash command execution tool."""
import asyncio
import subprocess
from typing import Dict, Any, Optional
from .base import BaseTool, ToolResult, ToolFailure


class BashTool(BaseTool):
    """Tool for executing bash commands."""
    
    name: str = "bash"
    description: str = "Execute bash commands in the system shell"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)",
                "default": 30
            }
        },
        "required": ["command"]
    }
    
    async def execute(self, command: str, timeout: int = 30, **kwargs) -> ToolResult:
        """Execute bash command."""
        try:
            # Security check - prevent dangerous commands
            dangerous_patterns = ['rm -rf /', 'sudo', 'passwd', 'chmod 777', 'mkfs']
            if any(pattern in command.lower() for pattern in dangerous_patterns):
                return ToolFailure(error="Command contains potentially dangerous operations")
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/tmp"  # Safe working directory
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ToolFailure(error=f"Command timed out after {timeout} seconds")
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            if process.returncode == 0:
                return ToolResult(
                    output=stdout_text,
                    metadata={
                        "command": command,
                        "return_code": process.returncode,
                        "stderr": stderr_text if stderr_text else None
                    }
                )
            else:
                return ToolFailure(
                    error=f"Command failed with return code {process.returncode}: {stderr_text}"
                )
                
        except Exception as e:
            return ToolFailure(error=f"Bash execution failed: {str(e)}")
