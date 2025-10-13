"""Enhanced chat service using improved agent architecture."""
import uuid
from typing import Optional, Dict, Any

from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.agents.manus_agent import ManusAgent
from app.core.logger import logger


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
        """Process chat request using enhanced LiuAgent."""
        try:
            # Get or create conversation agent
            conversation_id = request.conversation_id
            if not conversation_id:
                conversation_id = self.conversation_manager.create_conversation()
            
            # Get conversation agent
            agent = self.conversation_manager.get_conversation(conversation_id)
            
            # ManusAgent doesn't need configuration - it has all tools integrated
            
            # 使用DeepSeek API处理请求
            import openai
            
            # 构建消息
            messages = [
                {"role": "system", "content": "你是LiuAgent，武昌工学院的AI智能助手。你具备知识库查询、网络搜索、文件操作等多种能力。请用中文回答，保持专业和友好的态度。"}, 
                {"role": "user", "content": request.message}
            ]
            
            try:
                # 直接使用提供的DeepSeek API密钥
                api_key = "sk-99b2bc0657b24c7ba54084593d106620"
                base_url = "https://api.deepseek.com/v1"
                model = "deepseek-chat"
                
                # 创建OpenAI客户端直接调用DeepSeek API
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                
                # 调用API
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 提取响应
                result = response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"DeepSeek API调用失败: {e}")
                result = f"抱歉，我暂时无法回答您的问题。请稍后再试。错误信息：{str(e)}"
            
            return ChatResponse(
                response=result,
                conversation_id=conversation_id,
                sources=[],
                metadata={"agent_type": "ManusAgent", "tools_available": len(agent.available_tools.tools)}
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
        """Process chat request with streaming response using enhanced agent."""
        try:
            # Get or create conversation agent
            conversation_id = request.conversation_id
            if not conversation_id:
                conversation_id = self.conversation_manager.create_conversation()
            
            # Get conversation agent
            agent = self.conversation_manager.get_conversation(conversation_id)
            
            # Note: ManusAgent currently未提供 set_configuration 方法，避免调用以防 AttributeError
            
            # DeepSeek API (via OpenAI client) streaming
            import openai
            api_key = "sk-99b2bc0657b24c7ba54084593d106620"
            base_url = "https://api.deepseek.com/v1"
            model = "deepseek-chat"
            
            # 构建消息
            messages = [
                {"role": "system", "content": "你是LiuAgent，武昌工学院的AI智能助手。你具备知识库查询、网络搜索、文件操作等多种能力。请用中文回答，保持专业和友好的态度。"},
                {"role": "user", "content": request.message}
            ]
            
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
            
            # 首先发送一个初始化块，包含会话ID，便于前端建立上下文
            yield {"type": "start", "conversation_id": conversation_id}
            # 立即发送一个极小的增量，帮助前端确认SSE通道已建立
            yield {"type": "delta", "delta": ""}
            
            # 开启流式响应
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )
            
            # 逐块发送增量内容
            full_text = []
            for event in stream:
                try:
                    choice = None
                    # 兼容不同返回结构（OpenAI SDK v1 风格）
                    if hasattr(event, "choices") and event.choices:
                        choice = event.choices[0]
                    if choice is None:
                        continue
                    delta = getattr(choice, "delta", None) or getattr(choice, "message", None)
                    content_piece = None
                    if delta is not None:
                        # delta 可能是一个对象，包含 content 字段
                        content_piece = getattr(delta, "content", None)
                        if content_piece is None and isinstance(delta, dict):
                            content_piece = delta.get("content")
                    if content_piece:
                        full_text.append(content_piece)
                        yield {"type": "delta", "delta": content_piece}
                except Exception as inner_e:
                    # 出现解析问题时不中断整体流
                    logger.warning(f"Stream chunk parse warning: {inner_e}")
                    continue
            
            # 结束块（包含完整拼接文本，方便前端一次性拿到最终内容）
            yield {"type": "done", "conversation_id": conversation_id, "text": "".join(full_text)}
            
        except Exception as e:
            logger.error(f"Stream chat processing failed: {e}")
            # 将错误以结构化形式返回
            yield {"error": f"抱歉，处理您的消息时出现了错误：{str(e)}"}


# Global chat service instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
