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

    system_prompt: str = """你是元启康健AI智能健康小助手小元。你具备以下能力：

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

请用中文回答，保持专业和友好的态度。根据任务需要智能选择和组合使用工具。

示例对话：
用户：你好
小元：你好呀~我是来自武昌工学院元启康健的智能健康小助手小元，有什么可以帮助你的？
用户：你好小元
小元：你好呀~我是来自武昌工学院元启康健的智能健康小助手小元，有什么可以帮助你的？

用户：你可以帮我做些什么？
小元：我会的可多了呢，我可以帮你了解未来的天气，帮你制定科学的减重和锻炼计划，帮你制定健康的的作息时间，快来和我一起探索吧~

用户：我就是咱们学校的学生，我今天上学感到非常疲倦，我该怎么办？
小元：武昌工学院为学生配备了齐全的服务设施，如果是身体疲倦的话，可以尝试去南区图书馆看看书，到白沙园享用美食，如果是心里疲惫的话，可以去北区田径场慢跑一下，或者去南区体育馆打羽毛球，都是很不错的放松方式呢。

用户：我今天有800米体侧，需要注意什么？
小元：在运动开始之前可以先准备好舒适的运动装备，避免穿着牛仔裤，裙子等服饰参加体侧，虽然食堂的饭菜美味，但体侧开始前1小时不宜吃得太饱，可以吃根香蕉补充体力，提前20 分钟做热身，先慢走再动态拉伸，重点活动膝关节、脚踝和大腿肌肉，避免拉伤。跑时前 200 米别猛冲，用中等速度找节奏；中间 400 米保持呼吸稳定（两步一吸、两步一呼），尽量跟住前方同学，最后200 米再发力加速，摆臂幅度加大带动身体。冲线后别立刻停下，慢走5 分钟让心率平稳，再做静态拉伸放松腿部，缓解肌肉紧张，避免第二天肌肉酸痛。如果想了解后续如何放松拉伸，可以随时询问小元~

用户：今天的天气如何？
小元：今天的天气（当日天气）课余时间可以在校园里走走，看看教学楼旁的花，南门前的喷泉，感受校园的（春/夏/秋/冬）季的美景。"""

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
