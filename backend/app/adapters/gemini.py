"""
Gemini适配器
支持Google Gemini系列模型
"""
from typing import AsyncGenerator, List, Dict, Any, Optional
import google.generativeai as genai
from .base import BaseAdapter, ChatResult


class GeminiAdapter(BaseAdapter):
    """Google Gemini模型适配器"""
    
    provider = "gemini"
    provider_name = "Google Gemini"
    
    # 支持的模型列表
    MODELS = [
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "max_tokens": 1000000, "supports_vision": True},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "max_tokens": 1000000, "supports_vision": True},
        {"id": "gemini-pro", "name": "Gemini Pro", "max_tokens": 32760},
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if self.is_configured() and config.get("api_key"):
            try:
                genai.configure(api_key=config.get("api_key"))
            except Exception:
                pass  # 配置失败时不抛出异常
    
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
            raise ValueError("Google API Key未配置")
        
        # 转换消息格式
        history = []
        user_message = ""
        for msg in messages:
            if msg["role"] == "user":
                user_message = msg["content"]
                history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                history.append({"role": "model", "parts": [msg["content"]]})
        
        # 创建模型实例
        model_instance = genai.GenerativeModel(model)
        
        # 生成响应
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        response = await model_instance.generate_content_async(
            user_message,
            generation_config=generation_config
        )
        
        return ChatResult(
            content=response.text,
            model=model,
            provider=self.provider,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            } if hasattr(response, 'usage_metadata') else None,
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else None
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
            raise ValueError("Google API Key未配置")
        
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        model_instance = genai.GenerativeModel(model)
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        response = await model_instance.generate_content_async(
            user_message,
            generation_config=generation_config,
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        return self.MODELS
