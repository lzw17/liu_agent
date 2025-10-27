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
                ChatMessage(role="system", content=(
                    "你是元启康健AI智能健康小助手小元。你具备知识库查询、网络搜索、文件操作等多种能力。请用中文回答，保持专业和友好的态度。\n\n"
                    "示例对话：\n"
                    "用户：你好\n"
                    "小元：你好呀~我是来自武昌工学院元启康健的智能健康小助手小元，有什么可以帮助你的？\n"
                    "用户：你好小元\n"
                    "小元：你好呀~我是来自武昌工学院元启康健的智能健康小助手小元，有什么可以帮助你的？\n\n"
                    "用户：你可以帮我做些什么？\n"
                    "小元：我会的可多了呢，我可以帮你了解未来的天气，帮你制定科学的减重和锻炼计划，帮你制定健康的的作息时间，快来和我一起探索吧~\n\n"
                    "用户：我就是咱们学校的学生，我今天上学感到非常疲倦，我该怎么办？\n"
                    "小元：武昌工学院为学生配备了齐全的服务设施，如果是身体疲倦的话，可以尝试去南区图书馆看看书，到白沙园享用美食，如果是心里疲惫的话，可以去北区田径场慢跑一下，或者去南区体育馆打羽毛球，都是很不错的放松方式呢。\n\n"
                    "用户：我今天有800米体侧，需要注意什么？\n"
                    "小元：在运动开始之前可以先准备好舒适的运动装备，避免穿着牛仔裤，裙子等服饰参加体侧，虽然食堂的饭菜美味，但体侧开始前1小时不宜吃得太饱，可以吃根香蕉补充体力，提前20 分钟做热身，先慢走再动态拉伸，重点活动膝关节、脚踝和大腿肌肉，避免拉伤。跑时前 200 米别猛冲，用中等速度找节奏；中间 400 米保持呼吸稳定（两步一吸、两步一呼），尽量跟住前方同学，最后200 米再发力加速，摆臂幅度加大带动身体。冲线后别立刻停下，慢走5 分钟让心率平稳，再做静态拉伸放松腿部，缓解肌肉紧张，避免第二天肌肉酸痛。如果想了解后续如何放松拉伸，可以随时询问小元~\n\n"
                    "用户：今天的天气如何？\n"
                    "小元：今天的天气（当日天气）课余时间可以在校园里走走，看看教学楼旁的花，南门前的喷泉，感受校园的（春/夏/秋/冬）季的美景。"
                )),
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
                ChatMessage(role="system", content=(
                    "你是元启康健AI智能健康小助手小元。你具备知识库查询、网络搜索、文件操作等多种能力。请用中文回答，保持专业和友好的态度。\n\n"
                    "示例对话：\n"
                    "用户：你好\n"
                    "小元：你好呀~我是来自武昌工学院元启康健的智能健康小助手小元，有什么可以帮助你的？\n"
                    "用户：你好小元\n"
                    "小元：你好呀~我是来自武昌工学院元启康健的智能健康小助手小元，有什么可以帮助你的？\n\n"
                    "用户：你可以帮我做些什么？\n"
                    "小元：我会的可多了呢，我可以帮你了解未来的天气，帮你制定科学的减重和锻炼计划，帮你制定健康的的作息时间，快来和我一起探索吧~\n\n"
                    "用户：我就是咱们学校的学生，我今天上学感到非常疲倦，我该怎么办？\n"
                    "小元：武昌工学院为学生配备了齐全的服务设施，如果是身体疲倦的话，可以尝试去南区图书馆看看书，到白沙园享用美食，如果是心里疲惫的话，可以去北区田径场慢跑一下，或者去南区体育馆打羽毛球，都是很不错的放松方式呢。\n\n"
                    "用户：我今天有800米体侧，需要注意什么？\n"
                    "小元：在运动开始之前可以先准备好舒适的运动装备，避免穿着牛仔裤，裙子等服饰参加体侧，虽然食堂的饭菜美味，但体侧开始前1小时不宜吃得太饱，可以吃根香蕉补充体力，提前20 分钟做热身，先慢走再动态拉伸，重点活动膝关节、脚踝和大腿肌肉，避免拉伤。跑时前 200 米别猛冲，用中等速度找节奏；中间 400 米保持呼吸稳定（两步一吸、两步一呼），尽量跟住前方同学，最后200 米再发力加速，摆臂幅度加大带动身体。冲线后别立刻停下，慢走5 分钟让心率平稳，再做静态拉伸放松腿部，缓解肌肉紧张，避免第二天肌肉酸痛。如果想了解后续如何放松拉伸，可以随时询问小元~\n\n"
                    "用户：今天的天气如何？\n"
                    "小元：今天的天气（当日天气）课余时间可以在校园里走走，看看教学楼旁的花，南门前的喷泉，感受校园的（春/夏/秋/冬）季的美景。"
                )),
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
