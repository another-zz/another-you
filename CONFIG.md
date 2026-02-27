#!/usr/bin/env python3
"""
AnotherYou 配置说明

## API Key 配置方法（按优先级排序）

### 方法1: 命令行参数（最高优先级）
python3 dashboard.py --api-key "sk-your-kimi-api-key"

### 方法2: 配置文件（推荐）
编辑 config.yaml:
```yaml
llm:
  provider: "kimi"
  api_key: "sk-your-kimi-api-key"
```

### 方法3: 环境变量
export KIMI_API_KEY="sk-your-kimi-api-key"
python3 dashboard.py

## 当前状态

- LLM: 默认使用 mock 模式（无需API Key）
- 要接入真实Kimi: 使用上述任一方法配置

## 依赖安装

pip install openai pyyaml


import os

# 读取环境变量
KIMI_API_KEY = os.getenv("KIMI_API_KEY")

if __name__ == "__main__":
    print(__doc__)
    
    if KIMI_API_KEY:
        print(f"✅ 检测到 KIMI_API_KEY: {KIMI_API_KEY[:10]}...")
    else:
        print("⚠️  未检测到 KIMI_API_KEY，将使用 mock 模式")
        print("   设置方法: export KIMI_API_KEY='sk-your-key'")
