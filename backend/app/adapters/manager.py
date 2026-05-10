"""
AI模型适配器管理器
统一管理所有模型适配器
"""
from typing import Dict, List, Optional, Type
from .base import BaseAdapter
from .openai import OpenAIAdapter
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .domestic import BaiduAdapter, QwenAdapter, ZhipuAdapter
from .local import OllamaAdapter, VLLMAdapter


class AdapterManager:
    """适配器管理器"""
    
    # 注册的适配器类
    ADAPTER_CLASSES: Dict[str, Type[BaseAdapter]] = {
        "openai": OpenAIAdapter,
        "claude": ClaudeAdapter,
        "gemini": GeminiAdapter,
        "baidu": BaiduAdapter,
        "qwen": QwenAdapter,
        "zhipu": ZhipuAdapter,
        "ollama": OllamaAdapter,
        "vllm": VLLMAdapter,
    }
    
    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
    
    def register_adapter(self, provider: str, adapter: BaseAdapter):
        """注册适配器"""
        self._adapters[provider] = adapter
    
    def get_adapter(self, provider: str) -> Optional[BaseAdapter]:
        """获取适配器"""
        return self._adapters.get(provider)
    
    def get_all_adapters(self) -> Dict[str, BaseAdapter]:
        """获取所有适配器"""
        return self._adapters
    
    def get_configured_providers(self) -> List[str]:
        """获取已配置的提供商列表"""
        return [
            provider for provider, adapter in self._adapters.items()
            if adapter.is_configured()
        ]
    
    @classmethod
    def get_provider_info(cls) -> List[Dict]:
        """获取所有提供商信息"""
        providers = []
        for provider_id, adapter_class in cls.ADAPTER_CLASSES.items():
            try:
                # 创建临时实例获取模型列表
                temp_adapter = adapter_class({})
                providers.append({
                    "id": provider_id,
                    "name": adapter_class.provider_name,
                    "models": temp_adapter.get_models(),
                    "type": cls._get_provider_type(provider_id)
                })
            except Exception as e:
                # 如果创建实例失败，仍然返回基本信息
                providers.append({
                    "id": provider_id,
                    "name": adapter_class.provider_name,
                    "models": [],
                    "type": cls._get_provider_type(provider_id)
                })
        return providers
    
    @staticmethod
    def _get_provider_type(provider: str) -> str:
        """获取提供商类型"""
        commercial = ["openai", "claude", "gemini"]
        domestic = ["baidu", "qwen", "zhipu", "spark"]
        local = ["ollama", "vllm"]
        
        if provider in commercial:
            return "commercial"
        elif provider in domestic:
            return "domestic"
        elif provider in local:
            return "local"
        return "open_source"


# 全局适配器管理器实例
adapter_manager = AdapterManager()


def init_adapters(settings) -> AdapterManager:
    """
    初始化所有适配器
    
    Args:
        settings: 配置对象
        
    Returns:
        AdapterManager: 适配器管理器实例
    """
    # OpenAI
    if settings.OPENAI_API_KEY:
        adapter_manager.register_adapter(
            "openai",
            OpenAIAdapter({
                "api_key": settings.OPENAI_API_KEY,
                "base_url": settings.OPENAI_BASE_URL
            })
        )
    
    # Claude
    if settings.ANTHROPIC_API_KEY:
        adapter_manager.register_adapter(
            "claude",
            ClaudeAdapter({"api_key": settings.ANTHROPIC_API_KEY})
        )
    
    # Gemini
    if settings.GOOGLE_API_KEY:
        adapter_manager.register_adapter(
            "gemini",
            GeminiAdapter({"api_key": settings.GOOGLE_API_KEY})
        )
    
    # 百度文心一言
    if settings.BAIDU_API_KEY and settings.BAIDU_SECRET_KEY:
        adapter_manager.register_adapter(
            "baidu",
            BaiduAdapter({
                "api_key": settings.BAIDU_API_KEY,
                "secret_key": settings.BAIDU_SECRET_KEY
            })
        )
    
    # 通义千问
    if settings.QWEN_API_KEY:
        adapter_manager.register_adapter(
            "qwen",
            QwenAdapter({"api_key": settings.QWEN_API_KEY})
        )
    
    # 智谱AI
    if settings.ZHIPU_API_KEY:
        adapter_manager.register_adapter(
            "zhipu",
            ZhipuAdapter({"api_key": settings.ZHIPU_API_KEY})
        )
    
    # Ollama (本地，默认启用)
    adapter_manager.register_adapter(
        "ollama",
        OllamaAdapter({"base_url": settings.OLLAMA_BASE_URL})
    )
    
    return adapter_manager
