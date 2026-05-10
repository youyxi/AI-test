"""
AI Chat Hub - 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .core.config import settings
from .core.database import init_db
from .adapters import init_adapters
from .api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时初始化
    await init_db()
    init_adapters(settings)
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    yield
    
    # 关闭时清理
    pass


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="AI对话聚合平台 - 统一接入多种AI模型",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
