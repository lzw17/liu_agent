from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BaseTool(ABC, BaseModel):
    """Base class for all tools."""
    
    name: str
    description: str
    parameters: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True

    async def __call__(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        return await self.execute(**kwargs)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass

    def to_param(self) -> Dict:
        """Convert tool to function call format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolResult(BaseModel):
    """Represents the result of a tool execution."""

    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __bool__(self):
        return any(getattr(self, field) for field in self.__fields__)

    def __str__(self):
        return f"Error: {self.error}" if self.error else str(self.output)

    def replace(self, **kwargs):
        """Returns a new ToolResult with the given fields replaced."""
        return type(self)(**{**self.dict(), **kwargs})


class ToolFailure(ToolResult):
    """A ToolResult that represents a failure."""
    
    def __init__(self, error: str, **kwargs):
        super().__init__(error=error, **kwargs)
