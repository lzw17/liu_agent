"""Enhanced LiuAgent implementation based on OpenManus architecture."""
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
from pydantic import Field
from ..core.agent_base import BaseAgent, AgentState, Role, Message
from ..services.llm_service import get_llm_service
from ..services.knowledge_base import get_knowledge_base_service
from ..services.search_service import get_search_service
from ..tools import ToolCollection, WebSearchTool, KnowledgeBaseTool
from app.core.logger import logger


class LiuAgent(BaseAgent):
    """Enhanced LiuAgent with improved architecture based on OpenManus."""
    
    name: str = "LiuAgent"
    description: str = "武昌工学院AI竞赛项目智能助手，支持知识库问答、网络搜索和智能对话"
    
    system_prompt: str = """你是元启康健AI智能健康小助手小元。你的主要功能包括：
1. 基于知识库的智能问答
2. 网络搜索获取最新信息  
3. 自然语言对话交流
4. 任务规划和执行

请用中文回答，保持友好和专业的态度。

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
    
    next_step_prompt: str = "根据用户的需求，选择最合适的方式来回答问题。"
    
    # Services will be initialized in __init__
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm_service = get_llm_service()
        self.kb_service = get_knowledge_base_service()
        self.search_service = get_search_service()
        
        # Initialize tool collection
        self.tools = ToolCollection(
            WebSearchTool(search_service=self.search_service),
            KnowledgeBaseTool(kb_service=self.kb_service)
        )
        
        # Configuration flags
        self.use_knowledge_base = True
        self.use_web_search = True
    
    class Config:
        arbitrary_types_allowed = True
    
    async def step(self) -> str:
        """Execute a single step in the agent's workflow."""
        try:
            # Get the latest user message
            recent_messages = self.memory.get_recent_messages(5)
            if not recent_messages:
                return "No messages to process"
            
            user_message = None
            for msg in reversed(recent_messages):
                if msg.role == Role.USER:
                    user_message = msg.content
                    break
            
            if not user_message:
                return "No user message found"
            
            # Process the message
            response = await self.process_message(user_message)
            
            # Add response to memory
            self.update_memory(Role.ASSISTANT, response)
            
            # Mark as finished after processing
            self.state = AgentState.FINISHED
            
            return f"Processed message: {user_message[:50]}..."
            
        except Exception as e:
            logger.error(f"Error in agent step: {e}")
            self.state = AgentState.ERROR
            return f"Error: {str(e)}"
    
    async def process_message(self, message: str) -> str:
        """Process a user message and generate response using tools when appropriate."""
        try:
            # Determine which tools to use based on message content
            tool_results = []
            
            # Use knowledge base tool if enabled
            if self.use_knowledge_base:
                kb_result = await self.execute_tool("knowledge_base_search", {"query": message})
                if "知识库中未找到相关信息" not in kb_result:
                    tool_results.append(kb_result)
            
            # Use web search tool if enabled and needed
            if self.use_web_search and self._needs_web_search(message):
                web_result = await self.execute_tool("web_search", {"query": message})
                if "未找到相关的网络搜索结果" not in web_result:
                    tool_results.append(web_result)
            
            # Build context from tool results
            context = "\n\n".join(tool_results) if tool_results else ""
            
            # Build messages for LLM
            messages = []
            
            # System message with context
            system_content = self.system_prompt
            if context:
                system_content += f"\n\n参考信息:\n{context}"
            
            messages.append(Message(role=Role.SYSTEM, content=system_content))
            
            # Add recent conversation history
            recent_messages = self.memory.get_recent_messages(10)
            messages.extend(recent_messages)
            
            # Add current user message
            messages.append(Message(role=Role.USER, content=message))
            
            # Generate response
            response = await self.llm_service.chat_completion(
                [msg.to_dict() for msg in messages],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"抱歉，处理您的消息时出现了错误：{str(e)}"
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced chat method with conversation management."""
        try:
            # Add user message to memory
            self.update_memory(Role.USER, message, timestamp=datetime.now().isoformat())
            
            # Process the message
            response = await self.process_message(message)
            
            # Add assistant response to memory
            self.update_memory(Role.ASSISTANT, response, timestamp=datetime.now().isoformat())
            
            return {
                "response": response,
                "conversation_id": conversation_id or "default",
                "sources": [],
                "metadata": {
                    "used_knowledge_base": self.use_knowledge_base,
                    "used_web_search": self.use_web_search,
                    "message_count": len(self.memory.messages)
                }
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": f"抱歉，处理您的消息时出现了错误：{str(e)}",
                "conversation_id": conversation_id or "default",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    def clear_memory(self):
        """Clear agent memory."""
        self.memory.clear()
        self.current_step = 0
        self.state = AgentState.IDLE
    
    def get_conversation_history(self) -> list:
        """Get conversation history as list of dicts."""
        return self.memory.to_dict_list()
    
    def set_configuration(self, **kwargs):
        """Update agent configuration."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a specific tool and return formatted result."""
        try:
            result = await self.tools.execute(name=tool_name, tool_input=tool_input)
            
            if result.error:
                return f"工具执行失败: {result.error}"
            
            # Format tool output for display
            if tool_name == "web_search":
                if isinstance(result.output, list) and result.output:
                    formatted = "网络搜索结果:\n"
                    for item in result.output[:3]:  # Limit to top 3 results
                        formatted += f"• {item.get('title', '')}\n  {item.get('snippet', '')}\n  来源: {item.get('url', '')}\n\n"
                    return formatted
                else:
                    return "未找到相关的网络搜索结果。"
            
            elif tool_name == "knowledge_base_search":
                if isinstance(result.output, list) and result.output:
                    formatted = "知识库搜索结果:\n"
                    for item in result.output:
                        formatted += f"• 来源: {item.get('source', '')}\n  内容: {item.get('content', '')}\n\n"
                    return formatted
                else:
                    return "知识库中未找到相关信息。"
            
            return str(result.output)
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return f"工具执行出错: {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return self.tools.list_tools()
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available tools."""
        return self.tools.get_tool_descriptions()
