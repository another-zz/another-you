#!/usr/bin/env python3
"""
v0.10 多AI启动器 - 真实LLM + 技能执行

使用方法:
    # 模拟模式（无需API Key）
    python multi_agent_v10.py --names Alice Bob Charlie
    
    # 真实LLM模式（需要Kimi API Key）
    export KIMI_API_KEY="your-api-key"
    python multi_agent_v10.py --names Alice Bob Charlie
    
    # 连接真实Minecraft
    python multi_agent_v10.py --names Alice Bob Charlie --host localhost --port 25565
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_v10 import Agent
from core.world_coordinator import WorldCoordinator

async def run_world(agent_names: list, mc_host: str, mc_port: int, 
                   api_key: str = None, provider: str = None):
    """运行多AI世界"""
    
    # 创建世界协调器
    world = WorldCoordinator(world_name="AI文明世界-v0.10")
    
    # 创建多个AI
    agents = []
    for name in agent_names:
        agent = Agent(
            player_name=name,
            coordinator=world,
            mc_host=mc_host,
            mc_port=mc_port,
            api_key=api_key,
            provider=provider
        )
        agents.append(agent)
        
    # 显示信息
    print(f"\n{'='*60}")
    print(f"🌍 AnotherYou v0.10 - 多AI世界")
    print(f"{'='*60}")
    print(f"AI数量: {len(agents)}")
    print(f"AI列表: {', '.join(agent_names)}")
    print(f"架构: Memory Stream + LLM + Skill Execution")
    
    # 检测LLM模式
    if api_key or os.getenv("KIMI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        print(f"LLM模式: 真实API")
    else:
        print(f"LLM模式: 模拟（设置KIMI_API_KEY启用真实LLM）")
        
    print(f"Minecraft: {mc_host}:{mc_port}")
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
    stats = world.get_world_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
async def main():
    parser = argparse.ArgumentParser(
        description="AnotherYou v0.10 - 真实LLM驱动的AI世界",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速测试（模拟模式）
  python multi_agent_v10.py --names Alice Bob
  
  # 真实LLM模式
  export KIMI_API_KEY="sk-..."
  python multi_agent_v10.py --names Alice Bob Charlie
  
  # 连接Minecraft
  python multi_agent_v10.py --names Alice --host localhost --port 25565
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
                       help="API Key（或设置环境变量KIMI_API_KEY）")
    parser.add_argument("--provider", default=None,
                       help="LLM提供商（kimi/openai，自动检测）")
    
    args = parser.parse_args()
    
    await run_world(
        args.names, args.host, args.port, 
        args.api_key, args.provider
    )
    
if __name__ == "__main__":
    asyncio.run(main())
