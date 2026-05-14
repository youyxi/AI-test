"""
AI模型适配器管理器
统一管理所有模型适配器
"""
from typing import Dict, List, Optional, Type
from .base import BaseAdapter


# 安全导入适配器
def _safe_import_adapters():
    """安全导入适配器，处理所有可能的导入错误"""
    adapter_classes = {}
    
    # 尝试导入各个适配器，捕获所有异常
    try:
        from .openai import OpenAIAdapter
        adapter_classes["openai"] = OpenAIAdapter
    except Exception:
        pass
    
    try:
        from .claude import ClaudeAdapter
        adapter_classes["claude"] = ClaudeAdapter
    except Exception:
        pass
    
    try:
        from .gemini import GeminiAdapter
        adapter_classes["gemini"] = GeminiAdapter
    except Exception:
        pass
    
    try:
        from .domestic import BaiduAdapter, QwenAdapter, ZhipuAdapter
        adapter_classes["baidu"] = BaiduAdapter
        adapter_classes["qwen"] = QwenAdapter
        adapter_classes["zhipu"] = ZhipuAdapter
    except Exception:
        pass
    
    try:
        from .local import OllamaAdapter, VLLMAdapter
        adapter_classes["ollama"] = OllamaAdapter
        adapter_classes["vllm"] = VLLMAdapter
    except Exception:
        pass
    
    return adapter_classes


class AdapterManager:
    """适配器管理器"""
    
    # 注册的适配器类（使用安全导入）
    ADAPTER_CLASSES: Dict[str, Type[BaseAdapter]] = _safe_import_adapters()
    
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
    # 安全导入各个适配器类
    adapters_available = AdapterManager.ADAPTER_CLASSES
    
    # OpenAI
    if "openai" in adapters_available and settings.OPENAI_API_KEY:
        try:
            OpenAIAdapter = adapters_available["openai"]
            adapter_manager.register_adapter(
                "openai",
                OpenAIAdapter({
                    "api_key": settings.OPENAI_API_KEY,
                    "base_url": settings.OPENAI_BASE_URL
                })
            )
        except Exception:
            pass
    
    # Claude
    if "claude" in adapters_available and settings.ANTHROPIC_API_KEY:
        try:
            ClaudeAdapter = adapters_available["claude"]
            adapter_manager.register_adapter(
                "claude",
                ClaudeAdapter({"api_key": settings.ANTHROPIC_API_KEY})
            )
        except Exception:
            pass
    
    # Gemini
    if "gemini" in adapters_available and settings.GOOGLE_API_KEY:
        try:
            GeminiAdapter = adapters_available["gemini"]
            adapter_manager.register_adapter(
                "gemini",
                GeminiAdapter({"api_key": settings.GOOGLE_API_KEY})
            )
        except Exception:
            pass
    
    # 百度文心一言
    if "baidu" in adapters_available and settings.BAIDU_API_KEY and settings.BAIDU_SECRET_KEY:
        try:
            BaiduAdapter = adapters_available["baidu"]
            adapter_manager.register_adapter(
                "baidu",
                BaiduAdapter({
                    "api_key": settings.BAIDU_API_KEY,
                    "secret_key": settings.BAIDU_SECRET_KEY
                })
            )
        except Exception:
            pass
    
    # 通义千问
    if "qwen" in adapters_available and settings.QWEN_API_KEY:
        try:
            QwenAdapter = adapters_available["qwen"]
            adapter_manager.register_adapter(
                "qwen",
                QwenAdapter({"api_key": settings.QWEN_API_KEY})
            )
        except Exception:
            pass
    
    # 智谱AI
    if "zhipu" in adapters_available and settings.ZHIPU_API_KEY:
        try:
            ZhipuAdapter = adapters_available["zhipu"]
            adapter_manager.register_adapter(
                "zhipu",
                ZhipuAdapter({"api_key": settings.ZHIPU_API_KEY})
            )
        except Exception:
            pass
    
    # Ollama (本地，默认启用)
    if "ollama" in adapters_available:
        try:
            OllamaAdapter = adapters_available["ollama"]
            adapter_manager.register_adapter(
                "ollama",
                OllamaAdapter({"base_url": settings.OLLAMA_BASE_URL})
            )
        except Exception:
            pass
    
    return adapter_manager
