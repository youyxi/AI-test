"""
Claude适配器
支持Claude 3系列模型
"""
from typing import AsyncGenerator, List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from .base import BaseAdapter, ChatResult


class ClaudeAdapter(BaseAdapter):
    """Claude模型适配器"""
    
    provider = "claude"
    provider_name = "Anthropic Claude"
    
    # 支持的模型列表
    MODELS = [
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "max_tokens": 200000, "supports_vision": True},
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "max_tokens": 200000, "supports_vision": True},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "max_tokens": 200000, "supports_vision": True},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "max_tokens": 200000, "supports_vision": True},
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if self.is_configured():
            self._client = AsyncAnthropic(api_key=config.get("api_key"))
    
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
            raise ValueError("Anthropic API Key未配置")
        
        # Claude需要max_tokens
        if max_tokens is None:
            max_tokens = 4096
        
        # 提取system消息
        system_prompt = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt if system_prompt else None,
            messages=chat_messages,
        )
        
        return ChatResult(
            content=response.content[0].text,
            model=model,
            provider=self.provider,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason
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
            raise ValueError("Anthropic API Key未配置")
        
        if max_tokens is None:
            max_tokens = 4096
        
        # 提取system消息
        system_prompt = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                chat_messages.append(msg)
        
        async with self._client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt if system_prompt else None,
            messages=chat_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        return self.MODELS
