"""
聊天服务
处理聊天请求的核心业务逻辑
"""
from typing import AsyncGenerator, List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..adapters import adapter_manager, ChatResult
from ..models import Conversation, Message


class ChatService:
    """聊天服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        provider: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[int] = None
    ) -> ChatResult:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            model: 模型名称
            provider: 提供商
            temperature: 温度参数
            max_tokens: 最大token数
            conversation_id: 对话ID
            
        Returns:
            ChatResult: 聊天结果
        """
        # 获取适配器
        adapter = adapter_manager.get_adapter(provider)
        if not adapter:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        if not adapter.is_configured():
            raise ValueError(f"模型提供商 {provider} 未配置API密钥")
        
        # 发送请求
        result = await adapter.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 保存消息到数据库
        if conversation_id:
            await self._save_messages(
                conversation_id=conversation_id,
                messages=messages,
                response=result
            )
        
        return result
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        provider: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天请求
        
        Yields:
            str: 流式输出的内容片段
        """
        # 获取适配器
        adapter = adapter_manager.get_adapter(provider)
        if not adapter:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        if not adapter.is_configured():
            raise ValueError(f"模型提供商 {provider} 未配置API密钥")
        
        # 流式发送请求
        async for chunk in adapter.stream_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk
    
    async def _save_messages(
        self,
        conversation_id: int,
        messages: List[Dict[str, str]],
        response: ChatResult
    ):
        """保存消息到数据库"""
        # 保存用户消息
        for msg in messages:
            if msg["role"] == "user":
                user_msg = Message(
                    conversation_id=conversation_id,
                    role="user",
                    content=msg["content"]
                )
                self.db.add(user_msg)
        
        # 保存助手回复
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            tokens=response.usage.get("completion_tokens", 0) if response.usage else 0
        )
        self.db.add(assistant_msg)
        
        await self.db.commit()
    
    async def append_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ) -> Optional[Conversation]:
        """追加消息到对话"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def create_conversation(
        self,
        title: str,
        model: str,
        provider: str,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> Conversation:
        """创建新对话"""
        conversation = Conversation(
            title=title,
            model=model,
            provider=provider
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        if messages:
            for msg in messages:
                message = Message(
                    conversation_id=conversation.id,
                    role=msg["role"],
                    content=msg["content"]
                )
                self.db.add(message)
            await self.db.commit()
            await self.db.refresh(conversation)
        
        return conversation
    
    async def update_conversation(
        self,
        conversation_id: int,
        title: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Conversation]:
        """更新对话"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        if title is not None:
            conversation.title = title
        
        if messages is not None:
            # 清除旧消息
            from sqlalchemy import delete
            await self.db.execute(
                delete(Message).where(Message.conversation_id == conversation_id)
            )
            # 添加新消息
            for msg in messages:
                message = Message(
                    conversation_id=conversation_id,
                    role=msg["role"],
                    content=msg["content"]
                )
                self.db.add(message)
        
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """获取对话"""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_conversations(self, limit: int = 50) -> List[Conversation]:
        """获取对话列表"""
        result = await self.db.execute(
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def delete_conversation(self, conversation_id: int) -> bool:
        """删除对话"""
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            await self.db.delete(conversation)
            await self.db.commit()
            return True
        return False
