"""
Agent Brain - AI数字分身大脑
基于LangGraph + 长期记忆 + 自主决策
"""

import json
import time
from typing import Dict, List, Optional, TypedDict
from datetime import datetime

class AgentState(TypedDict):
    """AI状态"""
    observation: str          # 当前观察
    memory_context: str       # 相关记忆
    plan: List[str]          # 当前计划
    action: str              # 下一步行动
    reflection: str          # 反思

class AgentBrain:
    """AI大脑 - 另一个你的核心"""
    
    def __init__(self, agent_id: str, player_name: str, llm_client=None):
        self.agent_id = agent_id
        self.player_name = player_name
        self.llm = llm_client
        
        # 状态
        self.energy = 100
        self.hunger = 0
        self.location = {"x": 0, "y": 0, "z": 0}
        self.inventory = {}
        
        # 记忆
        self.short_term_memory = []  # 最近10件事
        self.long_term_memory = []   # 重要事件
        
        # 目标
        self.current_goal = "生存并建立基地"
        self.daily_plan = []
        
        # 统计
        self.birth_time = datetime.now()
        self.total_actions = 0
        
    def perceive(self, observation: Dict) -> str:
        """感知世界"""
        # 格式化观察
        obs_text = f"""
时间: {datetime.now().strftime('%H:%M')}
位置: {observation.get('position', 'unknown')}
周围: {observation.get('nearby_blocks', [])}
物品: {observation.get('inventory', {})}
血量: {observation.get('health', 20)}/20
饥饿: {observation.get('food', 20)}/20
        """.strip()
        
        # 存入短期记忆
        self.short_term_memory.append({
            "time": time.time(),
            "observation": obs_text
        })
        
        # 只保留最近10条
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
            
        return obs_text
        
    def think(self, observation: str) -> str:
        """思考决策"""
        # 检索相关记忆
        relevant_memories = self._retrieve_memories(observation)
        
        # 构建提示
        prompt = f"""你是{self.player_name}的AI数字分身"另一个你"。
玩家已经下线，你需要像真人一样自主生活。

## 你的记忆
{relevant_memories}

## 最近发生的事
{self._format_short_term_memory()}

## 当前观察
{observation}

## 你的当前目标
{self.current_goal}

基于以上信息，决定你下一步要做什么。
只输出一个具体的行动指令，例如：
- "去东边找木头"
- "回家睡觉"
- "在原地挖矿"
- "建造一个工作台"

你的决定："""

        # 调用LLM（如果没有LLM，使用简单规则）
        if self.llm:
            action = self.llm.generate(prompt)
        else:
            action = self._rule_based_decision(observation)
            
        self.total_actions += 1
        
        # 记录到记忆
        self._add_memory(f"我决定: {action}")
        
        return action
        
    def _rule_based_decision(self, observation: str) -> str:
        """基于规则的决策（无LLM时的备用）"""
        obs_lower = observation.lower()
        
        # 生存优先
        if "血量" in obs_lower and "10" in obs_lower:
            return "找安全的地方躲避"
        if "饥饿" in obs_lower and "10" in obs_lower:
            return "去找食物"
        if "晚上" in obs_lower or "黑夜" in obs_lower:
            return "回家睡觉"
            
        # 资源收集
        if "木头" not in obs_lower:
            return "去砍树收集木头"
        if "石头" not in obs_lower:
            return "去挖矿收集石头"
            
        # 建设
        return "建造一个简单的房子"
        
    def reflect(self) -> str:
        """反思 - 每天一次"""
        if len(self.short_term_memory) < 5:
            return ""
            
        # 总结今天做了什么
        recent_actions = [m["observation"] for m in self.short_term_memory[-5:]]
        
        reflection = f"""
今天总结：
- 完成了{self.total_actions}个行动
- 最近在做：{recent_actions}
- 当前目标进度：{self.current_goal}

明天计划：继续建设基地，收集更多资源。
        """.strip()
        
        self._add_to_long_term_memory(reflection)
        return reflection
        
    def _retrieve_memories(self, query: str) -> str:
        """检索相关记忆"""
        # 简化版：返回最近的重要记忆
        if not self.long_term_memory:
            return "（还没有长期记忆）"
        return "\n".join(self.long_term_memory[-3:])
        
    def _format_short_term_memory(self) -> str:
        """格式化短期记忆"""
        if not self.short_term_memory:
            return "（无）"
        return "\n".join([m["observation"] for m in self.short_term_memory[-3:]])
        
    def _add_memory(self, event: str):
        """添加记忆"""
        self.short_term_memory.append({
            "time": time.time(),
            "observation": event
        })
        
    def _add_to_long_term_memory(self, memory: str):
        """添加到长期记忆"""
        self.long_term_memory.append(memory)
        
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "agent_id": self.agent_id,
            "player_name": self.player_name,
            "age_hours": (datetime.now() - self.birth_time).total_seconds() / 3600,
            "total_actions": self.total_actions,
            "current_goal": self.current_goal,
            "location": self.location,
            "inventory": self.inventory,
        }
