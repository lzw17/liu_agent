"""Collection classes for managing multiple tools."""
from typing import Any, Dict, List
from .base import BaseTool, ToolFailure, ToolResult
import logging

logger = logging.getLogger(__name__)


class ToolCollection:
    """A collection of defined tools."""

    def __init__(self, *tools: BaseTool):
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    def __iter__(self):
        return iter(self.tools)

    def to_params(self) -> List[Dict[str, Any]]:
        """Convert all tools to function call parameters."""
        return [tool.to_param() for tool in self.tools]

    async def execute(
        self, *, name: str, tool_input: Dict[str, Any] = None
    ) -> ToolResult:
        """Execute a specific tool by name."""
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        
        try:
            if tool_input is None:
                tool_input = {}
            result = await tool(**tool_input)
            if isinstance(result, ToolResult):
                return result
            else:
                return ToolResult(output=result)
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}")
            return ToolFailure(error=str(e))

    async def execute_all(self) -> List[ToolResult]:
        """Execute all tools in the collection sequentially."""
        results = []
        for tool in self.tools:
            try:
                result = await tool()
                results.append(result)
            except Exception as e:
                results.append(ToolFailure(error=str(e)))
        return results

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name."""
        return self.tool_map.get(name)

    def add_tool(self, tool: BaseTool):
        """Add a single tool to the collection."""
        if tool.name in self.tool_map:
            logger.warning(f"Tool {tool.name} already exists in collection, skipping")
            return self

        self.tools += (tool,)
        self.tool_map[tool.name] = tool
        return self

    def add_tools(self, *tools: BaseTool):
        """Add multiple tools to the collection."""
        for tool in tools:
            self.add_tool(tool)
        return self

    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tool_map.keys())

    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all tools."""
        return {name: tool.description for name, tool in self.tool_map.items()}
