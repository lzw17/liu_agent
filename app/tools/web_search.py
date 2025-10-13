"""Web search tool implementation."""
from typing import Dict, Any, List
from .base import BaseTool, ToolResult, ToolFailure


class WebSearchTool(BaseTool):
    """Tool for performing web searches."""
    
    name: str = "web_search"
    description: str = "Search the web for information on a given query"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, search_service=None):
        super().__init__()
        self._search_service = search_service
        
    @property
    def search_service(self):
        return self._search_service
    
    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        """Execute web search."""
        try:
            if not self.search_service:
                return ToolFailure(error="Web search service not available")
            
            results = await self.search_service.search(query, max_results=max_results)
            
            if not results:
                return ToolResult(
                    output="No search results found",
                    metadata={"query": query, "results_count": 0}
                )
            
            # Format results for better readability
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append({
                    "rank": i,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", "")
                })
            
            return ToolResult(
                output=formatted_results,
                metadata={
                    "query": query,
                    "results_count": len(results),
                    "tool": "web_search"
                }
            )
            
        except Exception as e:
            return ToolFailure(error=f"Web search failed: {str(e)}")
