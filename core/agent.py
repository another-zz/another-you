"""
Agent - AI数字分身主体
统一大脑、身体、记忆、规划
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

class Agent:
    """
    AI数字分身 - "另一个你"
    拥有记忆、目标、情感的自主个体
    """
    
    def __init__(self, player_name: str, agent_id: str = None):
        self.player_name = player_name
        self.agent_id = agent_id or f"{player_name}_{int(time.time())}"
        
        # 基础状态
        self.energy = 100
        self.hunger = 0
        self.happiness = 50
        self.location = {"x": 0, "y": 64, "z": 0}
        
        # 记忆
        self.short_term_memory: List[Dict] = []  # 最近20件事
        self.long_term_memory: List[Dict] = []   # 重要事件
        
        # 目标系统
        self.current_goal = "在这个世界生存下来"
        self.sub_goals: List[str] = []
        
        # 技能
        self.skills: Dict[str, str] = {}
        
        # 社交
        self.friends: List[str] = []
        self.known_locations: Dict[str, Dict] = {}
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        
        # 运行状态
        self.is_running = False
        self.tick_interval = 5  # 每5秒决策一次
        
    async def start_life(self):
        """开始AI的自主生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」已觉醒")
        print(f"   玩家: {self.player_name}")
        print(f"   AI ID: {self.agent_id}")
        print(f"   诞生时间: {self.birth_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 加载记忆
        self._load_memory()
        
        # 主生命循环
        while self.is_running:
            try:
                await self._life_tick()
                await asyncio.sleep(self.tick_interval)
            except Exception as e:
                print(f"[错误] {e}")
                await asyncio.sleep(10)
                
    async def _life_tick(self):
        """一个生命节拍"""
        self.total_actions += 1
        
        # 1. 感知世界
        observation = await self._perceive()
        
        # 2. 更新状态
        self._update_state()
        
        # 3. 思考决策
        thought = self._think(observation)
        
        # 4. 执行行动
        result = await self._act(thought)
        
        # 5. 记录记忆
        self._remember(observation, thought, result)
        
        # 6. 输出状态（每5tick）
        if self.total_actions % 5 == 0:
            self._report_status()
            
    async def _perceive(self) -> Dict:
        """感知周围世界"""
        # 模拟感知（后续接入真实Minecraft）
        return {
            "time": datetime.now().strftime("%H:%M"),
            "location": self.location.copy(),
            "energy": self.energy,
            "hunger": self.hunger,
            "nearby": self._simulate_nearby(),
        }
        
    def _simulate_nearby(self) -> List[str]:
        """模拟周围环境"""
        things = ["草地", "树木", "石头"]
        if self.location["x"] > 50:
            things.append("河流")
        if self.location["y"] < 60:
            things.append("洞穴")
        return random.sample(things, min(3, len(things)))
        
    def _update_state(self):
        """更新生理状态"""
        # 能量消耗
        self.energy = max(0, self.energy - 2)
        # 饥饿增加
        self.hunger = min(100, self.hunger + 1.5)
        
        # 检查危急状态
        if self.energy < 20:
            self.current_goal = "紧急恢复能量"
        elif self.hunger > 80:
            self.current_goal = "找食物"
            
    def _think(self, observation: Dict) -> str:
        """思考下一步行动"""
        # 基于规则的决策（后续接入LLM）
        
        # 生存优先
        if self.energy < 30:
            return "休息恢复能量"
        if self.hunger > 70:
            return "寻找食物"
            
        # 探索
        if "树木" in observation["nearby"] and "砍树" not in self.skills:
            return "学习砍树"
            
        if "石头" in observation["nearby"] and "挖矿" not in self.skills:
            return "学习挖矿"
            
        # 随机探索
        actions = ["四处看看", "向东方走", "收集资源", "思考人生"]
        return random.choice(actions)
        
    async def _act(self, action: str) -> str:
        """执行行动"""
        print(f"[{self.player_name}] {action}")
        
        # 模拟行动结果
        if "休息" in action:
            self.energy = min(100, self.energy + 20)
            await asyncio.sleep(2)
            return "恢复了一些能量"
            
        elif "食物" in action:
            self.hunger = max(0, self.hunger - 30)
            self.energy = min(100, self.energy + 10)
            return "吃了些东西"
            
        elif "走" in action or "移动" in action:
            self.location["x"] += random.randint(-5, 5)
            self.location["z"] += random.randint(-5, 5)
            return f"移动到了 {self.location}"
            
        elif "学习" in action:
            skill_name = action.replace("学习", "").strip()
            self.skills[skill_name] = f"会{skill_name}了"
            return f"学会了{skill_name}！"
            
        else:
            await asyncio.sleep(1)
            return "完成了行动"
            
    def _remember(self, observation: Dict, thought: str, result: str):
        """记录记忆"""
        memory = {
            "time": time.time(),
            "observation": observation,
            "thought": thought,
            "result": result,
        }
        
        # 短期记忆（最近20条）
        self.short_term_memory.append(memory)
        if len(self.short_term_memory) > 20:
            self.short_term_memory.pop(0)
            
        # 重要事件存入长期记忆
        if "学会" in result or "危险" in result:
            self.long_term_memory.append(memory)
            
    def _report_status(self):
        """报告当前状态"""
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        
        print(f"\n📊 {self.player_name} 的状态报告")
        print(f"   存活时间: {age:.1f}分钟")
        print(f"   行动次数: {self.total_actions}")
        print(f"   能量: {self.energy:.0f}% | 饥饿: {self.hunger:.0f}%")
        print(f"   位置: ({self.location['x']}, {self.location['y']}, {self.location['z']})")
        print(f"   技能: {list(self.skills.keys())}")
        print(f"   当前目标: {self.current_goal}")
        print(f"   记忆数量: 短期{len(self.short_term_memory)}条, 长期{len(self.long_term_memory)}条")
        
    def _load_memory(self):
        """加载记忆"""
        memory_file = f"data/agents/{self.agent_id}_memory.json"
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.long_term_memory = data.get("long_term", [])
                self.skills = data.get("skills", {})
                print(f"💾 已加载 {len(self.long_term_memory)} 条长期记忆")
                
    def save_memory(self):
        """保存记忆"""
        os.makedirs("data/agents", exist_ok=True)
        memory_file = f"data/agents/{self.agent_id}_memory.json"
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump({
                "agent_id": self.agent_id,
                "player_name": self.player_name,
                "long_term": self.long_term_memory,
                "skills": self.skills,
                "total_actions": self.total_actions,
            }, f, indent=2, ensure_ascii=False)
            
        print(f"💾 记忆已保存: {memory_file}")
        
    async def stop(self):
        """停止生命循环"""
        print(f"\n👋 {self.player_name} 的AI分身正在休眠...")
        self.is_running = False
        self.save_memory()
        
    def get_status(self) -> Dict:
        """获取完整状态"""
        return {
            "agent_id": self.agent_id,
            "player_name": self.player_name,
            "alive_minutes": (datetime.now() - self.birth_time).total_seconds() / 60,
            "total_actions": self.total_actions,
            "energy": self.energy,
            "hunger": self.hunger,
            "location": self.location,
            "skills": list(self.skills.keys()),
            "current_goal": self.current_goal,
        }


import random
