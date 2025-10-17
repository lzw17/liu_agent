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

请用中文回答，保持友好和专业的态度。"""
    
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
