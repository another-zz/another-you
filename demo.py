#!/usr/bin/env python3
"""
AnotherYou - 快速测试启动器
无需Minecraft，纯Python模拟模式
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_v8 import Agent
from core.world_coordinator import WorldCoordinator

async def run_demo(agent_names: list):
    """运行演示模式"""
    
    print("\n" + "="*60)
    print("🌍 AnotherYou v0.8 - 模拟模式")
    print("   无需Minecraft，纯Python运行")
    print("="*60 + "\n")
    
    # 创建世界协调器
    world = WorldCoordinator(world_name="模拟世界")
    
    # 创建AI（不连接MC）
    agents = []
    for name in agent_names:
        agent = Agent(
            player_name=name,
            coordinator=world,
            mc_host="localhost",  # 不会实际连接
            mc_port=25565
        )
        agents.append(agent)
        
    print(f"🤖 创建了 {len(agents)} 个AI:")
    for agent in agents:
        print(f"   - {agent.player_name}")
    print()
    
    # 同时启动所有AI
    print("🚀 启动AI生命循环...\n")
    print("按 Ctrl+C 停止\n")
    
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
        
    print(f"\n{'='*60}")
    print("👋 感谢使用 AnotherYou!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # 默认AI名称
    names = ["Alice", "Bob", "Charlie"]
    
    if len(sys.argv) > 1:
        names = sys.argv[1:]
    
    try:
        asyncio.run(run_demo(names))
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
