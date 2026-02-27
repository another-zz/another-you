#!/usr/bin/env python3
"""
v0.11 多AI启动器 - 深度社会演化

使用方法:
    python main.py --names Alice Bob Charlie
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import Agent
from core.world_coordinator import WorldCoordinator
from core.social_network import SocialNetwork

async def run_world(agent_names: list, mc_host: str, mc_port: int, 
                   api_key: str = None, provider: str = None):
    """运行多AI世界"""
    
    # 创建共享社会网络
    social_network = SocialNetwork()
    
    # 创建世界协调器
    world = WorldCoordinator(world_name="AI文明世界-v0.11")
    
    # 创建多个AI
    agents = []
    for name in agent_names:
        agent = Agent(
            player_name=name,
            coordinator=world,
            social_network=social_network,
            mc_host=mc_host,
            mc_port=mc_port,
            api_key=api_key,
            provider=provider
        )
        agents.append(agent)
        
    # 显示信息
    print(f"\n{'='*60}")
    print(f"🌍 AnotherYou v0.11 - AI文明世界")
    print(f"{'='*60}")
    print(f"AI数量: {len(agents)}")
    print(f"AI列表: {', '.join(agent_names)}")
    print(f"架构: Memory + LLM + Skills + Social Network")
    
    if api_key or os.getenv("KIMI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        print(f"LLM模式: 真实API")
    else:
        print(f"LLM模式: 模拟")
        
    print(f"Minecraft: {mc_host}:{mc_port}")
    print(f"Web面板: http://localhost:8080 (启动nginx后)")
    print(f"{'='*60}\n")
    
    # 启动所有AI
    tasks = [agent.start_life() for agent in agents]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n\n🛑 停止所有AI...")
        for agent in agents:
            await agent.stop()
            
    # 最终报告
    print(f"\n{'='*60}")
    print(f"📊 世界最终统计")
    print(f"{'='*60}")
    
    # 世界统计
    stats = world.get_world_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
    # 社会网络统计
    network_stats = social_network.get_network_stats()
    print(f"\n🕸️ 社会网络统计")
    print(f"   关系总数: {network_stats['total_relationships']}")
    print(f"   派系数量: {network_stats['total_factions']}")
    print(f"   社交事件: {network_stats['total_events']}")
    
    # 每个AI的社交摘要
    print(f"\n👥 AI社交摘要")
    for agent in agents:
        social = social_network.get_social_summary(agent.player_name)
        print(f"   {agent.player_name}: {social['friends']}友/{social['enemies']}敌 声望{social['reputation']:.0f}")
        
async def main():
    parser = argparse.ArgumentParser(
        description="AnotherYou v0.11 - 深度社会演化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速测试
  python main.py --names Alice Bob Charlie
  
  # 真实LLM
  export KIMI_API_KEY="sk-..."
  python main.py --names Alice Bob
        """
    )
    parser.add_argument(
        "--names",
        nargs="+",
        default=["Alice", "Bob", "Charlie"],
        help="AI名称列表"
    )
    parser.add_argument("--host", default="localhost", 
                       help="Minecraft服务器地址")
    parser.add_argument("--port", type=int, default=25565,
                       help="Minecraft服务器端口")
    parser.add_argument("--api-key", default=None,
                       help="API Key")
    parser.add_argument("--provider", default=None,
                       help="LLM提供商")
    
    args = parser.parse_args()
    
    await run_world(
        args.names, args.host, args.port, 
        args.api_key, args.provider
    )
    
if __name__ == "__main__":
    asyncio.run(main())
