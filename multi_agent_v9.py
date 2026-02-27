#!/usr/bin/env python3
"""
v0.9 多AI启动器 - Memory Stream + LLM驱动
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_v9 import Agent
from core.world_coordinator import WorldCoordinator

async def run_world(agent_names: list, mc_host: str, mc_port: int, api_key: str = None):
    """运行多AI世界"""
    
    # 创建世界协调器
    world = WorldCoordinator(world_name="AI文明世界-v0.9")
    
    # 创建多个AI
    agents = []
    for name in agent_names:
        agent = Agent(
            player_name=name,
            coordinator=world,
            mc_host=mc_host,
            mc_port=mc_port,
            api_key=api_key
        )
        agents.append(agent)
        
    # 同时启动所有AI
    print(f"\n🌍 启动多AI世界: {len(agents)}个AI")
    print(f"   AI列表: {', '.join(agent_names)}")
    print(f"   架构: Memory Stream + LLM + Planning\n")
    
    tasks = [agent.start_life() for agent in agents]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n\n停止所有AI...")
        for agent in agents:
            await agent.stop()
            
    # 最终报告
    stats = world.get_world_stats()
    print(f"\n{'='*60}")
    print(f"📊 世界最终统计")
    print(f"{'='*60}")
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
async def main():
    parser = argparse.ArgumentParser(
        description="AnotherYou v0.9 - 多AI世界",
        epilog="示例: python multi_agent_v9.py --names Alice Bob Charlie"
    )
    parser.add_argument(
        "--names",
        nargs="+",
        default=["Alice", "Bob", "Charlie"],
        help="AI名称列表"
    )
    parser.add_argument("--host", default="localhost", help="Minecraft服务器地址")
    parser.add_argument("--port", type=int, default=25565, help="Minecraft服务器端口")
    parser.add_argument("--api-key", default=None, help="Kimi API Key（可选）")
    
    args = parser.parse_args()
    
    await run_world(args.names, args.host, args.port, args.api_key)
    
if __name__ == "__main__":
    asyncio.run(main())
