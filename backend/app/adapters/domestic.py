"""
国内大模型适配器
支持文心一言、通义千问、讯飞星火、智谱AI
"""
from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
import json
import hashlib
import time
from .base import BaseAdapter, ChatResult


class BaiduAdapter(BaseAdapter):
    """百度文心一言适配器"""
    
    provider = "baidu"
    provider_name = "百度文心一言"
    
    MODELS = [
        {"id": "ernie-4.0-8k", "name": "文心一言 4.0", "max_tokens": 8192},
        {"id": "ernie-3.5-8k", "name": "文心一言 3.5", "max_tokens": 8192},
        {"id": "ernie-speed-8k", "name": "文心一言 Speed", "max_tokens": 8192},
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_token = None
        self.token_expire_time = 0
    
    async def _get_access_token(self) -> str:
        """获取access_token"""
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.config.get('api_key')}&client_secret={self.config.get('secret_key')}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            data = response.json()
            self.access_token = data.get("access_token")
            self.token_expire_time = time.time() + data.get("expires_in", 86400) - 300
            return self.access_token
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResult:
        """发送聊天请求"""
        if not self.is_configured():
            raise ValueError("百度API Key未配置")
        
        token = await self._get_access_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={token}"
        
        payload = {
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_output_tokens"] = max_tokens
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()
        
        return ChatResult(
            content=data.get("result", ""),
            model=model,
            provider=self.provider,
            usage=data.get("usage"),
            finish_reason=data.get("finish_reason")
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
        if not self.is_configured():
            raise ValueError("百度API Key未配置")
        
        token = await self._get_access_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={token}&stream=true"
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data.get("result"):
                            yield data["result"]
    
    def get_models(self) -> List[Dict[str, Any]]:
        return self.MODELS


class QwenAdapter(BaseAdapter):
    """阿里通义千问适配器"""
    
    provider = "qwen"
    provider_name = "阿里通义千问"
    
    MODELS = [
        {"id": "qwen-turbo", "name": "通义千问 Turbo", "max_tokens": 8192},
        {"id": "qwen-plus", "name": "通义千问 Plus", "max_tokens": 32768},
        {"id": "qwen-max", "name": "通义千问 Max", "max_tokens": 32768},
        {"id": "qwen-vl-max", "name": "通义千问 VL", "max_tokens": 8192, "supports_vision": True},
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
        if not self.is_configured():
            raise ValueError("通义千问API Key未配置")
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {"temperature": temperature}
        }
        if max_tokens:
            payload["parameters"]["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()
        
        output = data.get("output", {})
        return ChatResult(
            content=output.get("text", ""),
            model=model,
            provider=self.provider,
            usage=data.get("usage"),
            finish_reason=output.get("finish_reason")
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
        if not self.is_configured():
            raise ValueError("通义千问API Key未配置")
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }
        
        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {"temperature": temperature, "incremental_output": True}
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = json.loads(line[5:])
                        if data.get("output", {}).get("text"):
                            yield data["output"]["text"]
    
    def get_models(self) -> List[Dict[str, Any]]:
        return self.MODELS


class ZhipuAdapter(BaseAdapter):
    """智谱AI适配器"""
    
    provider = "zhipu"
    provider_name = "智谱AI"
    
    MODELS = [
        {"id": "glm-4", "name": "GLM-4", "max_tokens": 128000},
        {"id": "glm-4-flash", "name": "GLM-4 Flash", "max_tokens": 128000},
        {"id": "glm-4v", "name": "GLM-4V", "max_tokens": 8192, "supports_vision": True},
        {"id": "chatglm3-6b", "name": "ChatGLM3-6B", "max_tokens": 8192},
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
        if not self.is_configured():
            raise ValueError("智谱API Key未配置")
        
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
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
        if not self.is_configured():
            raise ValueError("智谱API Key未配置")
        
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
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
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:])
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except:
                            pass
    
    def get_models(self) -> List[Dict[str, Any]]:
        return self.MODELS
