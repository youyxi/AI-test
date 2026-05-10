"""
聊天API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from ..core.database import get_db
from ..models import (
    ChatRequest, ChatResponse, ChatMessage,
    ConversationCreate, ConversationResponse,
    ModelInfo, ProviderInfo, SuccessResponse
)
from ..services import ChatService
from ..adapters import adapter_manager, AdapterManager

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/completions", response_model=ChatResponse)
async def chat_completions(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发送聊天请求
    """
    try:
        service = ChatService(db)
        
        # 转换消息格式
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        result = await service.chat(
            messages=messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            id=f"chat-{request.conversation_id or 'new'}",
            content=result.content,
            model=result.model,
            provider=result.provider,
            usage=result.usage
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天请求失败: {str(e)}")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    流式聊天请求
    """
    try:
        service = ChatService(db)
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        async def generate():
            full_content = ""
            async for chunk in service.stream_chat(
                messages=messages,
                model=request.model,
                provider=request.provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                full_content += chunk
                # SSE格式
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式聊天请求失败: {str(e)}")


@router.get("/providers", response_model=List[ProviderInfo])
async def get_providers():
    """
    获取所有模型提供商
    """
    providers = AdapterManager.get_provider_info()
    
    result = []
    for p in providers:
        adapter = adapter_manager.get_adapter(p["id"])
        models = [
            ModelInfo(
                id=m["id"],
                name=m["name"],
                provider=p["id"],
                provider_name=p["name"],
                type=p["type"],
                max_tokens=m.get("max_tokens", 4096),
                supports_stream=m.get("supports_stream", True),
                supports_vision=m.get("supports_vision", False)
            )
            for m in p["models"]
        ]
        
        result.append(ProviderInfo(
            id=p["id"],
            name=p["name"],
            models=models,
            configured=adapter.is_configured() if adapter else False
        ))
    
    return result


@router.get("/models", response_model=List[ModelInfo])
async def get_models():
    """
    获取所有可用模型
    """
    providers = AdapterManager.get_provider_info()
    
    models = []
    for p in providers:
        adapter = adapter_manager.get_adapter(p["id"])
        is_configured = adapter.is_configured() if adapter else False
        
        for m in p["models"]:
            models.append(ModelInfo(
                id=m["id"],
                name=m["name"],
                provider=p["id"],
                provider_name=p["name"],
                type=p["type"],
                max_tokens=m.get("max_tokens", 4096),
                supports_stream=m.get("supports_stream", True),
                supports_vision=m.get("supports_vision", False)
            ))
    
    return models
