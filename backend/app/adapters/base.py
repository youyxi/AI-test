"""
AI模型适配器基类
定义统一的模型调用接口
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatResult:
    """聊天结果"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class BaseAdapter(ABC):
    """AI模型适配器基类"""
    
    provider: str = "base"
    provider_name: str = "Base Provider"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._client = None
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResult:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            ChatResult: 聊天结果
        """
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天请求
        
        Yields:
            str: 流式输出的内容片段
        """
        pass
    
    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """
        获取支持的模型列表
        
        Returns:
            List[Dict]: 模型信息列表
        """
        pass
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.config)
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """格式化消息（子类可重写）"""
        return messages
