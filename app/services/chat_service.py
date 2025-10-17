"""Enhanced chat service using improved agent architecture."""
import uuid
from typing import Optional, Dict, Any, List

from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.agents.manus_agent import ManusAgent
from app.core.logger import logger
from app.core import get_config
from app.services.llm_service import get_llm_service


class ConversationManager:
    """Manages conversation state and history."""
    
    def __init__(self):
        self.conversations: Dict[str, ManusAgent] = {}
    
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = ManusAgent()
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> ManusAgent:
        """Get conversation agent by ID."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ManusAgent()
        return self.conversations[conversation_id]
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].clear_memory()


class ChatService:
    """Enhanced service for handling chat requests using LiuAgent."""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request using enhanced LiuAgent via LLMService."""
        conversation_id = request.conversation_id
        try:
            # Get or create conversation agent
            if not conversation_id:
                conversation_id = self.conversation_manager.create_conversation()

            # Get conversation agent
            agent = self.conversation_manager.get_conversation(conversation_id)

            # Build messages for provider
            messages: List[ChatMessage] = [
                ChatMessage(role="system", content="你是元启康健AI智能健康小助手小元。你具备知识库查询、网络搜索、文件操作等多种能力。请用中文回答，保持专业和友好的态度。"),
                ChatMessage(role="user", content=request.message)
            ]

            # Use LLMService with provider selection
            llm = get_llm_service()
            result = await llm.chat_completion(
                messages,
                provider=request.provider or "primary",
                max_tokens=request.max_tokens or None,
                temperature=request.temperature or None
            )

            return ChatResponse(
                response=result,
                conversation_id=conversation_id,
                sources=[],
                metadata={
                    "agent_type": "ManusAgent",
                    "tools_available": len(agent.available_tools.tools),
                    "provider": request.provider or "primary"
                }
            )

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return ChatResponse(
                response=f"抱歉，处理您的消息时出现了错误：{str(e)}",
                conversation_id=conversation_id or "error",
                sources=[],
                metadata={"error": str(e)}
            )
    
    async def stream_chat(self, request: ChatRequest):
        """Process chat request with streaming response using LLMService."""
        try:
            # Get or create conversation agent
            conversation_id = request.conversation_id
            if not conversation_id:
                conversation_id = self.conversation_manager.create_conversation()

            # Ensure agent exists (for future tool integration)
            _ = self.conversation_manager.get_conversation(conversation_id)

            # Build messages
            messages: List[ChatMessage] = [
                ChatMessage(role="system", content="你是元启康健AI智能健康小助手小元。你具备知识库查询、网络搜索、文件操作等多种能力。请用中文回答，保持专业和友好的态度。"),
                ChatMessage(role="user", content=request.message)
            ]

            # Send start block
            yield {"type": "start", "conversation_id": conversation_id}
            yield {"type": "delta", "delta": ""}

            llm = get_llm_service()
            full_text_parts: List[str] = []
            async for piece in llm.stream_completion(
                messages,
                provider=request.provider or "primary",
                max_tokens=request.max_tokens or None,
                temperature=request.temperature or None
            ):
                if piece:
                    full_text_parts.append(piece)
                    yield {"type": "delta", "delta": piece}

            yield {"type": "done", "conversation_id": conversation_id, "text": "".join(full_text_parts)}

        except Exception as e:
            logger.error(f"Stream chat processing failed: {e}")
            yield {"error": f"抱歉，处理您的消息时出现了错误：{str(e)}"}


# Global chat service instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
