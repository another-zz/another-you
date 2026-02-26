"""
AnotherYou v0.4 - 主程序
连接真实Minecraft的AI数字分身
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_v4 import Agent

async def main():
    parser = argparse.ArgumentParser(
        description="另一个你 v0.4 - Minecraft AI数字分身",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 连接本地Minecraft服务器
  python start.py --name="小明" --host=localhost --port=25565
  
  # 模拟模式（不连接MC）
  python start.py --name="Alice"
        """
    )
    parser.add_argument("--name", default="玩家", help="你的名称")
    parser.add_argument("--host", default="localhost", help="Minecraft服务器地址")
    parser.add_argument("--port", type=int, default=25565, help="Minecraft服务器端口")
    parser.add_argument("--tick", type=int, default=5, help="决策间隔（秒）")
    
    args = parser.parse_args()
    
    # 创建AI
    agent = Agent(
        player_name=args.name,
        mc_host=args.host,
        mc_port=args.port
    )
    agent.tick_interval = args.tick
    
    # 启动
    try:
        await agent.start_life()
    except KeyboardInterrupt:
        print("\n\n停止信号...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
