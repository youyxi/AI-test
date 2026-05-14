"""
对话API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..core.database import get_db
from ..models import (
    ConversationCreate, ConversationUpdate, ConversationResponse, ChatMessage,
    SuccessResponse, MessageCreate
)
from ..services import ChatService

router = APIRouter(prefix="/conversations", tags=["对话管理"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新对话
    """
    service = ChatService(db)
    
    conversation = await service.create_conversation(
        title=request.title,
        model=request.model,
        provider=request.provider,
        messages=request.messages or []
    )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        model=conversation.model,
        provider=conversation.provider,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            ChatMessage(role=m.role, content=m.content)
            for m in conversation.messages
        ]
    )


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话列表
    """
    service = ChatService(db)
    conversations = await service.get_conversations(limit=limit)
    
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            model=c.model,
            provider=c.provider,
            created_at=c.created_at,
            updated_at=c.updated_at,
            messages=[]
        )
        for c in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话详情
    """
    service = ChatService(db)
    conversation = await service.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = [
        ChatMessage(role=m.role, content=m.content)
        for m in conversation.messages
    ]
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        model=conversation.model,
        provider=conversation.provider,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages
    )


@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
async def append_message(
    conversation_id: int,
    request: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    追加消息到对话
    """
    service = ChatService(db)
    conversation = await service.append_message(
        conversation_id=conversation_id,
        role=request.role,
        content=request.content
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = [
        ChatMessage(role=m.role, content=m.content)
        for m in conversation.messages
    ]
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        model=conversation.model,
        provider=conversation.provider,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    request: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新对话
    """
    service = ChatService(db)
    conversation = await service.update_conversation(
        conversation_id=conversation_id,
        title=request.title,
        messages=request.messages
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        model=conversation.model,
        provider=conversation.provider,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            ChatMessage(role=m.role, content=m.content)
            for m in conversation.messages
        ]
    )


@router.delete("/{conversation_id}", response_model=SuccessResponse)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除对话
    """
    service = ChatService(db)
    success = await service.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return SuccessResponse(message="对话已删除")
