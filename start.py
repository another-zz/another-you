#!/usr/bin/env python3
"""
AnotherYou - 启动脚本
启动本地Minecraft服务器和AI分身
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="启动 AnotherYou AI分身")
    parser.add_argument(
        "--mode",
        choices=["local", "server", "client"],
        default="local",
        help="运行模式: local(本地完整), server(仅服务端), client(仅客户端)"
    )
    parser.add_argument(
        "--ai-name",
        type=str,
        default="我的分身",
        help="AI分身的名字"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=25565,
        help="Minecraft服务器端口"
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="API服务器端口"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 启动 AnotherYou - {args.ai_name}")
    print(f"   模式: {args.mode}")
    print(f"   Minecraft端口: {args.port}")
    print(f"   API端口: {args.api_port}")
    print()
    print("⚠️  这是MVP版本，完整功能开发中...")
    print()
    
    # TODO: 实现实际的启动逻辑
    if args.mode in ["local", "server"]:
        print("📦 启动Minecraft服务器...")
        # start_minecraft_server(args.port)
        
        print("🤖 启动AI分身引擎...")
        # start_ai_engine(args.ai_name)
        
        print("🌐 启动API服务...")
        # start_api_server(args.api_port)
    
    if args.mode in ["local", "client"]:
        print("🎮 启动Web控制面板...")
        # start_web_panel()
    
    print()
    print("✅ 服务已启动！")
    print(f"   Minecraft: localhost:{args.port}")
    print(f"   Web面板: http://localhost:{args.api_port}")
    print()
    print("按 Ctrl+C 停止")
    
    try:
        # 保持运行
        while True:
            pass
    except KeyboardInterrupt:
        print("\n👋 再见！")


if __name__ == "__main__":
    main()
