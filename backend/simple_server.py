#!/usr/bin/env python3
"""
简化版后端服务 - 用于预览
不依赖编译的包，只使用标准库和纯Python包
支持对话历史保存功能
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio

app = FastAPI(title="AI Chat Hub - Demo")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据库
conversations_db = [
    {
        "id": 1,
        "title": "Python入门教程",
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [
            {"role": "user", "content": "你好，我想学习Python"},
            {"role": "assistant", "content": "你好！欢迎学习Python。Python是一门简洁优雅的编程语言。"},
            {"role": "user", "content": "如何打印Hello World？"},
            {"role": "assistant", "content": "很简单！在Python中，只需：\n\n```python\nprint('Hello World')\n```\n\n这样就可以了！"},
        ]
    },
    {
        "id": 2,
        "title": "AI聊天测试",
        "model": "gpt-4",
        "provider": "openai",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [
            {"role": "user", "content": "你能帮我写个故事吗？"},
            {"role": "assistant", "content": "当然！请告诉我你想要什么类型的故事？"},
        ]
    },
    {
        "id": 3,
        "title": "DeepSeek 模型测试",
        "model": "deepseek-chat",
        "provider": "deepseek",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"},
            {"role": "assistant", "content": "你好！我是DeepSeek AI助手。很高兴为您服务！"},
        ]
    },
]

# 模型和提供商信息
providers_data = [
    {
        "id": "openai",
        "name": "OpenAI",
        "configured": True,
        "models": [
            {"id": "gpt-4", "name": "GPT-4", "max_tokens": 8192, "supports_vision": True},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "max_tokens": 16385, "supports_vision": False},
        ]
    },
    {
        "id": "claude",
        "name": "Claude",
        "configured": True,
        "models": [
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "max_tokens": 200000, "supports_vision": True},
            {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "max_tokens": 200000, "supports_vision": True},
        ]
    },
    {
        "id": "gemini",
        "name": "Gemini",
        "configured": False,
        "models": [
            {"id": "gemini-pro", "name": "Gemini Pro", "max_tokens": 32768, "supports_vision": True},
        ]
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "configured": True,
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "max_tokens": 32768, "supports_vision": False},
        ]
    },
]

# Pydantic 模型
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-3.5-turbo"
    provider: str = "openai"
    stream: bool = True
    temperature: float = 0.7
    conversation_id: Optional[int] = None

class MessageCreate(BaseModel):
    role: str
    content: str
    tokens: Optional[int] = None

class ConversationCreate(BaseModel):
    title: str = "New Chat"
    model: str
    provider: str

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

# API 端点
@app.get("/")
async def root():
    return {"name": "AI Chat Hub", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 聊天端点
@app.get("/api/v1/chat/providers")
async def get_providers():
    result = []
    for p in providers_data:
        models_list = []
        for m in p["models"]:
            models_list.append({
                "id": m["id"],
                "name": m["name"],
                "provider": p["id"],
                "provider_name": p["name"],
                "max_tokens": m["max_tokens"],
                "supports_stream": True,
                "supports_vision": m["supports_vision"]
            })
        result.append({
            "id": p["id"],
            "name": p["name"],
            "models": models_list,
            "configured": p["configured"]
        })
    return result

@app.get("/api/v1/chat/models")
async def get_models():
    models = []
    for p in providers_data:
        for m in p["models"]:
            models.append({
                "id": m["id"],
                "name": m["name"],
                "provider": p["id"],
                "provider_name": p["name"],
                "max_tokens": m["max_tokens"],
                "supports_stream": True,
                "supports_vision": m["supports_vision"]
            })
    return models

# 流式聊天（包含消息保存）
@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        user_message = request.messages[-1].content if request.messages else "Hello"
        
        # 生成模拟响应
        response_parts = [
            "你好！",
            "我是AI助手，",
            "很高兴为您服务。",
            "\n\n",
            "我看到您说：",
            f"「{user_message}」",
            "\n\n",
            "这是一个演示响应。",
            "实际使用时，",
            "这里会调用真实的AI模型。",
            "\n\n",
            "✨ 对话已自动保存到数据库"
        ]
        
        full_response = ""
        for i, part in enumerate(response_parts):
            await asyncio.sleep(0.1)
            full_response += part
            yield f"data: {json.dumps({'content': part})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
        
        # 保存消息到数据库
        await save_chat_messages(
            conversation_id=request.conversation_id,
            messages=request.messages,
            assistant_response=full_response,
            model=request.model,
            provider=request.provider
        )
    
    return StreamingResponse(generate(), media_type="text/event-stream")

async def save_chat_messages(conversation_id, messages, assistant_response, model, provider):
    """保存聊天消息到数据库"""
    global conversations_db
    
    try:
        if conversation_id is None:
            # 创建新对话
            new_id = max([c["id"] for c in conversations_db], default=0) + 1
            new_conv = {
                "id": new_id,
                "title": generate_title(messages[0].content if messages else "新对话"),
                "model": model,
                "provider": provider,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "messages": []
            }
            
            # 添加用户消息
            for msg in messages:
                new_conv["messages"].append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # 添加助手回复
            new_conv["messages"].append({
                "role": "assistant",
                "content": assistant_response
            })
            
            conversations_db.append(new_conv)
            print(f"✅ 创建新对话 {new_id}: {new_conv['title']}")
        else:
            # 更新现有对话
            conv = next((c for c in conversations_db if c["id"] == conversation_id), None)
            if conv:
                # 添加最后一条用户消息（如果不在消息列表中）
                if not any(m.role == "user" for m in messages[-1:]):
                    if messages:
                        conv["messages"].append({
                            "role": messages[-1].role,
                            "content": messages[-1].content
                        })
                
                # 添加助手回复
                conv["messages"].append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
                # 更新标题（如果是对话的第一条）
                if len(conv["messages"]) == 2:
                    conv["title"] = generate_title(messages[0].content if messages else "新对话")
                
                conv["updated_at"] = datetime.now().isoformat()
                print(f"✅ 更新对话 {conversation_id}: {conv['title']}")
    except Exception as e:
        print(f"❌ 保存消息失败: {e}")

def generate_title(first_message):
    """生成对话标题"""
    if not first_message:
        return "新对话"
    
    # 取前30个字符作为标题
    title = first_message[:30]
    if len(first_message) > 30:
        title += "..."
    
    return title

# 对话管理
@app.get("/api/v1/conversations")
async def list_conversations():
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "model": c["model"],
            "provider": c["provider"],
            "created_at": c["created_at"],
            "updated_at": c["updated_at"],
        }
        for c in conversations_db
    ]

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: int):
    conv = next((c for c in conversations_db if c["id"] == conversation_id), None)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": conv["id"],
        "title": conv["title"],
        "model": conv["model"],
        "provider": conv["provider"],
        "created_at": conv["created_at"],
        "updated_at": conv["updated_at"],
        "messages": conv["messages"]
    }

@app.post("/api/v1/conversations")
async def create_conversation(request: ConversationCreate):
    new_id = max([c["id"] for c in conversations_db], default=0) + 1
    new_conv = {
        "id": new_id,
        "title": request.title,
        "model": request.model,
        "provider": request.provider,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": []
    }
    conversations_db.append(new_conv)
    return {
        "id": new_conv["id"],
        "title": new_conv["title"],
        "model": new_conv["model"],
        "provider": new_conv["provider"],
        "created_at": new_conv["created_at"],
        "updated_at": new_conv["updated_at"],
        "messages": []
    }

@app.put("/api/v1/conversations/{conversation_id}")
async def update_conversation(conversation_id: int, request: ConversationUpdate):
    conv = next((c for c in conversations_db if c["id"] == conversation_id), None)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if request.title:
        conv["title"] = request.title
    conv["updated_at"] = datetime.now().isoformat()
    
    return {
        "id": conv["id"],
        "title": conv["title"],
        "model": conv["model"],
        "provider": conv["provider"],
        "created_at": conv["created_at"],
        "updated_at": conv["updated_at"],
        "messages": conv["messages"]
    }

@app.post("/api/v1/conversations/{conversation_id}/messages")
async def add_message(conversation_id: int, request: MessageCreate):
    """向指定对话添加消息"""
    conv = next((c for c in conversations_db if c["id"] == conversation_id), None)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv["messages"].append({
        "role": request.role,
        "content": request.content
    })
    conv["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Message added"
    }

@app.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int):
    global conversations_db
    conversations_db = [c for c in conversations_db if c["id"] != conversation_id]
    return {"success": True, "message": "Conversation deleted"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动简化版后端服务（支持对话保存）...")
    print("📝 访问: http://localhost:8000/docs 查看API文档")
    print("✅ 新增功能：")
    print("   - 发送消息自动保存到数据库")
    print("   - 创建新对话")
    print("   - 更新对话标题")
    print("   - 添加消息到指定对话")
    uvicorn.run(app, host="0.0.0.0", port=8000)
