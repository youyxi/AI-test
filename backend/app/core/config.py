"""
核心配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "AI Chat Hub"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ai_chat.db"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Claude配置
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Gemini配置
    GOOGLE_API_KEY: Optional[str] = None
    
    # 百度文心一言配置
    BAIDU_API_KEY: Optional[str] = None
    BAIDU_SECRET_KEY: Optional[str] = None
    
    # 阿里通义千问配置
    QWEN_API_KEY: Optional[str] = None
    
    # 讯飞星火配置
    SPARK_APP_ID: Optional[str] = None
    SPARK_API_KEY: Optional[str] = None
    SPARK_API_SECRET: Optional[str] = None
    
    # 智谱AI配置
    ZHIPU_API_KEY: Optional[str] = None
    
    # 本地模型配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
