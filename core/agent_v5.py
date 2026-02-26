"""
Agent v0.5 - 技能代码生成版
AI能生成并执行新技能
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List

from core.llm_brain import LLMBrain
from core.vector_memory import VectorMemory
from core.mc_connector import MinecraftConnector
from core.skill_generator import SkillCodeGenerator

class Agent:
    """
    AI数字分身 v0.5
    - 自动生成技能代码
    - 终身学习
    """
    
    def __init__(self, player_name: str, agent_id: str = None,
                 mc_host: str = "localhost", mc_port: int = 25565):
        self.player_name = player_name
        self.agent_id = agent_id or f"{player_name}_{int(time.time())}"
        
        # 核心组件
        self.brain = LLMBrain(player_name)
        self.memory = VectorMemory(self.agent_id)
        self.mc = MinecraftConnector(
            host=mc_host,
            port=mc_port,
            username=f"{player_name}_AI"
        )
        self.skill_gen = SkillCodeGenerator()
        
        # MC回调
        self.mc.on_state_update = self._on_mc_state
        self.mc.on_chat = self._on_mc_chat
        self.mc.on_death = self._on_mc_death
        
        # 状态
        self.energy = 100.0
        self.hunger = 0.0
        self.location = {"x": 0, "y": 64, "z": 0}
        self.inventory = {}
        self.is_in_mc = False
        
        # 学习系统
        self.learned_skills: List[str] = []
        self.current_task = None
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        self.is_running = False
        self.tick_interval = 5
        
    async def start_life(self):
        """开始自主生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」v0.5 已觉醒")
        print(f"   玩家: {self.player_name}")
        print(f"   能力: 自动生成技能代码 + 终身学习")
        print(f"{'='*60}\n")
        
        # 连接MC
        print("[系统] 连接Minecraft...")
        if self.mc.start():
            self.is_in_mc = True
            print("[系统] ✅ 已连接！")
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
        
        # 2. 决策
        memories = self.memory.retrieve(str(obs))
        action = self.brain.decide(obs, memories, self.learned_skills)
        
        # 3. 执行（可能生成新技能）
        result = await self._execute_with_learning(action)
        
        # 4. 记录
        self.memory.add(f"{action}: {result}", importance=0.3)
        
        # 5. 报告
        if self.total_actions % 6 == 0:
            self._report()
            
    async def _execute_with_learning(self, action: str) -> str:
        """执行并学习"""
        print(f"[{self.player_name}] {action}")
        
        # 检查是否需要生成新技能
        if action not in self.learned_skills and action not in ["rest", "explore"]:
            print(f"  📝 生成新技能: {action}")
            skill = self.skill_gen.generate_skill(action)
            self.learned_skills.append(action)
            print(f"  ✅ 技能已生成！")
            
        # 执行
        if self.is_in_mc:
            return await self._execute_mc(action)
        else:
            return await self._execute_sim(action)
            
    async def _execute_mc(self, action: str) -> str:
        """在MC中执行"""
        if action == "砍树":
            self.mc.dig(0, 0, 1)
            return "砍树中"
        elif action == "挖矿":
            self.mc.dig(0, -1, 0)
            return "挖矿中"
        elif action == "探索":
            dx, dz = random.randint(-10, 10), random.randint(-10, 10)
            self.mc.move_to(
                self.location['x'] + dx,
                self.location['y'],
                self.location['z'] + dz
            )
            return f"移动到({dx}, {dz})"
        else:
            self.mc.say(f"我在{action}")
            return action
            
    async def _execute_sim(self, action: str) -> str:
        """模拟执行"""
        effects = {
            "rest": lambda: self._mod(20, 5),
            "砍树": lambda: self._mod(-10, 10) or self._learn("砍树"),
            "挖矿": lambda: self._mod(-15, 15) or self._learn("挖矿"),
            "探索": lambda: self._mod(-5, 5) or self._move(),
        }
        
        effect = effects.get(action, lambda: "未知")
        result = effect()
        
        await asyncio.sleep(1)
        return result or "完成"
        
    def _mod(self, e: float, h: float):
        self.energy = max(0, min(100, self.energy + e))
        self.hunger = min(100, self.hunger + h)
        
    def _move(self):
        self.location["x"] += random.randint(-10, 10)
        self.location["z"] += random.randint(-10, 10)
        
    def _learn(self, skill: str):
        if skill not in self.learned_skills:
            self.learned_skills.append(skill)
            self.memory.add(f"学会了{skill}！", importance=0.8)
            
    def _perceive(self) -> Dict:
        if self.is_in_mc:
            return {
                "source": "minecraft",
                "location": self.location.copy(),
                "energy": self.energy,
                "inventory": self.inventory,
            }
        return {
            "source": "simulated",
            "location": self.location.copy(),
            "energy": self.energy,
            "nearby": ["草地", "树木"],
        }
        
    def _report(self):
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        print(f"\n📊 {self.player_name} | 存活{age:.1f}分钟 | 技能{len(self.learned_skills)}个")
        print(f"   能量{self.energy:.0f}% | 背包{self.inventory}")
        
    async def stop(self):
        print(f"\n👋 {self.player_name} 休眠...")
        self.is_running = False
        if self.is_in_mc:
            self.mc.stop()
        self.memory.save()
