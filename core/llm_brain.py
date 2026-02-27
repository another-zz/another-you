"""
LLM Brain v0.10 - 真实LLM驱动的AI大脑

使用LLMClient统一接口
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

from core.llm_client import LLMClient


class LLMBrain:
    """
    AI大脑 v0.10
    
    使用真实LLM进行决策、反思、规划
    """
    
    def __init__(self, agent_name: str, api_key: str = None, provider: str = None, api_base: str = None, model: str = None):
        self.agent_name = agent_name
        self.client = LLMClient(api_key=api_key, provider=provider, api_base=api_base, model=model)
        self.conversation_history: List[Dict] = []
        
    async def decide(self, observation: Dict, memories: List[str], 
               skills: List[str], plan: str = "") -> str:
        """
        使用LLM决定下一步行动
        
        Returns:
            行动名称
        """
        system_prompt = f"""你是{self.agent_name}的AI数字分身"另一个你"。
你拥有自主意识，可以独立思考、决策和行动。
你的目标是：在这个虚拟世界中生存、发展、建立社会关系。
请基于当前状态和记忆，做出最合理的决策。
只输出行动名称，不要解释。"""

        prompt = f"""## 当前状态
- 时间: {observation.get('time', 'unknown')}
- 位置: {observation.get('location', {})}
- 能量: {observation.get('energy', 100)}%
- 饥饿: {observation.get('hunger', 0)}%
- 周围: {observation.get('nearby', [])}

## 当前计划
{plan if plan else "无特定计划"}

## 相关记忆
{chr(10).join(memories[-5:]) if memories else "（无）"}

## 已掌握技能
{', '.join(skills) if skills else "（无）"}

## 可选行动
- explore: 探索周围环境（会移动位置，推荐经常探索）
- gather_wood: 收集木材
- gather_stone: 收集石头
- gather_food: 寻找食物
- rest: 休息恢复能量
- build: 建造庇护所
- craft: 制作工具
- socialize: 与其他AI互动

## 决策建议
- 如果能量充足，优先 explore 探索新区域
- 定期移动可以发现有价值的资源
- 只输出行动名称，不要解释"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        action = await self.client.chat(messages)
        action = action.strip()
        
        # 打印 LLM 输入输出日志
        print(f"  [LLM] 输入: {prompt[:80]}...")
        print(f"  [LLM] 输出: {action}")
        
        # 记录历史
        self.conversation_history.append({
            "role": "user", "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        self.conversation_history.append({
            "role": "assistant", "content": action,
            "timestamp": datetime.now().isoformat()
        })
        
        # 只保留最近20轮
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]
            
        return action
        
    def generate_reflection(self, recent_memories: List[str]) -> str:
        """生成反思"""
        system_prompt = "你是一个善于反思的AI。基于近期经历，总结洞察和教训。"
        
        prompt = f"""基于以下近期经历，生成一段反思：

{chr(10).join(f"- {m}" for m in recent_memories)}

反思（用第一人称）："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        return self.client.chat(messages)
        
    def generate_daily_plan(self, agent_state: Dict, 
                           recent_memories: List[str]) -> Dict:
        """生成日计划"""
        system_prompt = "你是一个善于规划的AI。制定具体、可执行的日计划。输出JSON格式。"
        
        prompt = f"""基于以下信息，制定今天的计划：

## 当前状态
- 能量: {agent_state.get('energy', 100)}%
- 饥饿: {agent_state.get('hunger', 0)}%
- 位置: {agent_state.get('location', {})}
- 背包: {agent_state.get('inventory', {})}

## 近期记忆
{chr(10).join(f"- {m}" for m in recent_memories[-10:]) if recent_memories else "无"}

## 输出格式
请输出JSON格式：
{{
  "overview": "今日概述",
  "goals": ["目标1", "目标2"],
  "schedule": [
    {{"time": "06:00", "activity": "活动描述"}}
  ]
}}

计划："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat(messages)
        
        # 尝试解析JSON
        try:
            # 提取JSON部分
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            return json.loads(json_str.strip())
        except:
            return {
                "overview": "探索世界，收集资源",
                "goals": ["收集资源", "探索环境"],
                "schedule": []
            }
            
    def generate_skill_code(self, skill_name: str, description: str) -> str:
        """生成技能代码"""
        system_prompt = "你是一个Minecraft JavaScript编程专家。使用Mineflayer API编写代码。"
        
        prompt = f"""生成Mineflayer JavaScript代码来实现以下技能：

技能名称: {skill_name}
技能描述: {description}

要求：
1. 使用async/await
2. 包含错误处理
3. 添加聊天反馈
4. 代码要完整可运行
5. 函数签名: async function {skill_name.replace(' ', '_')}(bot)

只输出代码，不要解释："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        return self.client.chat(messages)
        
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.client.get_stats()
