#!/bin/bash

# Auto DevOps 启动脚本

echo "🔧 检查虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

echo "📦 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 文件不存在"
    exit 1
fi

echo "🚀 启动服务..."
.venv/bin/python main.py