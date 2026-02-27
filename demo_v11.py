#!/usr/bin/env python3
"""
AnotherYou v0.11 快速演示
无需Docker，直接运行
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_v11 import Agent
from core.world_coordinator import WorldCoordinator
from core.social_network import SocialNetwork

async def quick_demo():
    """快速演示"""
    print("="*60)
    print("🌍 AnotherYou v0.11 快速演示")
    print("="*60)
    print("\n这是一个简化演示，展示核心功能:\n")
    print("1. AI自主决策")
    print("2. Memory Stream记忆")
    print("3. 社会网络关系")
    print("4. 技能学习")
    
    # 创建组件
    social = SocialNetwork()
    world = WorldCoordinator(world_name='演示世界')
    
    # 创建AI
    print("\n" + "-"*60)
    print("🤖 创建3个AI: Alice, Bob, Charlie")
    print("-"*60)
    
    agents = []
    for name in ['Alice', 'Bob', 'Charlie']:
        agent = Agent(
            player_name=name,
            coordinator=world,
            social_network=social
        )
        agents.append(agent)
        print(f"   ✅ {name} 已创建")
    
    # 模拟运行
    print("\n" + "-"*60)
    print("🔄 模拟运行 (每个AI执行3个行动)")
    print("-"*60)
    
    for agent in agents:
        agent.is_running = True
        
    for i in range(3):
        print(f"\n--- 第 {i+1} 轮 ---")
        for agent in agents:
            await agent._life_tick()
            print(f"   [{agent.player_name}] 行动 #{agent.total_actions}")
    
    # 显示结果
    print("\n" + "="*60)
    print("📊 演示结果")
    print("="*60)
    
    for agent in agents:
        status = agent.get_status()
        print(f"\n🤖 {status['name']}")
        print(f"   总行动: {status['total_actions']}")
        print(f"   能量: {status['energy']:.0f}%")
        print(f"   记忆: {status['memory_summary']}")
        print(f"   技能: {len(status['skills'])}个")
        if 'social' in status:
            s = status['social']
            print(f"   社交: {s['friends']}友/{s['enemies']}敌")
    
    # 社会网络
    print(f"\n🕸️ 社会网络统计")
    stats = social.get_network_stats()
    print(f"   关系总数: {stats['total_relationships']}")
    print(f"   社交事件: {stats['total_events']}")
    
    # 保存
    for agent in agents:
        await agent.stop()
    
    print("\n" + "="*60)
    print("✅ 演示完成!")
    print("="*60)
    print("\n完整运行命令:")
    print("  python3 multi_agent_v11.py --names Alice Bob Charlie")
    print("\nWeb面板地址 (启动docker后):")
    print("  http://localhost:8080")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(quick_demo())
