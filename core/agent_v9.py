"""
Agent v0.9 - 基于Memory Stream和真实LLM的AI数字分身

核心改进：
1. 使用Memory Stream替代简单记忆列表
2. 真实LLM驱动决策（预留API接口）
3. 日计划/小时计划架构
4. 自动反思机制
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List

from core.llm_brain_v9 import LLMBrain
from core.memory_stream import MemoryStream, ReflectionEngine, PlanningEngine
from core.mc_connector import MinecraftConnector
from core.skill_generator import SkillCodeGenerator
from core.world_coordinator import WorldCoordinator
from core.economy import EconomySystem


class Agent:
    """
    AI数字分身 v0.9
    
    基于Generative Agents架构：
    - Memory Stream: 完整的经历记录
    - Reflection: 定期反思总结
    - Planning: 日计划/小时计划
    - Real LLM: 真实AI驱动决策
    """
    
    def __init__(self, player_name: str, coordinator: WorldCoordinator = None,
                 mc_host: str = "localhost", mc_port: int = 25565,
                 api_key: str = None):
        self.player_name = player_name
        self.agent_id = f"{player_name}_{int(time.time())}"
        
        # 核心组件 - v0.9新架构
        self.brain = LLMBrain(player_name, api_key)
        self.memory = MemoryStream(self.agent_id)  # 新的Memory Stream
        self.reflection_engine = ReflectionEngine(self.memory)
        self.planning_engine = PlanningEngine(self.memory)
        
        # MC连接
        self.mc = MinecraftConnector(
            host=mc_host, port=mc_port,
            username=f"{player_name}_AI"
        )
        
        # 技能系统
        self.skill_gen = SkillCodeGenerator()
        self.learned_skills: List[str] = []
        
        # 经济系统
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
        self.reputation = 50
        
        # 规划
        self.daily_plan: Dict = None
        self.current_hour_plan: str = ""
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        self.is_running = False
        self.tick_interval = 5
        
        # 反思计数器
        self.ticks_since_reflection = 0
        self.reflection_interval = 20  # 每20个tick检查反思
        
    async def start_life(self):
        """开始自主生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」v0.9 已觉醒")
        print(f"   玩家: {self.player_name}")
        print(f"   架构: Memory Stream + LLM + Planning")
        print(f"{'='*60}\n")
        
        # 连接MC
        if self.mc.start():
            self.is_in_mc = True
            print("[系统] ✅ 已连接Minecraft")
            self.memory.add_observation(
                "我成功进入了Minecraft世界",
                importance=1.0,
                source="spawn"
            )
        else:
            print("[系统] ⚠️ 模拟模式")
            self.memory.add_observation(
                "进入模拟模式运行",
                importance=0.5,
                source="simulation"
            )
            
        # 生成日计划
        await self._generate_daily_plan()
        
        # 主循环
        while self.is_running:
            try:
                await self._life_tick()
                await asyncio.sleep(self.tick_interval)
            except Exception as e:
                print(f"[错误] {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(10)
                
    async def _generate_daily_plan(self):
        """生成日计划"""
        print(f"📋 [{self.player_name}] 制定今日计划...")
        
        agent_state = {
            "energy": self.energy,
            "hunger": self.hunger,
            "location": self.location,
            "inventory": self.inventory
        }
        
        # 获取相关记忆
        recent = self.memory.get_recent_observations(hours=24)
        memory_contents = [m.content for m in recent]
        
        # 使用LLM生成计划
        self.daily_plan = self.brain.generate_daily_plan(agent_state, memory_contents)
        
        # 记录计划到记忆流
        plan_content = f"今日计划: {self.daily_plan.get('overview', '探索世界')}"
        self.memory.add_plan(plan_content, plan_type="daily", importance=0.8)
        
        print(f"   目标: {self.daily_plan.get('overview')}")
        print(f"   子目标: {', '.join(self.daily_plan.get('goals', []))}")
        
    async def _life_tick(self):
        """生命节拍 - v0.9核心循环"""
        self.total_actions += 1
        self.ticks_since_reflection += 1
        
        # 1. 感知环境
        observation = self._perceive()
        
        # 2. 获取当前小时计划
        if self.daily_plan:
            self.current_hour_plan = self.planning_engine.get_current_hour_activity(self.daily_plan)
        
        # 3. 检索相关记忆
        query = f"{observation.get('energy')}%能量 {self.current_hour_plan}"
        relevant_memories = self.memory.retrieve(query, context=observation, top_k=5)
        memory_contents = [m.content for m in relevant_memories]
        
        # 4. LLM决策
        action = self.brain.decide(
            observation, 
            memory_contents, 
            self.learned_skills,
            plan=self.current_hour_plan
        )
        
        # 如果返回的是JSON（计划格式），提取第一个活动
        if action.startswith('{') or action.startswith('今天'):
            action = "explore"  # 默认行动
        
        # 5. 执行行动
        result = await self._execute(action)
        
        # 6. 记录观察
        self.memory.add_observation(
            f"{action}: {result}",
            importance=0.4 if result == "完成" else 0.6,
            location=self.location.copy(),
            source="action"
        )
        
        # 7. 检查社交
        if self.coordinator and self.total_actions % 10 == 0:
            await self._check_social()
            
        # 8. 检查反思
        if self.ticks_since_reflection >= self.reflection_interval:
            await self._check_reflection()
            self.ticks_since_reflection = 0
            
        # 9. 定期报告
        if self.total_actions % 12 == 0:
            self._report()
            
    async def _check_reflection(self):
        """检查是否需要反思"""
        recent = self.memory.get_recent_observations(hours=2)
        
        if len(recent) >= 10:
            print(f"🤔 [{self.player_name}] 正在反思...")
            
            # 生成反思
            memory_contents = [m.content for m in recent]
            reflection_content = self.brain.generate_reflection(memory_contents)
            
            # 记录反思
            related_ids = [m.id for m in recent]
            self.memory.add_reflection(
                reflection_content,
                importance=0.8,
                related_memories=related_ids
            )
            
            print(f"   💭 {reflection_content[:100]}...")
            
    async def _check_social(self):
        """检查社交机会"""
        if not self.coordinator:
            return
            
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
                    self.coordinator.facilitate_trade(
                        self.agent_id, partner, "stone", "wood"
                    )
                    
            # 交友
            if other_id not in self.friends:
                self.friends.append(other_id)
                self.memory.add_observation(
                    f"认识了{other.player_name}",
                    importance=0.6,
                    source="social"
                )
                print(f"[社交] {self.player_name} 认识了 {other.player_name}")
                
    async def _execute(self, action: str) -> str:
        """执行行动"""
        print(f"[{self.player_name}] {action}")
        
        # 学习新技能
        if action not in self.learned_skills and action not in ["rest", "explore", "socialize"]:
            print(f"  📝 学习新技能: {action}")
            skill = self.skill_gen.generate_skill(action)
            self.learned_skills.append(action)
            print(f"  ✅ 已掌握!")
            
        # 执行
        if self.is_in_mc:
            return await self._execute_mc(action)
        else:
            return await self._execute_sim(action)
            
    async def _execute_mc(self, action: str) -> str:
        """在真实MC中执行"""
        if action == "gather_wood":
            self.mc.dig(0, 0, 1)
            self.inventory["wood"] = self.inventory.get("wood", 0) + 1
            return "砍树获得木头"
        elif action == "gather_stone":
            self.mc.dig(0, -1, 0)
            self.inventory["stone"] = self.inventory.get("stone", 0) + 1
            return "挖矿获得石头"
        elif action == "explore":
            dx, dz = random.randint(-10, 10), random.randint(-10, 10)
            self.mc.move_to(
                self.location['x'] + dx,
                self.location['y'],
                self.location['z'] + dz
            )
            self.location['x'] += dx
            self.location['z'] += dz
            return f"移动到({self.location['x']}, {self.location['z']})"
        elif action == "rest":
            self.energy = min(100, self.energy + 20)
            self.mc.say("休息一下...")
            return "休息恢复能量"
        else:
            self.mc.say(f"我在{action}")
            return action
            
    async def _execute_sim(self, action: str) -> str:
        """模拟执行"""
        effects = {
            "rest": lambda: self._mod(20, 5),
            "gather_wood": lambda: self._mod(-10, 10) or self._add_item("wood", 3),
            "gather_stone": lambda: self._mod(-15, 15) or self._add_item("stone", 2),
            "gather_food": lambda: self._mod(-5, 5) or self._mod(0, -30),
            "explore": lambda: self._mod(-5, 5) or self._move(),
            "socialize": lambda: self._mod(-3, 3),
        }
        
        effect = effects.get(action, lambda: "未知")
        result = effect()
        
        await asyncio.sleep(1)
        return result or "完成"
        
    def _mod(self, e: float, h: float):
        """修改状态"""
        self.energy = max(0, min(100, self.energy + e))
        self.hunger = min(100, self.hunger + h)
        
    def _add_item(self, item: str, count: int):
        """添加物品"""
        self.inventory[item] = self.inventory.get(item, 0) + count
        
    def _move(self):
        """移动"""
        self.location["x"] += random.randint(-10, 10)
        self.location["z"] += random.randint(-10, 10)
        
    def _perceive(self) -> Dict:
        """感知环境"""
        if self.is_in_mc:
            # 从MC获取真实状态
            return {
                "source": "minecraft",
                "time": datetime.now().strftime("%H:%M"),
                "location": self.location.copy(),
                "energy": self.energy,
                "hunger": self.hunger,
                "inventory": self.inventory.copy(),
                "friends": len(self.friends),
            }
        else:
            return {
                "source": "simulated",
                "time": datetime.now().strftime("%H:%M"),
                "location": self.location.copy(),
                "energy": self.energy,
                "hunger": self.hunger,
                "nearby": ["草地", "树木", "石头", "河流"],
                "friends": len(self.friends),
            }
            
    def _report(self):
        """状态报告"""
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        wealth = self.economy.evaluate_inventory(self.inventory)
        
        print(f"\n📊 {self.player_name}")
        print(f"   存活: {age:.1f}分钟 | 行动: {self.total_actions}")
        print(f"   能量: {self.energy:.0f}% | 饥饿: {self.hunger:.0f}%")
        print(f"   财富: {wealth:.0f} | 朋友: {len(self.friends)}")
        print(f"   背包: {self.inventory}")
        print(f"   记忆: {self.memory.get_summary()}")
        if self.current_hour_plan:
            print(f"   当前计划: {self.current_hour_plan}")
            
    async def stop(self):
        """停止"""
        print(f"\n👋 {self.player_name} 休眠...")
        self.is_running = False
        
        if self.coordinator:
            self.coordinator.unregister_agent(self.agent_id)
            
        if self.is_in_mc:
            self.mc.stop()
            
        self.memory.save()
        print(f"💾 已保存记忆流")
