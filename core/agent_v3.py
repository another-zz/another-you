"""
Agent v0.3 - 完整AI数字分身
集成LLM大脑 + 向量记忆
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Optional

from core.llm_brain import LLMBrain
from core.vector_memory import VectorMemory

class Agent:
    """
    AI数字分身 v0.3
    - LLM大脑决策
    - 向量长期记忆
    - 技能学习
    - 自主生存循环
    """
    
    def __init__(self, player_name: str, agent_id: str = None):
        self.player_name = player_name
        self.agent_id = agent_id or f"{player_name}_{int(time.time())}"
        
        # 大脑和记忆
        self.brain = LLMBrain(player_name)
        self.memory = VectorMemory(self.agent_id)
        
        # 基础状态
        self.energy = 100.0
        self.hunger = 0.0
        self.happiness = 50.0
        self.location = {"x": 0, "y": 64, "z": 0}
        
        # 技能
        self.skills: Dict[str, str] = {}
        
        # 目标
        self.current_goal = "在这个世界生存并发展"
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        self.is_running = False
        self.tick_interval = 5
        
    async def start_life(self):
        """开始自主生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」v0.3 已觉醒")
        print(f"   玩家: {self.player_name}")
        print(f"   AI ID: {self.agent_id}")
        print(f"   大脑: LLM + 向量记忆")
        print(f"   诞生: {self.birth_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 添加诞生记忆
        self.memory.add(
            f"我诞生了，成为{self.player_name}的数字分身",
            memory_type="event",
            importance=1.0
        )
        
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
        observation = self._perceive()
        
        # 2. 检索记忆
        relevant_memories = self.memory.retrieve(
            f"位置{self.location} 能量{self.energy} 饥饿{self.hunger}"
        )
        
        # 3. LLM决策
        action = self.brain.decide(
            observation=observation,
            memories=relevant_memories,
            skills=list(self.skills.keys())
        )
        
        # 4. 执行
        result = await self._execute(action)
        
        # 5. 记录记忆
        self.memory.add(
            f"{action}: {result}",
            memory_type="action",
            importance=0.3
        )
        
        # 6. 状态更新
        self._update_state()
        
        # 7. 定期报告
        if self.total_actions % 6 == 0:  # 每30秒
            self._report()
            
        # 8. 定期反思
        if self.total_actions % 60 == 0:  # 每5分钟
            await self._reflect()
            
    def _perceive(self) -> Dict:
        """感知世界"""
        return {
            "time": datetime.now().strftime("%H:%M"),
            "location": self.location.copy(),
            "energy": self.energy,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "nearby": self._simulate_nearby(),
        }
        
    def _simulate_nearby(self) -> List[str]:
        """模拟环境"""
        things = ["草地", "树木", "石头"]
        if self.location["x"] > 30:
            things.extend(["河流", "鱼"])
        if self.location["y"] < 60:
            things.append("洞穴")
        return random.sample(things, min(3, len(things)))
        
    async def _execute(self, action: str) -> str:
        """执行行动"""
        print(f"[{self.player_name}] {action}")
        
        # 行动效果
        effects = {
            "rest": lambda: self._effect(energy=20, hunger=5),
            "gather_food": lambda: self._effect(energy=-5, hunger=-30),
            "gather_wood": lambda: self._effect(energy=-10, hunger=10) or self._learn("wood"),
            "explore": lambda: self._effect(energy=-5, hunger=5) or self._move(),
            "build": lambda: self._effect(energy=-20, hunger=10) or self._learn("build"),
        }
        
        effect = effects.get(action, lambda: "未知行动")
        result = effect()
        
        await asyncio.sleep(1)
        return result or "完成"
        
    def _effect(self, energy: float = 0, hunger: float = 0):
        """状态效果"""
        self.energy = max(0, min(100, self.energy + energy))
        self.hunger = max(0, min(100, self.hunger + hunger))
        return f"能量{energy:+.0f}, 饥饿{hunger:+.0f}"
        
    def _move(self):
        """移动"""
        self.location["x"] += random.randint(-10, 10)
        self.location["z"] += random.randint(-10, 10)
        return f"移动到({self.location['x']}, {self.location['z']})"
        
    def _learn(self, skill: str):
        """学习技能"""
        if skill not in self.skills:
            self.skills[skill] = f"会{skill}了"
            self.memory.add(
                f"学会了{skill}！",
                memory_type="skill",
                importance=0.8
            )
            return f"学会{skill}！"
        return ""
        
    def _update_state(self):
        """自然消耗"""
        self.energy = max(0, self.energy - 1.5)
        self.hunger = min(100, self.hunger + 1.0)
        
        # 危急状态
        if self.energy < 20:
            self.memory.add("能量严重不足，需要休息", importance=0.9)
        if self.hunger > 80:
            self.memory.add("非常饥饿，需要食物", importance=0.9)
            
    def _report(self):
        """状态报告"""
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        print(f"\n📊 {self.player_name} 状态")
        print(f"   存活: {age:.1f}分钟 | 行动: {self.total_actions}")
        print(f"   能量: {self.energy:.0f}% | 饥饿: {self.hunger:.0f}%")
        print(f"   位置: ({self.location['x']}, {self.location['y']}, {self.location['z']})")
        print(f"   技能: {list(self.skills.keys())}")
        print(f"   记忆: {len(self.memory.memories)}条")
        
    async def _reflect(self):
        """反思"""
        recent = self.memory.get_recent(10)
        reflection = self.brain.reflect(recent)
        
        if reflection:
            print(f"\n💭 {self.player_name}的反思:")
            print(f"   {reflection}")
            self.memory.add(reflection, memory_type="reflection", importance=0.7)
            
        # 记忆整合
        if len(self.memory.memories) > 100:
            self.memory.consolidate()
            
    async def stop(self):
        """停止"""
        print(f"\n👋 {self.player_name} 休眠中...")
        self.is_running = False
        self.memory.save()
        print(f"💾 已保存 {len(self.memory.memories)} 条记忆")
