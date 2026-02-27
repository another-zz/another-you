#!/usr/bin/env python3
"""
测试 Kimi API 地址
"""

import os
import sys
from openai import OpenAI

# 从环境变量获取 API Key
api_key = os.getenv("KIMI_API_KEY")
if not api_key:
    print("请设置 KIMI_API_KEY 环境变量")
    sys.exit(1)

# 测试多个可能的地址
configs = [
    {"name": "Kimi官方", "base_url": "https://api.moonshot.cn/v1", "model": "kimi-k2.5"},
    {"name": "Kimi Code", "base_url": "https://api.kimi.com/coding", "model": "kimi-coding"},
    {"name": "Kimi Code v1", "base_url": "https://api.kimi.com/coding/v1", "model": "kimi-coding"},
    {"name": "Kimi k2", "base_url": "https://api.moonshot.cn/v1", "model": "kimi-k2-turbo-preview"},
]

print("="*60)
print("测试 Kimi API 地址")
print("="*60)

for config in configs:
    print(f"\n测试: {config['name']}")
    print(f"  URL: {config['base_url']}")
    print(f"  Model: {config['model']}")
    
    try:
        client = OpenAI(api_key=api_key, base_url=config['base_url'])
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=10
        )
        
        print(f"  ✅ 成功: {response.choices[0].message.content[:30]}...")
        print(f"\n{'='*60}")
        print(f"推荐配置:")
        print(f"  base_url: {config['base_url']}")
        print(f"  model: {config['model']}")
        print(f"{'='*60}")
        break
        
    except Exception as e:
        error = str(e)
        if "401" in error:
            print(f"  ❌ 401 认证失败")
        elif "404" in error:
            print(f"  ❌ 404 地址不存在")
        elif "model" in error.lower():
            print(f"  ❌ 模型不存在: {error[:50]}")
        else:
            print(f"  ❌ 错误: {error[:50]}")

print("\n测试完成")
