"""Terminate tool for ending agent execution."""
from typing import Dict, Any
from .base import BaseTool, ToolResult


class TerminateTool(BaseTool):
    """Tool for terminating agent execution."""
    
    name: str = "terminate"
    description: str = "Terminate the agent execution when task is completed"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Reason for termination"
            },
            "success": {
                "type": "boolean",
                "description": "Whether the task was completed successfully",
                "default": True
            }
        },
        "required": ["reason"]
    }
    
    async def execute(self, reason: str, success: bool = True, **kwargs) -> ToolResult:
        """Execute termination."""
        return ToolResult(
            output=f"任务{'成功' if success else '失败'}完成: {reason}",
            metadata={
                "terminated": True,
                "success": success,
                "reason": reason
            }
        )
