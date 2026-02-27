"""
Agent v0.10 - 真实LLM + 技能执行的AI数字分身

核心改进：
1. 使用LLMClient统一接口
2. SkillExecutor真实执行技能
3. 完整的观察-决策-执行-反馈循环
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List

from core.llm_brain_v10 import LLMBrain
from core.memory_stream import MemoryStream
from core.mc_connector import MinecraftConnector
from core.skill_executor import SkillExecutor, SkillLibrary
from core.world_coordinator import WorldCoordinator
from core.economy import EconomySystem


class Agent:
    """
    AI数字分身 v0.10
    
    完整能力：
    - Memory Stream记忆
    - LLM驱动决策
    - 真实技能执行
    - 社会交互
    """
    
    def __init__(self, player_name: str, coordinator: WorldCoordinator = None,
                 mc_host: str = "localhost", mc_port: int = 25565,
                 api_key: str = None, provider: str = None):
        self.player_name = player_name
        self.agent_id = f"{player_name}_{int(time.time())}"
        
        # 核心组件
        self.brain = LLMBrain(player_name, api_key=api_key, provider=provider)
        self.memory = MemoryStream(self.agent_id)
        
        # MC连接
        self.mc = MinecraftConnector(
            host=mc_host, port=mc_port,
            username=f"{player_name}_AI"
        )
        
        # 技能系统
        self.skill_executor = SkillExecutor(mc_host, mc_port)
        self.skill_library = SkillLibrary()
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
        
        # 反思
        self.ticks_since_reflection = 0
        self.reflection_interval = 20
        
    async def start_life(self):
        """开始自主生活"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」v0.10 已觉醒")
        print(f"   玩家: {self.player_name}")
        print(f"   架构: Memory Stream + LLM + Skill Execution")
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
            print("[系统] ⚠️ 模拟模式（技能执行受限）")
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
        
        recent = self.memory.get_recent_observations(hours=24)
        memory_contents = [m.content for m in recent]
        
        self.daily_plan = self.brain.generate_daily_plan(agent_state, memory_contents)
        
        plan_content = f"今日计划: {self.daily_plan.get('overview', '探索世界')}"
        self.memory.add_plan(plan_content, plan_type="daily", importance=0.8)
        
        print(f"   目标: {self.daily_plan.get('overview')}")
        print(f"   子目标: {', '.join(self.daily_plan.get('goals', []))}")
        
    async def _life_tick(self):
        """生命节拍"""
        self.total_actions += 1
        self.ticks_since_reflection += 1
        
        # 1. 感知
        observation = self._perceive()
        
        # 2. 获取当前计划
        if self.daily_plan:
            self.current_hour_plan = self._get_current_activity()
        
        # 3. 检索记忆
        query = f"{observation.get('energy')}%能量 {self.current_hour_plan}"
        relevant_memories = self.memory.retrieve(query, context=observation, top_k=5)
        memory_contents = [m.content for m in relevant_memories]
        
        # 4. LLM决策
        action = self.brain.decide(
            observation, memory_contents, self.learned_skills,
            plan=self.current_hour_plan
        )
        
        # 清理action（防止返回JSON或长文本）
        action = self._sanitize_action(action)
        
        # 5. 执行
        result = await self._execute(action)
        
        # 6. 记录
        self.memory.add_observation(
            f"{action}: {result}",
            importance=0.4 if "完成" in result else 0.6,
            location=self.location.copy(),
            source="action"
        )
        
        # 7. 社交
        if self.coordinator and self.total_actions % 10 == 0:
            await self._check_social()
            
        # 8. 反思
        if self.ticks_since_reflection >= self.reflection_interval:
            await self._check_reflection()
            self.ticks_since_reflection = 0
            
        # 9. 报告
        if self.total_actions % 12 == 0:
            self._report()
            
    def _sanitize_action(self, action: str) -> str:
        """清理action，确保是有效的行动名称"""
        action = action.strip().lower()
        
        # 如果包含JSON，使用默认行动
        if action.startswith('{') or len(action) > 50:
            return "explore"
            
        # 有效行动列表
        valid_actions = [
            "explore", "gather_wood", "gather_stone", "gather_food",
            "rest", "build", "craft", "socialize", "mine", "chop_tree"
        ]
        
        # 模糊匹配
        for valid in valid_actions:
            if valid in action or action in valid:
                return valid
                
        return "explore"
        
    def _get_current_activity(self) -> str:
        """获取当前小时的活动"""
        if not self.daily_plan:
            return "自由探索"
            
        current_hour = datetime.now().hour
        schedule = self.daily_plan.get('schedule', [])
        
        for item in schedule:
            item_hour = int(item.get('time', '00:00').split(':')[0])
            if item_hour == current_hour:
                return item.get('activity', '自由探索')
                
        return "自由探索"
        
    async def _check_reflection(self):
        """检查反思"""
        recent = self.memory.get_recent_observations(hours=2)
        
        if len(recent) >= 10:
            print(f"🤔 [{self.player_name}] 正在反思...")
            
            memory_contents = [m.content for m in recent]
            reflection_content = self.brain.generate_reflection(memory_contents)
            
            related_ids = [m.id for m in recent]
            self.memory.add_reflection(
                reflection_content,
                importance=0.8,
                related_memories=related_ids
            )
            
            print(f"   💭 {reflection_content[:80]}...")
            
    async def _check_social(self):
        """检查社交"""
        if not self.coordinator:
            return
            
        nearby = self.coordinator.get_nearby_agents(self.location, 100)
        
        for other_id in nearby:
            other = self.coordinator.agents.get(other_id)
            if not other:
                continue
                
            # 交易
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
                print(f"[社交] {self.player_name} ↔ {other.player_name}")
                
    async def _execute(self, action: str) -> str:
        """执行行动"""
        print(f"[{self.player_name}] {action}")
        
        # 检查技能库
        skill = self.skill_library.get_skill(action)
        
        if skill and self.is_in_mc:
            # 执行已有技能
            print(f"  🎯 执行技能: {action}")
            result = self.skill_executor.execute(skill['code'], action)
            
            if result['success']:
                self.skill_library.update_skill_stats(action, True)
                return f"技能执行成功: {result['output'][:50]}"
            else:
                self.skill_library.update_skill_stats(action, False)
                return f"技能执行失败: {result['error'][:50]}"
                
        elif action not in self.learned_skills:
            # 学习新技能
            print(f"  📝 学习新技能: {action}")
            code = self.brain.generate_skill_code(action, f"执行{action}任务")
            
            # 验证代码
            errors = self.skill_executor.validate_code(code)
            if errors:
                print(f"  ⚠️ 代码验证警告: {errors}")
                
            # 保存到技能库
            self.skill_library.add_skill(action, code, f"{action}技能")
            self.learned_skills.append(action)
            
            # 如果是MC模式，尝试执行
            if self.is_in_mc:
                result = self.skill_executor.execute(code, action)
                if result['success']:
                    return f"新技能学习并执行成功"
                else:
                    return f"新技能学习但执行失败: {result['error'][:30]}"
            else:
                print(f"  ✅ 技能已记录（模拟模式不执行）")
                return "技能已学习（模拟模式）"
        else:
            # 已掌握的技能，模拟执行
            return await self._execute_sim(action)
            
    async def _execute_sim(self, action: str) -> str:
        """模拟执行"""
        effects = {
            "rest": lambda: self._mod(20, 5),
            "gather_wood": lambda: self._mod(-10, 10) or self._add_item("wood", 3),
            "gather_stone": lambda: self._mod(-15, 15) or self._add_item("stone", 2),
            "gather_food": lambda: self._mod(-5, 5) or self._mod(0, -30),
            "explore": lambda: self._mod(-5, 5) or self._move(),
            "socialize": lambda: self._mod(-3, 3),
            "mine": lambda: self._mod(-15, 15) or self._add_item("stone", 2),
            "chop_tree": lambda: self._mod(-10, 10) or self._add_item("wood", 3),
        }
        
        effect = effects.get(action, lambda: "未知")
        result = effect()
        
        await asyncio.sleep(1)
        return result or "完成"
        
    def _mod(self, e: float, h: float):
        self.energy = max(0, min(100, self.energy + e))
        self.hunger = min(100, self.hunger + h)
        
    def _add_item(self, item: str, count: int):
        self.inventory[item] = self.inventory.get(item, 0) + count
        
    def _move(self):
        self.location["x"] += random.randint(-10, 10)
        self.location["z"] += random.randint(-10, 10)
        
    def _perceive(self) -> Dict:
        if self.is_in_mc:
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
        age = (datetime.now() - self.birth_time).total_seconds() / 60
        wealth = self.economy.evaluate_inventory(self.inventory)
        llm_stats = self.brain.get_stats()
        
        print(f"\n📊 {self.player_name}")
        print(f"   存活: {age:.1f}分钟 | 行动: {self.total_actions}")
        print(f"   能量: {self.energy:.0f}% | 饥饿: {self.hunger:.0f}%")
        print(f"   财富: {wealth:.0f} | 朋友: {len(self.friends)}")
        print(f"   技能: {len(self.learned_skills)}个")
        print(f"   背包: {self.inventory}")
        print(f"   记忆: {self.memory.get_summary()}")
        print(f"   LLM: {llm_stats['provider']} | 调用{llm_stats['total_calls']}次")
        if self.current_hour_plan:
            print(f"   当前: {self.current_hour_plan}")
            
    async def stop(self):
        print(f"\n👋 {self.player_name} 休眠...")
        self.is_running = False
        
        if self.coordinator:
            self.coordinator.unregister_agent(self.agent_id)
            
        if self.is_in_mc:
            self.mc.stop()
            
        self.memory.save()
        print(f"💾 已保存记忆流")
        print(f"📚 技能库: {len(self.skill_library.skills)}个技能")
