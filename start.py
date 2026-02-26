"""
AnotherYou v0.1 - 主程序
启动AI数字分身
"""

import asyncio
import argparse
import json
import os
from datetime import datetime

from core.agent_brain import AgentBrain
from core.agent_body import AgentBody

class AnotherYou:
    """另一个你 - 主控制器"""
    
    def __init__(self, player_name: str, agent_id: str = None):
        self.player_name = player_name
        self.agent_id = agent_id or f"agent_{player_name}_{int(datetime.now().timestamp())}"
        
        # 创建大脑和身体
        self.brain = AgentBrain(self.agent_id, player_name)
        self.body = AgentBody(self.agent_id, f"{player_name}_AI")
        
        # 连接身体和大脑
        self.body.on_observation = self._on_observation
        
        # 运行状态
        self.is_running = False
        self.tick_count = 0
        
    async def start(self):
        """启动AI分身"""
        print(f"\n{'='*50}")
        print(f"🎮 启动「另一个你」")
        print(f"   玩家: {self.player_name}")
        print(f"   AI ID: {self.agent_id}")
        print(f"{'='*50}\n")
        
        # 连接Minecraft
        await self.body.connect()
        
        if not self.body.is_connected:
            print("❌ 连接失败，请确保Minecraft服务器已启动")
            return
            
        self.is_running = True
        
        # 主循环
        while self.is_running:
            await self._tick()
            await asyncio.sleep(3)  # 每3秒一个决策周期
            
    async def _tick(self):
        """一个决策周期"""
        self.tick_count += 1
        
        # 1. 感知
        observation = self.body.get_observation_sync()
        perception = self.brain.perceive(observation)
        
        # 2. 思考决策
        action = self.brain.think(perception)
        
        # 3. 执行行动
        await self.body.execute_action(action)
        
        # 4. 每10个tick反思一次
        if self.tick_count % 10 == 0:
            reflection = self.brain.reflect()
            if reflection:
                print(f"\n💭 {self.player_name}的反思:\n{reflection}\n")
                
    async def stop(self):
        """停止AI分身"""
        print(f"\n👋 {self.player_name}的AI分身正在保存记忆...")
        self.is_running = False
        await self.body.disconnect()
        
        # 保存状态
        self._save_state()
        print(f"✅ 已保存。期待下次再见！\n")
        
    def _on_observation(self, observation: dict):
        """观察回调"""
        # 可以在这里处理紧急事件
        pass
        
    def _save_state(self):
        """保存AI状态"""
        state = self.brain.get_status()
        
        # 确保目录存在
        os.makedirs("data/agents", exist_ok=True)
        
        # 保存到文件
        filepath = f"data/agents/{self.agent_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            
        print(f"💾 状态已保存: {filepath}")


async def main():
    parser = argparse.ArgumentParser(description="另一个你 - AI数字分身")
    parser.add_argument("--name", default="玩家", help="玩家名称")
    parser.add_argument("--host", default="localhost", help="Minecraft服务器地址")
    parser.add_argument("--port", type=int, default=25565, help="Minecraft服务器端口")
    
    args = parser.parse_args()
    
    # 创建并启动
    another_you = AnotherYou(args.name)
    
    try:
        await another_you.start()
    except KeyboardInterrupt:
        print("\n\n收到停止信号...")
    finally:
        await another_you.stop()


if __name__ == "__main__":
    asyncio.run(main())
