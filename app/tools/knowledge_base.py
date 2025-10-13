"""Knowledge base search tool implementation."""
from typing import Dict, Any, List
from .base import BaseTool, ToolResult, ToolFailure


class KnowledgeBaseTool(BaseTool):
    """Tool for searching the knowledge base."""
    
    name: str = "knowledge_base_search"
    description: str = "Search the knowledge base for relevant information"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute against the knowledge base"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 3
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, kb_service=None):
        super().__init__()
        self._kb_service = kb_service
        
    @property
    def kb_service(self):
        return self._kb_service
    
    async def execute(self, query: str, max_results: int = 3, **kwargs) -> ToolResult:
        """Execute knowledge base search."""
        try:
            if not self.kb_service:
                return ToolFailure(error="Knowledge base service not available")
            
            results = await self.kb_service.search_documents(query, max_results=max_results)
            
            if not results:
                return ToolResult(
                    output="No relevant documents found in knowledge base",
                    metadata={"query": query, "results_count": 0}
                )
            
            # Format results for better readability
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append({
                    "rank": i,
                    "source": result.get("source", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                })
            
            return ToolResult(
                output=formatted_results,
                metadata={
                    "query": query,
                    "results_count": len(results),
                    "tool": "knowledge_base_search"
                }
            )
            
        except Exception as e:
            return ToolFailure(error=f"Knowledge base search failed: {str(e)}")
