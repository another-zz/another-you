#!/usr/bin/env python3
"""
AnotherYou 配置说明

## 1. LLM API Key 配置

### 方法1: 命令行参数
python3 dashboard.py --api-key "sk-your-kimi-api-key"

### 方法2: 环境变量
export KIMI_API_KEY="sk-your-kimi-api-key"
python3 dashboard.py

### 方法3: 修改配置文件
创建 .env 文件:
KIMI_API_KEY=sk-your-kimi-api-key

## 2. 当前状态

- LLM: 默认使用 mock 模式（无需API Key）
- 要接入真实Kimi: 提供 --api-key 参数

## 3. 修复计划

问题1: 所有AI数值一样
- 原因: 状态更新可能有bug
- 修复: 确保每个AI独立存储状态

问题2: 应该是单独线程/subagent
- 当前: 使用 asyncio 协程
- 建议: 每个AI一个独立进程（使用 multiprocessing）
"""

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
