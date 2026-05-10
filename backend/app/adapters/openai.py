"""
OpenAI适配器
支持GPT-4, GPT-3.5等模型
"""
from typing import AsyncGenerator, List, Dict, Any, Optional
from openai import AsyncOpenAI
from .base import BaseAdapter, ChatResult


class OpenAIAdapter(BaseAdapter):
    """OpenAI模型适配器"""
    
    provider = "openai"
    provider_name = "OpenAI"
    
    # 支持的模型列表
    MODELS = [
        {"id": "gpt-4o", "name": "GPT-4o", "max_tokens": 128000, "supports_vision": True},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "max_tokens": 128000, "supports_vision": True},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "max_tokens": 128000, "supports_vision": True},
        {"id": "gpt-4", "name": "GPT-4", "max_tokens": 8192},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "max_tokens": 16384},
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if self.is_configured():
            self._client = AsyncOpenAI(
                api_key=config.get("api_key"),
                base_url=config.get("base_url", "https://api.openai.com/v1")
            )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResult:
        """发送聊天请求"""
        if not self._client:
            raise ValueError("OpenAI API Key未配置")
        
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        choice = response.choices[0]
        return ChatResult(
            content=choice.message.content,
            model=model,
            provider=self.provider,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None,
            finish_reason=choice.finish_reason
        )
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        if not self._client:
            raise ValueError("OpenAI API Key未配置")
        
        stream = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        return self.MODELS
