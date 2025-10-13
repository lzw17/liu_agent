"""LLM service for handling multiple LLM providers."""
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import openai
import anthropic
import httpx
from ..core import get_config, logger
from ..models.schemas import ChatMessage


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> str:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    async def stream_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = openai.AsyncOpenAI(
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.openai.com/v1"),
            timeout=config.get("timeout", 30)
        )
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> str:
        """Generate chat completion using OpenAI."""
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self.config.get("model", "gpt-4"),
                messages=openai_messages,
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.7)),
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise
    
    async def stream_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion using OpenAI."""
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.config.get("model", "gpt-4"),
                messages=openai_messages,
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.7)),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = openai.AsyncOpenAI(
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.deepseek.com/v1"),
            timeout=config.get("timeout", 30)
        )
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> str:
        """Generate chat completion using DeepSeek."""
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self.config.get("model", "deepseek-chat"),
                messages=openai_messages,
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.7)),
                stream=False
            )
            
            # 处理不同格式的响应
            try:
                return response.choices[0].message.content
            except AttributeError:
                # 尝试直接访问字典格式的响应
                if isinstance(response.choices[0].message, dict):
                    return response.choices[0].message.get('content', '')
                raise
            
        except Exception as e:
            logger.error(f"DeepSeek completion error: {e}")
            raise
    
    async def stream_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion using DeepSeek."""
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.config.get("model", "deepseek-chat"),
                messages=openai_messages,
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.7)),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"DeepSeek streaming error: {e}")
            raise


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.anthropic.com/v1"),
            timeout=config.get("timeout", 30)
        )
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> str:
        """Generate chat completion using Anthropic."""
        try:
            # Convert messages to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    user_messages.append({"role": msg.role, "content": msg.content})
            
            response = await self.client.messages.create(
                model=self.config.get("model", "claude-3-sonnet-20240229"),
                system=system_message if system_message else None,
                messages=user_messages,
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.7))
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic completion error: {e}")
            raise
    
    async def stream_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion using Anthropic."""
        try:
            # Convert messages to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    user_messages.append({"role": msg.role, "content": msg.content})
            
            async with self.client.messages.stream(
                model=self.config.get("model", "claude-3-sonnet-20240229"),
                system=system_message if system_message else None,
                messages=user_messages,
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.7))
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434/v1")
        self.client = httpx.AsyncClient(timeout=config.get("timeout", 60))
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> str:
        """Generate chat completion using Ollama."""
        try:
            ollama_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.config.get("model", "llama2"),
                    "messages": ollama_messages,
                    "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                    "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                    "stream": False
                }
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Ollama completion error: {e}")
            raise
    
    async def stream_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion using Ollama."""
        try:
            ollama_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.config.get("model", "llama2"),
                    "messages": ollama_messages,
                    "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                    "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                    "stream": True
                }
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            try:
                                import json
                                chunk = json.loads(data)
                                if chunk["choices"][0]["delta"].get("content"):
                                    yield chunk["choices"][0]["delta"]["content"]
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise


class LLMService:
    """Service for managing multiple LLM providers."""
    
    def __init__(self):
        self.config = get_config()
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize LLM providers based on configuration."""
        # Primary LLM provider
        primary_config = self.config.llm.model_dump()
        provider_type = primary_config.get("provider", "openai")
        
        self.providers["primary"] = self._create_provider(provider_type, primary_config)
        
        # Alternative LLM providers
        for name, llm_config in self.config.llm_configs.items():
            config_dict = llm_config.model_dump()
            provider_type = config_dict.get("provider", "openai")
            self.providers[name] = self._create_provider(provider_type, config_dict)
    
    def _create_provider(self, provider_type: str, config: Dict[str, Any]) -> BaseLLMProvider:
        """Create a provider instance based on type."""
        if provider_type == "openai":
            return OpenAIProvider(config)
        elif provider_type == "anthropic":
            return AnthropicProvider(config)
        elif provider_type == "deepseek":
            return DeepSeekProvider(config)
        elif provider_type == "ollama":
            return OllamaProvider(config)
        else:
            logger.warning(f"Unknown provider type: {provider_type}, defaulting to OpenAI")
            return OpenAIProvider(config)
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        provider: str = "primary",
        **kwargs
    ) -> str:
        """Generate chat completion using specified provider."""
        if provider not in self.providers:
            logger.warning(f"Provider {provider} not found, using primary")
            provider = "primary"
        
        return await self.providers[provider].chat_completion(messages, **kwargs)
    
    async def stream_completion(
        self, 
        messages: List[ChatMessage], 
        provider: str = "primary",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion using specified provider."""
        if provider not in self.providers:
            logger.warning(f"Provider {provider} not found, using primary")
            provider = "primary"
        
        async for chunk in self.providers[provider].stream_completion(messages, **kwargs):
            yield chunk
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
