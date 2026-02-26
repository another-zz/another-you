#!/bin/bash
# setup.sh - 项目初始化脚本

echo "🚀 AnotherYou 项目初始化"
echo "=========================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 Python 3"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 创建目录
echo "📁 创建目录结构..."
mkdir -p data/agents
mkdir -p data/memories
mkdir -p data/skills
mkdir -p logs

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 检查Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js 版本: $(node --version)"
    
    # 安装Mineflayer
    echo "📦 安装Mineflayer..."
    npm install mineflayer mineflayer-pathfinder
else
    echo "⚠️  未检测到Node.js，Minecraft连接功能不可用"
    echo "   安装Node.js后运行: npm install mineflayer mineflayer-pathfinder"
fi

echo ""
echo "✅ 初始化完成！"
echo ""
echo "启动方式:"
echo "  单AI:    python3 start.py --name='你的名字'"
echo "  多AI:    python3 multi_agent.py --names AI1 AI2 AI3"
echo ""
