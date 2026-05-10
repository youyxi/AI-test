# AI Chat Hub - AI对话聚合平台

一个集成多种AI模型的对话聚合平台，支持主流商业模型、开源模型、国内大模型和本地部署模型。

## 功能特性

- 多模型支持：OpenAI、Claude、Gemini、文心一言、通义千问、本地模型等
- 统一对话界面：一个界面切换不同AI模型
- 流式响应：支持实时流式输出
- 对话历史：保存和管理对话记录
- 现代化UI：基于Vue 3的响应式界面

## 项目结构

```
ai-chat-hub/
├── backend/                # Python后端服务
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── adapters/      # AI模型适配器
│   └── requirements.txt
├── frontend/              # Vue前端
│   ├── src/
│   │   ├── components/   # Vue组件
│   │   ├── views/        # 页面视图
│   │   ├── stores/       # 状态管理
│   │   └── api/          # API调用
│   └── package.json
└── docs/                  # 文档
```

## 快速开始

### 方式一：一键启动脚本

**Linux/Mac:**
```bash
./start.sh
```

**Windows (CMD):**
```cmd
start.bat
```

**Windows (PowerShell - 推荐):**
```powershell
# 先设置执行策略（首次运行需要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后运行
.\start.ps1
```

### 方式二：手动启动

#### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 配置API密钥
python run.py
```

#### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 支持的AI模型

| 类型 | 模型 |
|------|------|
| 主流商业模型 | OpenAI GPT-4/GPT-3.5, Claude, Gemini |
| 国内大模型 | 文心一言、通义千问、讯飞星火、智谱AI |
| 开源模型 | Llama、Qwen、ChatGLM |
| 本地部署 | Ollama、vLLM |

## 配置说明

在 `backend/.env` 文件中配置API密钥：

```env
# OpenAI
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Claude
ANTHROPIC_API_KEY=your_key

# Gemini
GOOGLE_API_KEY=your_key

# 国内模型
BAIDU_API_KEY=your_key
BAIDU_SECRET_KEY=your_secret
QWEN_API_KEY=your_key

# 本地模型
OLLAMA_BASE_URL=http://localhost:11434
```

## 访问地址

- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## License

MIT
