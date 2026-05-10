# API使用指南

本文档介绍如何使用 AI Chat Hub 的 API 接口。

## 基础信息

- 基础URL: `http://localhost:8000/api/v1`
- 所有请求和响应均为 JSON 格式
- 支持 CORS 跨域请求

## 接口列表

### 1. 获取模型提供商列表

```
GET /chat/providers
```

**响应示例:**
```json
[
  {
    "id": "openai",
    "name": "OpenAI",
    "configured": true,
    "models": [
      {
        "id": "gpt-4",
        "name": "GPT-4",
        "max_tokens": 8192,
        "supports_stream": true,
        "supports_vision": false
      }
    ]
  }
]
```

### 2. 发送聊天请求

```
POST /chat/completions
```

**请求体:**
```json
{
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**响应示例:**
```json
{
  "id": "chat-123",
  "content": "你好！有什么我可以帮助你的吗？",
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 3. 流式聊天

```
POST /chat/stream
```

**请求体:** 同上

**响应:** Server-Sent Events (SSE) 格式

```
data: {"content": "你"}
data: {"content": "好"}
data: {"done": true}
```

### 4. 获取对话列表

```
GET /conversations
```

### 5. 创建对话

```
POST /conversations
```

**请求体:**
```json
{
  "title": "新对话",
  "model": "gpt-3.5-turbo",
  "provider": "openai"
}
```

### 6. 获取对话详情

```
GET /conversations/{id}
```

### 7. 删除对话

```
DELETE /conversations/{id}
```

## 错误处理

所有错误响应格式:
```json
{
  "detail": "错误描述"
}
```

常见错误码:
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 代码示例

### Python

```python
import requests

# 发送聊天请求
response = requests.post(
    "http://localhost:8000/api/v1/chat/completions",
    json={
        "messages": [{"role": "user", "content": "你好"}],
        "model": "gpt-3.5-turbo",
        "provider": "openai"
    }
)
print(response.json())
```

### JavaScript

```javascript
// 发送聊天请求
const response = await fetch('http://localhost:8000/api/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: '你好' }],
    model: 'gpt-3.5-turbo',
    provider: 'openai'
  })
});
const data = await response.json();
console.log(data);
```
