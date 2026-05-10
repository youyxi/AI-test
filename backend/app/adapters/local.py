"""
本地模型适配器
支持Ollama、vLLM等本地部署模型
"""
from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
import json
from .base import BaseAdapter, ChatResult


class OllamaAdapter(BaseAdapter):
    """Ollama本地模型适配器"""
    
    provider = "ollama"
    provider_name = "Ollama (本地)"
    
    # 常用模型列表（实际模型取决于本地安装）
    COMMON_MODELS = [
        {"id": "llama3", "name": "Llama 3", "max_tokens": 8192},
        {"id": "llama3:70b", "name": "Llama 3 70B", "max_tokens": 8192},
        {"id": "qwen2", "name": "Qwen 2", "max_tokens": 32768},
        {"id": "qwen2:72b", "name": "Qwen 2 72B", "max_tokens": 32768},
        {"id": "mistral", "name": "Mistral", "max_tokens": 8192},
        {"id": "codellama", "name": "Code Llama", "max_tokens": 16384},
        {"id": "deepseek-coder", "name": "DeepSeek Coder", "max_tokens": 16384},
        {"id": "chatglm3", "name": "ChatGLM3", "max_tokens": 8192},
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
    
    async def _get_installed_models(self) -> List[Dict[str, Any]]:
        """获取本地已安装的模型"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("models", [])
        except:
            pass
        return []
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResult:
        """发送聊天请求"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(url, json=payload)
            data = response.json()
        
        message = data.get("message", {})
        return ChatResult(
            content=message.get("content", ""),
            model=model,
            provider=self.provider,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
            },
            finish_reason="stop" if data.get("done") else None
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
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    try:
                        data = json.loads(line)
                        if data.get("message", {}).get("content"):
                            yield data["message"]["content"]
                    except:
                        pass
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        return self.COMMON_MODELS
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """获取本地可用的模型"""
        installed = await self._get_installed_models()
        if installed:
            return [{"id": m["name"], "name": m["name"], "max_tokens": 8192} for m in installed]
        return self.COMMON_MODELS
    
    def is_configured(self) -> bool:
        """Ollama只需要base_url，默认本地"""
        return bool(self.base_url)


class VLLMAdapter(BaseAdapter):
    """vLLM本地模型适配器"""
    
    provider = "vllm"
    provider_name = "vLLM (本地)"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:8000")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResult:
        """发送聊天请求（OpenAI兼容接口）"""
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 2048
        }
        
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(url, json=payload)
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
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 2048,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except:
                            pass
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        return [
            {"id": "local-model", "name": "本地模型", "max_tokens": 8192}
        ]
    
    def is_configured(self) -> bool:
        return bool(self.base_url)
