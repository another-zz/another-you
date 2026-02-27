#!/bin/bash
# install_minestudio.sh - 安装MineStudio

echo "📦 安装MineStudio"
echo "=================="

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装MineStudio
echo "安装MineStudio..."
pip install minestudio

echo ""
echo "✅ 安装完成"
echo "激活环境: source venv/bin/activate"
echo "测试运行: python -m minestudio.simulator.entry"
