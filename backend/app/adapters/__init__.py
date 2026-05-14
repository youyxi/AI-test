"""
AI模型适配器模块
"""
from .base import BaseAdapter, ChatResult
from .manager import AdapterManager, adapter_manager, init_adapters

__all__ = [
    "BaseAdapter", "ChatResult",
    "AdapterManager", "adapter_manager", "init_adapters"
]
