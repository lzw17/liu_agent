"""Enhanced Pydantic models for API requests and responses."""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    use_knowledge_base: bool = Field(True, description="Whether to use knowledge base")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    temperature: Optional[float] = Field(None, description="Response temperature")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[str] = Field(default_factory=list, description="Knowledge base sources used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: Optional[int] = Field(10, description="Maximum number of results")
    engine: Optional[str] = Field(None, description="Search engine to use")


class SearchResult(BaseModel):
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result snippet")
    source: str = Field(..., description="Search engine used")


class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total number of results")


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    pages: int = Field(..., description="Number of pages processed")
    chunks: int = Field(..., description="Number of text chunks created")
    status: str = Field(..., description="Processing status")


class KnowledgeBaseDocument(BaseModel):
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    upload_date: datetime = Field(..., description="Upload timestamp")
    pages: int = Field(..., description="Number of pages")
    chunks: int = Field(..., description="Number of chunks")
    file_size: int = Field(..., description="File size in bytes")


class KnowledgeBaseResponse(BaseModel):
    documents: List[KnowledgeBaseDocument] = Field(..., description="List of documents")
    total_documents: int = Field(..., description="Total number of documents")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict, description="Service statuses")


# Agent-related schemas
class AgentState(str, Enum):
    """Agent execution states."""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class Role(str, Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AgentMessage(BaseModel):
    """Enhanced message model for agent communication."""
    role: Role = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AgentStatus(BaseModel):
    """Agent status information."""
    name: str = Field(..., description="Agent name")
    state: AgentState = Field(..., description="Current agent state")
    current_step: int = Field(..., description="Current execution step")
    max_steps: int = Field(..., description="Maximum allowed steps")
    memory_size: int = Field(..., description="Number of messages in memory")
    tools_available: List[str] = Field(..., description="Available tool names")


class ToolRequest(BaseModel):
    """Tool execution request."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ToolResponse(BaseModel):
    """Tool execution response."""
    tool_name: str = Field(..., description="Name of the executed tool")
    success: bool = Field(..., description="Whether execution was successful")
    output: Any = Field(default=None, description="Tool output")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ConversationInfo(BaseModel):
    """Conversation information."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    created_at: datetime = Field(..., description="Conversation creation time")
    message_count: int = Field(..., description="Number of messages in conversation")
    last_activity: datetime = Field(..., description="Last message timestamp")
    agent_state: AgentState = Field(..., description="Current agent state")


class ConfigResponse(BaseModel):
    llm_providers: List[str] = Field(..., description="Available LLM providers")
    search_engines: List[str] = Field(..., description="Available search engines")
    max_file_size: int = Field(..., description="Maximum file upload size")
    allowed_extensions: List[str] = Field(..., description="Allowed file extensions")
    agent_config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
