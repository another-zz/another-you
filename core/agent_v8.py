"""
Agent v0.8 - 完整版
多AI协作 + 经济系统 + 社会演化
"""

import asyncio
import time
import random
from datetime import datetime
from typing import Dict, List

from core.llm_brain import LLMBrain
from core.vector_memory import VectorMemory
from core.mc_connector import MinecraftConnector
from core.skill_generator import SkillCodeGenerator
from core.world_coordinator import WorldCoordinator
from core.economy import EconomySystem

class Agent:
    """
    AI数字分身 v0.8
    完整功能：学习、协作、交易、演化
    """
    
    def __init__(self, player_name: str, coordinator: WorldCoordinator = None,
                 mc_host: str = "localhost", mc_port: int = 25565):
        self.player_name = player_name
        self.agent_id = f"{player_name}_{int(time.time())}"
        
        # 核心组件
        self.brain = LLMBrain(player_name)
        self.memory = VectorMemory(self.agent_id)
        self.mc = MinecraftConnector(
            host=mc_host, port=mc_port,
            username=f"{player_name}_AI"
        )
        self.skill_gen = SkillCodeGenerator()
        self.economy = EconomySystem()
        
        # 世界协调
        self.coordinator = coordinator
        if coordinator:
            coordinator.register_agent(self)
            
        # 状态
        self.location = {"x": 0, "y": 64, "z": 0}
        self.inventory: Dict[str, int] = {}
        self.energy = 100.0
        self.hunger = 0.0
        self.is_in_mc = False
        
        # 社交
        self.friends: List[str] = []
        self.reputation = 50  # 声望 0-100
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        self.is_running = False
        self.tick_interval = 5
        
    async def start_life(self):
        """开始生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」v0.8 完整版")
        print(f"   玩家: {self.player_name}")
        print(f"   能力: 学习 | 协作 | 交易 | 演化")
        print(f"{'='*60}\n")
        
        # 连接MC
        if self.mc.start():
            self.is_in_mc = True
            print("[系统] ✅ 已连接Minecraft")
        else:
            print("[系统] ⚠️ 模拟模式")
            
        # 主循环
        while self.is_running:
            try:
                await self._life_tick()
                await asyncio.sleep(self.tick_interval)
            except Exception as e:
                print(f"[错误] {e}")
                await asyncio.sleep(10)
                
    async def _life_tick(self):
        """生命节拍"""
        self.total_actions += 1
        
        # 1. 感知
        obs = self._perceive()
        
        # 2. 检查社交机会
        if self.coordinator and self.total_actions % 10 == 0:
            await self._check_social()
            
        # 3. 决策
        memories = self.memory.retrieve(str(obs))
        action = self.brain.decide(obs, memories, [])
        
        # 4. 执行
        result = await self._execute(action)
        
        # 5. 记录
        self.memory.add(f"{action}: {result}", importance=0.3)
        
        # 6. 报告
        if self.total_actions % 12 == 0:
            self._report()
            
    async def _check_social(self):
        """检查社交/交易机会"""
        if not self.coordinator:
            return
            
        # 找附近AI
        nearby = self.coordinator.get_nearby_agents(self.location, 100)
        
        for other_id in nearby:
            other = self.coordinator.agents.get(other_id)
            if not other:
                continue
                
            # 交易检查
            if self.economy.should_trade(self.inventory, "wood"):
                partner = self.coordinator.find_trade_partner(
                    self.agent_id, "wood", self.coordinator.agents
                )
                if partner:
                    # 执行交易
                    self.coordinator.facilitate_trade(
                        self.agent_id, partner,
                        "stone", "wood"
                    )
                    
            # 交友
            if other_id not in self.friends:
                self.friends.append(other_id)
                self.memory.add(f"认识了{other.player_name}", importance=0.5)
                print(f"[社交] {self.player_name} 认识了 {other.player_name}")
                
    async def _execute(self, action: str) -> str:
        """执行"""
        print(f"[{self.player_name}] {action}")
        
        # 学习新技能
        if action not in ["rest", "explore", "socialize"]:
            self.skill_gen.generate_skill(action)
            
        # 模拟执行
        if action == "砍树":
            self.inventory["wood"] = self.inventory.get("wood", 0) + 5
            self.energy -= 10
        elif action == "挖矿":
            self.inventory["stone"] = self.inventory.get("stone", 0) + 3
            self.energy -= 15
        elif action == "rest":
            self.energy = min(100, self.energy + 20)
            
        await asyncio.sleep(1)
        return "完成"
        
    def _perceive(self) -> Dict:
        """感知"""
        return {
            "location": self.location.copy(),
            "energy": self.energy,
            "inventory": self.inventory.copy(),
            "friends": len(self.friends),
        }
        
    def _report(self):
        """报告"""
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        wealth = self.economy.evaluate_inventory(self.inventory)
        
        print(f"\n📊 {self.player_name}")
        print(f"   存活: {age:.1f}分钟 | 财富: {wealth:.0f}")
        print(f"   朋友: {len(self.friends)} | 声望: {self.reputation}")
        print(f"   背包: {self.inventory}")
        
    async def stop(self):
        """停止"""
        print(f"\n👋 {self.player_name} 休眠...")
        self.is_running = False
        if self.coordinator:
            self.coordinator.unregister_agent(self.agent_id)
        self.mc.stop()
        self.memory.save()
