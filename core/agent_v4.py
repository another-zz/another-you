"""
Agent v0.4 - 连接真实Minecraft的AI数字分身
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

class Agent:
    """
    AI数字分身 v0.4
    - 连接真实Minecraft世界
    - LLM大脑决策
    - 向量长期记忆
    - 真实生存循环
    """
    
    def __init__(self, player_name: str, agent_id: str = None,
                 mc_host: str = "localhost", mc_port: int = 25565):
        self.player_name = player_name
        self.agent_id = agent_id or f"{player_name}_{int(time.time())}"
        
        # 大脑和记忆
        self.brain = LLMBrain(player_name)
        self.memory = VectorMemory(self.agent_id)
        
        # Minecraft连接
        self.mc = MinecraftConnector(
            host=mc_host,
            port=mc_port,
            username=f"{player_name}_AI"
        )
        self.mc.on_state_update = self._on_mc_state
        self.mc.on_chat = self._on_mc_chat
        self.mc.on_death = self._on_mc_death
        
        # 状态
        self.energy = 100.0
        self.hunger = 0.0
        self.location = {"x": 0, "y": 64, "z": 0}
        self.inventory = {}
        self.is_in_mc = False
        
        # 技能
        self.skills: Dict[str, str] = {}
        
        # 目标
        self.current_goal = "在Minecraft世界生存发展"
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        self.is_running = False
        self.tick_interval = 5
        
    async def start_life(self):
        """开始自主生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」v0.4 已觉醒")
        print(f"   玩家: {self.player_name}")
        print(f"   AI ID: {self.agent_id}")
        print(f"   世界: Minecraft @ {self.mc.host}:{self.mc.port}")
        print(f"{'='*60}\n")
        
        # 尝试连接Minecraft
        print("[系统] 正在连接Minecraft服务器...")
        if self.mc.start():
            self.is_in_mc = True
            print("[系统] ✅ 已连接到Minecraft世界！")
            self.memory.add("我成功进入了Minecraft世界", importance=1.0)
        else:
            print("[系统] ⚠️ 无法连接MC，进入模拟模式")
            self.memory.add("无法连接Minecraft，在模拟模式中运行", importance=0.5)
            
        # 主循环
        while self.is_running:
            try:
                await self._life_tick()
                await asyncio.sleep(self.tick_interval)
            except Exception as e:
                print(f"[错误] {e}")
                await asyncio.sleep(10)
                
    def _on_mc_state(self, state: Dict):
        """MC状态更新回调"""
        if 'position' in state:
            pos = state['position']
            self.location = {"x": int(pos['x']), "y": int(pos['y']), "z": int(pos['z'])}
        if 'health' in state:
            self.energy = state['health'] * 5  # 20血=100能量
        if 'food' in state:
            self.hunger = 100 - state['food'] * 5  # 20饱食=0饥饿
        if 'inventory' in state:
            self.inventory = {item['name']: item['count'] for item in state['inventory']}
            
    def _on_mc_chat(self, username: str, message: str):
        """MC聊天回调"""
        print(f"[聊天] {username}: {message}")
        self.memory.add(f"听到{username}说: {message}", importance=0.4)
        
    def _on_mc_death(self):
        """MC死亡回调"""
        print("[系统] 💀 AI死亡了！")
        self.memory.add("我死亡了，需要小心", importance=0.9)
        
    async def _life_tick(self):
        """生命节拍"""
        self.total_actions += 1
        
        # 1. 感知
        observation = self._perceive()
        
        # 2. 检索记忆
        memories = self.memory.retrieve(str(observation))
        
        # 3. LLM决策
        action = self.brain.decide(observation, memories, list(self.skills.keys()))
        
        # 4. 执行（真实MC或模拟）
        if self.is_in_mc:
            result = await self._execute_in_mc(action)
        else:
            result = await self._execute_simulated(action)
            
        # 5. 记录
        self.memory.add(f"{action}: {result}", importance=0.3)
        
        # 6. 报告
        if self.total_actions % 6 == 0:
            self._report()
            
    def _perceive(self) -> Dict:
        """感知"""
        if self.is_in_mc:
            return {
                "source": "minecraft",
                "location": self.location.copy(),
                "energy": self.energy,
                "hunger": self.hunger,
                "inventory": self.inventory,
            }
        else:
            return {
                "source": "simulated",
                "location": self.location.copy(),
                "energy": self.energy,
                "hunger": self.hunger,
                "nearby": ["草地", "树木", "石头"],
            }
            
    async def _execute_in_mc(self, action: str) -> str:
        """在真实MC中执行"""
        print(f"[{self.player_name}] MC执行: {action}")
        
        if action == "gather_wood":
            # 向前挖
            self.mc.dig(0, 0, 1)
            return "挖掘前方方块"
            
        elif action == "explore":
            # 随机移动
            dx = random.randint(-5, 5)
            dz = random.randint(-5, 5)
            new_x = self.location['x'] + dx
            new_z = self.location['z'] + dz
            self.mc.move_to(new_x, self.location['y'], new_z)
            return f"移动到({new_x}, {new_z})"
            
        elif action == "rest":
            self.mc.say("我需要休息一下...")
            return "休息中"
            
        else:
            self.mc.say(f"我在{action}")
            return f"执行{action}"
            
    async def _execute_simulated(self, action: str) -> str:
        """模拟执行"""
        print(f"[{self.player_name}] 模拟: {action}")
        
        # 状态变化
        if action == "rest":
            self.energy = min(100, self.energy + 20)
            self.hunger = min(100, self.hunger + 5)
        elif action == "gather_food":
            self.hunger = max(0, self.hunger - 30)
        elif action == "gather_wood":
            self.energy -= 10
            self.hunger += 10
            self.skills["wood"] = "会砍树"
        elif action == "explore":
            self.location["x"] += random.randint(-10, 10)
            self.location["z"] += random.randint(-10, 10)
            self.energy -= 5
            
        await asyncio.sleep(1)
        return "完成"
        
    def _report(self):
        """状态报告"""
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        mode = "Minecraft" if self.is_in_mc else "模拟"
        
        print(f"\n📊 {self.player_name} 状态 ({mode}模式)")
        print(f"   存活: {age:.1f}分钟 | 行动: {self.total_actions}")
        print(f"   能量: {self.energy:.0f}% | 饥饿: {self.hunger:.0f}%")
        print(f"   位置: ({self.location['x']}, {self.location['y']}, {self.location['z']})")
        if self.inventory:
            print(f"   背包: {self.inventory}")
            
    async def stop(self):
        """停止"""
        print(f"\n👋 {self.player_name} 休眠中...")
        self.is_running = False
        
        if self.is_in_mc:
            self.mc.say("我要下线了，再见！")
            self.mc.stop()
            
        self.memory.save()
        print(f"💾 已保存 {len(self.memory.memories)} 条记忆")
