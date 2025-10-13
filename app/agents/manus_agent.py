"""Manus agent implementation - the main LiuAgent based on OpenManus architecture."""
from typing import Dict, List, Optional, Any
from pydantic import Field

from .toolcall_agent import ToolCallAgent
from ..tools import ToolCollection
from ..tools.bash import BashTool
from ..tools.file_editor import FileEditorTool
from ..tools.python_executor import PythonExecutorTool
from ..tools.web_search import WebSearchTool
from ..tools.knowledge_base import KnowledgeBaseTool
from ..tools.planning import PlanningTool
from ..tools.terminate import TerminateTool
from ..core.logger import logger


class ManusAgent(ToolCallAgent):
    """A versatile general-purpose agent with comprehensive tool support."""

    name: str = "LiuAgent"
    description: str = "武昌工学院AI竞赛项目智能助手，支持多种工具和任务执行"

    system_prompt: str = """你是LiuAgent，武昌工学院的AI智能助手。你具备以下能力：

🔧 **工具能力**：
- 文件操作：创建、编辑、读取各种文件
- 代码执行：Python代码运行和调试
- 网络搜索：获取最新信息和资料
- 知识库查询：检索相关文档和资料
- 系统命令：执行bash命令和系统操作
- 任务规划：制定和管理复杂任务计划

🎯 **核心职责**：
1. 理解用户需求，制定合理的解决方案
2. 选择合适的工具完成任务
3. 提供准确、有用的信息和建议
4. 协助学习、研究和项目开发

请用中文回答，保持专业和友好的态度。根据任务需要智能选择和组合使用工具。"""

    next_step_prompt: str = "基于当前情况，我应该采取什么行动来更好地帮助用户？"

    max_observe: int = 10000
    max_steps: int = 25

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all available tools."""
        try:
            # Import services
            from ..services.llm_service import get_llm_service
            from ..services.knowledge_base import get_knowledge_base_service
            from ..services.search_service import get_search_service
            
            # Get service instances
            llm_service = get_llm_service()
            kb_service = get_knowledge_base_service()
            search_service = get_search_service()
            
            # Initialize tools with services
            tools = [
                WebSearchTool(search_service=search_service),
                KnowledgeBaseTool(kb_service=kb_service),
                PythonExecutorTool(),
                FileEditorTool(),
                BashTool(),
                PlanningTool(),
                TerminateTool()
            ]
            
            self.available_tools = ToolCollection(*tools)
            logger.info(f"Initialized {len(tools)} tools for ManusAgent")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            self.available_tools = ToolCollection()

    @classmethod
    async def create(cls, **kwargs) -> "ManusAgent":
        """Factory method to create and properly initialize a ManusAgent instance."""
        instance = cls(**kwargs)
        # Additional async initialization if needed
        return instance

    async def cleanup(self):
        """Clean up agent resources."""
        # Cleanup any resources if needed
        pass

    async def process_user_request(self, request: str) -> str:
        """Process a user request and return response."""
        try:
            # Add user message to memory
            self.update_memory(role="user", content=request)
            
            # Run the agent to process the request
            result = await self.run(request)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing user request: {e}")
            return f"抱歉，处理您的请求时出现了错误：{str(e)}"

    def get_tool_status(self) -> Dict[str, Any]:
        """Get status of all available tools."""
        return {
            "available_tools": self.available_tools.list_tools(),
            "tool_descriptions": self.available_tools.get_tool_descriptions(),
            "total_tools": len(self.available_tools.tools)
        }
