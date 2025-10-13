"""ToolCall agent implementation based on OpenManus architecture."""
import asyncio
import json
import uuid
from typing import Any, List, Optional, Union, Dict

from pydantic import Field

from ..core.agent_base import BaseAgent, AgentState, Message, ToolCall, Role
from ..core.logger import logger
from ..tools import ToolCollection, BaseTool


class ToolCallAgent(BaseAgent):
    """Base agent class for handling tool/function calls with enhanced abstraction"""

    name: str = "toolcall"
    description: str = "An agent that can execute tool calls."

    system_prompt: str = """You are an intelligent AI assistant that can use various tools to help users accomplish tasks.

When you need to use a tool, you should:
1. Analyze the user's request carefully
2. Choose the most appropriate tool(s) for the task
3. Execute the tool calls with proper parameters
4. Interpret the results and provide helpful responses

Available tools will be provided in the function definitions. Use them wisely to provide the best assistance possible."""

    next_step_prompt: str = "What should I do next to help the user?"

    available_tools: ToolCollection = Field(default_factory=ToolCollection)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    
    max_steps: int = 30
    max_observe: Optional[Union[int, bool]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm_service = None
        
    async def think(self) -> bool:
        """Process current state and decide next actions using tools"""
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.memory.add_message(user_msg)

        try:
            # Get response with tool options
            response = await self._get_llm_response()
            
            if not response:
                return False
                
            # Parse tool calls if any
            tool_calls = self._parse_tool_calls(response)
            
            if tool_calls:
                # Execute tool calls
                await self._execute_tool_calls(tool_calls)
                return True
            else:
                # Regular response without tools
                assistant_msg = Message.assistant_message(response)
                self.memory.add_message(assistant_msg)
                return False
                
        except Exception as e:
            logger.error(f"Error in think(): {e}")
            self.state = AgentState.ERROR
            return False

    async def _get_llm_response(self) -> Optional[str]:
        """Get response from LLM with tool support."""
        if not self.llm_service:
            from ..services.llm_service import get_llm_service
            self.llm_service = get_llm_service()
        
        # Build messages for LLM
        messages = []
        
        # Add system message
        if self.system_prompt:
            messages.append(Message.system_message(self.system_prompt))
        
        # Add conversation history
        messages.extend(self.memory.get_recent_messages(10))
        
        # Convert to dict format for LLM
        message_dicts = []
        for msg in messages:
            try:
                message_dicts.append(msg.to_dict())
            except Exception as e:
                logger.error(f"Failed to convert message to dict: {e}")
                # 创建一个基本的消息字典
                message_dicts.append({
                    "role": msg.role.value if hasattr(msg, 'role') else "user",
                    "content": msg.content if hasattr(msg, 'content') else str(msg)
                })
        
        try:
            # Get tools for function calling
            tools = self.available_tools.to_params() if self.available_tools.tools else None
            
            # 暂时不支持工具调用，使用普通聊天完成
            response = await self.llm_service.chat_completion(
                message_dicts,
                max_tokens=2000
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return None

    def _parse_tool_calls(self, response: str) -> List[ToolCall]:
        """Parse tool calls from LLM response."""
        tool_calls = []
        
        # Try to parse JSON tool calls (this is a simplified implementation)
        # In a real implementation, you'd parse the actual LLM response format
        try:
            if "tool_calls" in response:
                # Parse structured tool calls
                data = json.loads(response)
                for tc_data in data.get("tool_calls", []):
                    tool_call = ToolCall(
                        id=tc_data.get("id", str(uuid.uuid4())),
                        function=tc_data.get("function", {}),
                        type=tc_data.get("type", "function")
                    )
                    tool_calls.append(tool_call)
        except (json.JSONDecodeError, KeyError):
            # If not structured, look for function call patterns
            pass
            
        return tool_calls

    async def _execute_tool_calls(self, tool_calls: List[ToolCall]) -> None:
        """Execute a list of tool calls."""
        for tool_call in tool_calls:
            try:
                # Execute the tool
                function_name = tool_call.function.get("name")
                function_args = tool_call.function.get("arguments", {})
                
                if isinstance(function_args, str):
                    function_args = json.loads(function_args)
                
                # Execute tool
                result = await self.available_tools.execute(
                    name=function_name,
                    tool_input=function_args
                )
                
                # Add tool result to memory
                tool_result_msg = Message.tool_message(
                    content=str(result.output) if result.output else str(result.error),
                    tool_call_id=tool_call.id
                )
                self.memory.add_message(tool_result_msg)
                
                logger.info(f"Executed tool {function_name}: {result}")
                
            except Exception as e:
                logger.error(f"Tool execution failed for {tool_call.function.get('name')}: {e}")
                # Add error message
                error_msg = Message.tool_message(
                    content=f"Tool execution failed: {str(e)}",
                    tool_call_id=tool_call.id
                )
                self.memory.add_message(error_msg)

    async def step(self) -> str:
        """Execute a single step in the agent's workflow."""
        try:
            self.state = AgentState.THINKING
            
            # Think and decide on actions
            should_continue = await self.think()
            
            if should_continue:
                self.state = AgentState.EXECUTING
                return f"Step {self.current_step}: Executed tools and continuing..."
            else:
                self.state = AgentState.FINISHED
                return f"Step {self.current_step}: Task completed."
                
        except Exception as e:
            logger.error(f"Error in agent step: {e}")
            self.state = AgentState.ERROR
            return f"Error: {str(e)}"

    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent's available tools."""
        self.available_tools.add_tool(tool)

    def add_tools(self, *tools: BaseTool) -> None:
        """Add multiple tools to the agent."""
        self.available_tools.add_tools(*tools)

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return self.available_tools.list_tools()
