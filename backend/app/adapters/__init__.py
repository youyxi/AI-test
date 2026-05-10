"""
AI模型适配器模块
"""
from .base import BaseAdapter, ChatResult
from .openai import OpenAIAdapter
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .domestic import BaiduAdapter, QwenAdapter, ZhipuAdapter
from .local import OllamaAdapter, VLLMAdapter
from .manager import AdapterManager, adapter_manager, init_adapters

__all__ = [
    "BaseAdapter", "ChatResult",
    "OpenAIAdapter", "ClaudeAdapter", "GeminiAdapter",
    "BaiduAdapter", "QwenAdapter", "ZhipuAdapter",
    "OllamaAdapter", "VLLMAdapter",
    "AdapterManager", "adapter_manager", "init_adapters"
]
