"""Enhanced base agent architecture inspired by OpenManus."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, AsyncContextManager, Union
from enum import Enum
from datetime import datetime
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, model_validator
import asyncio
import json
from app.core.logger import logger


class AgentState(str, Enum):
    """Agent execution states."""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    THINKING = "thinking"
    EXECUTING = "executing"


class Role(str, Enum):
    """Message role options"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """Tool call representation."""
    id: str
    function: Dict[str, Any]
    type: str = "function"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "function": self.function
        }

class Message(BaseModel):
    """Message model for agent communication."""
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.tool_calls:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result
    
    @classmethod
    def user_message(cls, content: str) -> "Message":
        """Create user message."""
        return cls(role=Role.USER, content=content)
    
    @classmethod
    def assistant_message(cls, content: str, tool_calls: Optional[List[ToolCall]] = None) -> "Message":
        """Create assistant message."""
        return cls(role=Role.ASSISTANT, content=content, tool_calls=tool_calls)
    
    @classmethod
    def system_message(cls, content: str) -> "Message":
        """Create system message."""
        return cls(role=Role.SYSTEM, content=content)
    
    @classmethod
    def tool_message(cls, content: str, tool_call_id: str) -> "Message":
        """Create tool result message."""
        return cls(role=Role.TOOL, content=content, tool_call_id=tool_call_id)


class Memory(BaseModel):
    """Agent memory management system"""
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100)
    
    def add_message(self, message: Message) -> None:
        """Add a message to memory"""
        self.messages.append(message)
        # Implement message limit
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def add_messages(self, messages: List[Message]) -> None:
        """Add multiple messages to memory"""
        self.messages.extend(messages)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()
    
    def get_recent_messages(self, n: int) -> List[Message]:
        """Get n most recent messages"""
        return self.messages[-n:]
    
    def to_dict_list(self) -> List[dict]:
        """Convert messages to list of dicts"""
        return [msg.dict() for msg in self.messages]


class BaseAgent(BaseModel, ABC):
    """Abstract base class for managing agent state and execution.
    
    Provides foundational functionality for state transitions, memory management,
    and a step-based execution loop. Subclasses must implement the `step` method.
    """
    
    # Core attributes
    name: str = Field(..., description="Unique name of the agent")
    description: Optional[str] = Field(None, description="Optional agent description")
    
    # Prompts
    system_prompt: Optional[str] = Field(
        None, description="System-level instruction prompt"
    )
    next_step_prompt: Optional[str] = Field(
        None, description="Prompt for determining next action"
    )
    
    # Dependencies
    memory: Memory = Field(default_factory=Memory, description="Agent's memory store")
    state: AgentState = Field(
        default=AgentState.IDLE, description="Current agent state"
    )
    
    # Execution control
    max_steps: int = Field(default=10, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")
    duplicate_threshold: int = 2
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
    
    @model_validator(mode="after")
    def initialize_agent(self) -> "BaseAgent":
        """Initialize agent with default settings if not provided."""
        if not isinstance(self.memory, Memory):
            self.memory = Memory()
        return self
    
    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """Context manager for safe agent state transitions."""
        if not isinstance(new_state, AgentState):
            raise ValueError(f"Invalid state: {new_state}")
        
        previous_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR
            raise e
        finally:
            self.state = previous_state
    
    def update_memory(
        self,
        role: Role,
        content: str,
        **kwargs,
    ) -> None:
        """Add a message to the agent's memory."""
        message_map = {
            Role.USER: Message.user_message,
            Role.SYSTEM: Message.system_message,
            Role.ASSISTANT: Message.assistant_message,
        }
        
        if role not in message_map:
            raise ValueError(f"Unsupported message role: {role}")
        
        self.memory.add_message(message_map[role](content, **kwargs))
    
    async def run(self, request: Optional[str] = None) -> str:
        """Execute the agent's main loop asynchronously."""
        if self.state != AgentState.IDLE:
            raise RuntimeError(f"Cannot run agent from state: {self.state}")
        
        if request:
            self.update_memory(Role.USER, request)
        
        results: List[str] = []
        async with self.state_context(AgentState.RUNNING):
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
            ):
                self.current_step += 1
                logger.info(f"Executing step {self.current_step}/{self.max_steps}")
                step_result = await self.step()
                
                # Check for stuck state
                if self.is_stuck():
                    self.handle_stuck_state()
                
                results.append(f"Step {self.current_step}: {step_result}")
            
            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                results.append(f"Terminated: Reached max steps ({self.max_steps})")
        
        return "\n".join(results) if results else "No steps executed"
    
    @abstractmethod
    async def step(self) -> str:
        """Execute a single step in the agent's workflow."""
        pass
    
    def handle_stuck_state(self):
        """Handle stuck state by adding a prompt to change strategy"""
        stuck_prompt = "Observed duplicate responses. Consider new strategies and avoid repeating ineffective paths already attempted."
        self.next_step_prompt = f"{stuck_prompt}\n{self.next_step_prompt}"
        logger.warning(f"Agent detected stuck state. Added prompt: {stuck_prompt}")
    
    def is_stuck(self) -> bool:
        """Check if the agent is stuck in a loop by detecting duplicate content"""
        if len(self.memory.messages) < 2:
            return False
        
        last_message = self.memory.messages[-1]
        if not last_message.content:
            return False
        
        # Count identical content occurrences
        duplicate_count = sum(
            1
            for msg in reversed(self.memory.messages[:-1])
            if msg.role == Role.ASSISTANT and msg.content == last_message.content
        )
        
        return duplicate_count >= self.duplicate_threshold
    
    @property
    def messages(self) -> List[Message]:
        """Retrieve a list of messages from the agent's memory."""
        return self.memory.messages
    
    @messages.setter
    def messages(self, value: List[Message]):
        """Set the list of messages in the agent's memory."""
        self.memory.messages = value
