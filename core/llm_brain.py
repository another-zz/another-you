"""
LLM Brain - AI大脑（接入真实LLM）
使用Kimi K2.5进行决策
"""

import json
import os
from typing import Dict, List, Optional

class LLMBrain:
    """
    AI大脑 - 使用LLM进行决策
    当前使用Kimi K2.5
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.conversation_history: List[Dict] = []
        
    def decide(self, observation: Dict, memories: List[str], skills: List[str]) -> str:
        """
        使用LLM决定下一步行动
        
        由于当前环境无法直接调用API，使用模拟LLM响应
        实际部署时接入Kimi API
        """
        
        # 构建提示
        prompt = self._build_prompt(observation, memories, skills)
        
        # 模拟LLM决策（基于规则的高级版本）
        action = self._simulate_llm_decision(observation, memories, skills)
        
        # 记录历史
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        self.conversation_history.append({
            "role": "assistant", 
            "content": action
        })
        
        # 只保留最近10轮
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
            
        return action
        
    def _build_prompt(self, observation: Dict, memories: List[str], skills: List[str]) -> str:
        """构建提示词"""
        return f"""你是{self.agent_name}的AI数字分身"另一个你"。

## 当前状态
- 时间: {observation.get('time', 'unknown')}
- 位置: {observation.get('location', {})}
- 能量: {observation.get('energy', 100)}%
- 饥饿: {observation.get('hunger', 0)}%
- 周围: {observation.get('nearby', [])}

## 相关记忆
{chr(10).join(memories[-5:]) if memories else "（无）"}

## 已掌握技能
{', '.join(skills) if skills else "（无）"}

## 你的任务
基于以上信息，决定下一步行动。
可选行动：
- explore: 探索周围环境
- gather_wood: 收集木材
- gather_food: 寻找食物
- rest: 休息恢复能量
- build: 建造庇护所
- craft: 制作工具
- social: 与其他AI互动

只输出行动名称，不要解释。"""

    def _simulate_llm_decision(self, observation: Dict, memories: List[str], skills: List[str]) -> str:
        """
        模拟LLM决策（智能规则版）
        实际部署时替换为真实API调用
        """
        energy = observation.get('energy', 100)
        hunger = observation.get('hunger', 0)
        nearby = observation.get('nearby', [])
        
        # 生存优先
        if energy < 30:
            return "rest"
        if hunger > 70:
            return "gather_food"
            
        # 技能发展
        if "wood" not in skills and "tree" in nearby:
            return "gather_wood"
            
        if len(skills) >= 2 and "build" not in skills:
            return "build"
            
        # 探索
        return "explore"
        
    def reflect(self, recent_events: List[str]) -> str:
        """
        反思总结
        返回反思内容
        """
        if len(recent_events) < 3:
            return ""
            
        # 模拟反思
        reflection = f"""最近我完成了{len(recent_events)}个行动。
主要在做：{recent_events[-1]}。
感觉需要继续发展技能，同时注意保持能量。"""

        return reflection
        
    def generate_skill_code(self, skill_name: str, description: str) -> str:
        """
        生成技能代码
        实际部署时使用LLM生成Mineflayer代码
        """
        # 模拟代码生成
        templates = {
            "gather_wood": """
async function gatherWood(bot, times = 5) {
    for(let i = 0; i < times; i++) {
        const tree = bot.findBlock({
            matching: block => block.name.includes('log'),
            maxDistance: 32
        });
        if(tree) {
            await bot.pathfinder.goto(new GoalBlock(tree.position.x, tree.position.y, tree.position.z));
            await bot.dig(tree);
        }
    }
}""",
            "gather_food": """
async function gatherFood(bot) {
    // 寻找动物
    const animals = bot.entities.filter(e => 
        ['pig', 'cow', 'chicken'].includes(e.name)
    );
    if(animals.length > 0) {
        const target = animals[0];
        await bot.pathfinder.goto(new GoalEntity(target));
        // 攻击获取食物
    }
}""",
        }
        
        return templates.get(skill_name, "// TODO: 生成代码")
