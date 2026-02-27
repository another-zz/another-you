#!/bin/bash
# 启动 LiteLLM 代理 + AnotherYou

set -e

echo "🚀 启动 LiteLLM 代理..."

# 检查 litellm 是否安装
if ! command -v litellm &> /dev/null; then
    echo "安装 LiteLLM..."
    pip install litellm
fi

# 检查 KIMI_API_KEY
if [ -z "$KIMI_API_KEY" ]; then
    echo "❌ 请设置 KIMI_API_KEY 环境变量"
    echo "export KIMI_API_KEY='sk-kimi-...'"
    exit 1
fi

# 启动 LiteLLM 代理（后台）
echo "📡 启动 LiteLLM 代理..."
litellm --config litellm_config.yaml &
LITELLM_PID=$!

# 等待 LiteLLM 启动
sleep 3

echo "✅ LiteLLM 代理已启动 (PID: $LITELLM_PID)"
echo "📍 代理地址: http://localhost:4000/v1"

# 设置 AnotherYou 使用 LiteLLM
export LITELLM_API_KEY="dummy-key"
export LITELLM_BASE_URL="http://localhost:4000/v1"
export LITELLM_MODEL="kimi-coding"

echo ""
echo "🎮 启动 AnotherYou..."
python3 dashboard.py "$@"

# 清理：关闭 LiteLLM
echo ""
echo "🛑 关闭 LiteLLM 代理..."
kill $LITELLM_PID 2>/dev/null || true
