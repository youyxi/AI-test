#!/bin/bash

# AI Chat Hub 启动脚本

echo "🚀 启动 AI Chat Hub..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
if [ ! -f ".installed" ]; then
    echo "安装后端依赖..."
    pip install -r requirements.txt
    touch .installed
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，使用示例配置..."
    cp .env.example .env
    echo "请编辑 backend/.env 文件配置您的API密钥"
fi

# 启动后端服务
python run.py &
BACKEND_PID=$!

cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ AI Chat Hub 已启动!"
echo ""
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端地址: http://localhost:8000"
echo "📍 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待进程
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
