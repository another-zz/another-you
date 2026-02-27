"""
LLM Brain v0.9 - 真实LLM驱动的AI大脑

集成Kimi API，实现：
1. 真实LLM决策
2. 反思生成
3. 计划生成
4. 技能代码生成
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class LLMBrain:
    """
    AI大脑 v0.9
    
    使用真实LLM（Kimi K2.5）进行决策
    """
    
    def __init__(self, agent_name: str, api_key: str = None):
        self.agent_name = agent_name
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        self.conversation_history: List[Dict] = []
        
        # 统计
        self.total_calls = 0
        self.total_tokens = 0
        
    def _call_llm(self, prompt: str, system_prompt: str = "", 
                  temperature: float = 0.7) -> str:
        """
        调用LLM API
        
        当前使用模拟实现，实际部署时接入真实API
        """
        self.total_calls += 1
        
        # TODO: 接入真实Kimi API
        # from openai import OpenAI
        # client = OpenAI(api_key=self.api_key, base_url="https://api.moonshot.cn/v1")
        # response = client.chat.completions.create(
        #     model="kimi-k2.5",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=temperature
        # )
        # return response.choices[0].message.content
        
        # 模拟响应（用于测试）
        return self._simulate_response(prompt)
        
    def _simulate_response(self, prompt: str) -> str:
        """模拟LLM响应（测试用）"""
        prompt_lower = prompt.lower()
        
        # 决策相关
        if "决定" in prompt or "decide" in prompt_lower:
            return self._simulate_decision(prompt)
            
        # 反思相关
        if "反思" in prompt or "reflect" in prompt_lower:
            return self._simulate_reflection(prompt)
            
        # 计划相关
        if "计划" in prompt or "plan" in prompt_lower:
            return self._simulate_planning(prompt)
            
        # 技能相关
        if "技能" in prompt or "skill" in prompt_lower or "code" in prompt_lower:
            return self._simulate_skill_code(prompt)
            
        return "explore"
        
    def _simulate_decision(self, prompt: str) -> str:
        """模拟决策"""
        # 提取状态信息
        if "能量" in prompt and ("低" in prompt or "30" in prompt):
            return "rest"
        if "饥饿" in prompt and ("高" in prompt or "70" in prompt):
            return "gather_food"
        if "木头" in prompt or "wood" in prompt.lower():
            return "gather_wood"
        if "石头" in prompt or "stone" in prompt.lower():
            return "gather_stone"
        if "探索" in prompt or "explore" in prompt.lower():
            return "explore"
            
        # 随机选择
        import random
        actions = ["explore", "gather_wood", "gather_stone", "rest", "socialize"]
        return random.choice(actions)
        
    def _simulate_reflection(self, prompt: str) -> str:
        """模拟反思"""
        return """最近我主要在探索这个世界，收集基础资源。
我意识到需要更好地规划时间，平衡探索和休息。
我应该多与其他AI交流，建立社交关系。"""
        
    def _simulate_planning(self, prompt: str) -> str:
        """模拟计划生成"""
        return """{
  "overview": "今天我要探索周围环境，收集资源，建立基础",
  "goals": ["收集20个木头", "收集10个石头", "探索100格范围"],
  "schedule": [
    {"time": "06:00", "activity": "起床，检查环境"},
    {"time": "07:00", "activity": "收集木头"},
    {"time": "09:00", "activity": "收集石头"},
    {"time": "12:00", "activity": "休息"},
    {"time": "14:00", "activity": "探索"},
    {"time": "18:00", "activity": "返回"},
    {"time": "22:00", "activity": "休息"}
  ]
}"""
        
    def _simulate_skill_code(self, prompt: str) -> str:
        """模拟技能代码生成"""
        if "砍树" in prompt or "tree" in prompt.lower():
            return '''async function chopTree(bot) {
    const tree = bot.findBlock({
        matching: block => block.name.includes('log'),
        maxDistance: 32
    });
    if (tree) {
        await bot.pathfinder.goto(new GoalBlock(tree.position.x, tree.position.y, tree.position.z));
        await bot.dig(tree);
        bot.chat("砍了一棵树！");
        return true;
    }
    return false;
}'''
        elif "挖矿" in prompt or "mine" in prompt.lower():
            return '''async function mineStone(bot) {
    const stone = bot.findBlock({
        matching: block => block.name === 'stone',
        maxDistance: 16
    });
    if (stone) {
        await bot.dig(stone);
        return true;
    }
    return false;
}'''
        else:
            return '''async function customTask(bot) {
    bot.chat("开始执行任务");
    await bot.waitForTicks(20);
    return true;
}'''
        
    def decide(self, observation: Dict, memories: List[str], 
               skills: List[str], plan: str = "") -> str:
        """
        使用LLM决定下一步行动
        
        Args:
            observation: 当前观察
            memories: 相关记忆
            skills: 已掌握技能
            plan: 当前计划
            
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
- explore: 探索周围环境
- gather_wood: 收集木材
- gather_stone: 收集石头
- gather_food: 寻找食物
- rest: 休息恢复能量
- build: 建造庇护所
- craft: 制作工具
- socialize: 与其他AI互动

## 决策
基于以上信息，选择最合适的行动（只输出行动名称）："""

        action = self._call_llm(prompt, system_prompt)
        
        # 记录历史
        self.conversation_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": action,
            "timestamp": datetime.now().isoformat()
        })
        
        # 只保留最近20轮
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]
            
        return action.strip()
        
    def generate_reflection(self, recent_memories: List[str]) -> str:
        """
        生成反思
        
        Args:
            recent_memories: 近期记忆列表
            
        Returns:
            反思内容
        """
        system_prompt = "你是一个善于反思的AI。基于近期经历，总结洞察和教训。"
        
        prompt = f"""基于以下近期经历，生成一段反思：

{chr(10).join(f"- {m}" for m in recent_memories)}

反思（用第一人称）："""

        return self._call_llm(prompt, system_prompt)
        
    def generate_daily_plan(self, agent_state: Dict, 
                           recent_memories: List[str]) -> Dict:
        """
        生成日计划
        
        Args:
            agent_state: AI当前状态
            recent_memories: 近期记忆
            
        Returns:
            计划字典
        """
        system_prompt = "你是一个善于规划的AI。制定具体、可执行的日计划。"
        
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

        response = self._call_llm(prompt, system_prompt)
        
        # 尝试解析JSON
        try:
            return json.loads(response)
        except:
            return {
                "overview": "探索世界，收集资源",
                "goals": ["收集资源", "探索环境"],
                "schedule": []
            }
            
    def generate_skill_code(self, skill_name: str, 
                           description: str) -> str:
        """
        生成技能代码
        
        Args:
            skill_name: 技能名称
            description: 技能描述
            
        Returns:
            JavaScript代码
        """
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

        return self._call_llm(prompt, system_prompt)
        
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "history_length": len(self.conversation_history)
        }
