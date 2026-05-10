from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
from .base import BaseAdapter, ChatResult


class DeepSeekAdapter(BaseAdapter):
    """DeepSeek模型适配器"""

    provider = "deepseek"
    provider_name = "DeepSeek"

    # 声明支持的模型
    MODELS = [
        {"id": "deepseek-chat", "name": "DeepSeek Chat", "max_tokens": 32768},
        {"id": "deepseek-coder", "name": "DeepSeek Coder", "max_tokens": 16384},
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResult:
        """发送聊天请求"""
        url = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        choice = data.get("choices", [{}])[0]
        return ChatResult(
            content=choice.get("message", {}).get("content", ""),
            model=model,
            provider=self.provider,
            usage=data.get("usage"),
            finish_reason=choice.get("finish_reason")
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
        url = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        data = json.loads(line[6:])
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            yield content

    def get_models(self) -> List[Dict[str, Any]]:
        return self.MODELS