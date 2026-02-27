"""
LLM Client - 统一LLM调用接口

支持：
- Kimi (Moonshot)
- OpenAI
- 本地模型
- 模拟模式（测试用）
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class LLMClient:
    """
    统一LLM客户端
    
    自动检测可用API，按优先级选择：
    1. Kimi API (KIMI_API_KEY)
    2. OpenAI API (OPENAI_API_KEY)
    3. 模拟模式
    """
    
    def __init__(self, api_key: str = None, provider: str = None):
        self.provider = provider or self._detect_provider()
        self.api_key = api_key or self._get_api_key()
        self.client = None
        
        # 统计
        self.total_calls = 0
        self.total_tokens = 0
        
        # 初始化客户端
        if self.provider == "kimi":
            self._init_kimi()
        elif self.provider == "openai":
            self._init_openai()
        else:
            print(f"[LLM] 使用模拟模式")
            
    def _detect_provider(self) -> str:
        """检测可用的API提供商"""
        if os.getenv("KIMI_API_KEY"):
            return "kimi"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        else:
            return "mock"
            
    def _get_api_key(self) -> Optional[str]:
        """获取API Key"""
        if self.provider == "kimi":
            return os.getenv("KIMI_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None
        
    def _init_kimi(self):
        """初始化Kimi客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.moonshot.cn/v1"
            )
            print(f"[LLM] ✅ Kimi API 已连接")
        except ImportError:
            print(f"[LLM] ⚠️ 请安装openai库: pip install openai")
            self.provider = "mock"
            
    def _init_openai(self):
        """初始化OpenAI客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            print(f"[LLM] ✅ OpenAI API 已连接")
        except ImportError:
            print(f"[LLM] ⚠️ 请安装openai库: pip install openai")
            self.provider = "mock"
            
    def chat(self, messages: List[Dict], temperature: float = 0.7, 
             max_tokens: int = 2000) -> str:
        """
        调用LLM进行对话
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            LLM响应文本
        """
        self.total_calls += 1
        
        if self.provider == "mock":
            return self._mock_response(messages)
            
        try:
            model = "kimi-k2.5" if self.provider == "kimi" else "gpt-4"
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            self.total_tokens += response.usage.total_tokens
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[LLM] API调用失败: {e}")
            return self._mock_response(messages)
            
    def _mock_response(self, messages: List[Dict]) -> str:
        """模拟响应（测试用）"""
        last_message = messages[-1]["content"] if messages else ""
        last_lower = last_message.lower()
        
        # 决策相关
        if "决定" in last_message or "decide" in last_lower:
            return self._mock_decision(last_message)
            
        # 反思相关
        if "反思" in last_message or "reflect" in last_lower:
            return self._mock_reflection(last_message)
            
        # 计划相关
        if "计划" in last_message or "plan" in last_lower:
            return self._mock_planning(last_message)
            
        # 技能相关
        if "技能" in last_message or "code" in last_lower:
            return self._mock_skill_code(last_message)
            
        return "explore"
        
    def _mock_decision(self, prompt: str) -> str:
        """模拟决策"""
        if "能量" in prompt and ("低" in prompt or "30" in prompt):
            return "rest"
        if "饥饿" in prompt and ("高" in prompt or "70" in prompt):
            return "gather_food"
        if "木头" in prompt or "wood" in prompt.lower():
            return "gather_wood"
        if "石头" in prompt or "stone" in prompt.lower():
            return "gather_stone"
            
        import random
        actions = ["explore", "gather_wood", "gather_stone", "rest", "socialize"]
        return random.choice(actions)
        
    def _mock_reflection(self, prompt: str) -> str:
        """模拟反思"""
        return """最近我主要在探索这个世界，收集基础资源。
我意识到需要更好地规划时间，平衡探索和休息。
我应该多与其他AI交流，建立社交关系。"""
        
    def _mock_planning(self, prompt: str) -> str:
        """模拟计划"""
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
        
    def _mock_skill_code(self, prompt: str) -> str:
        """模拟技能代码"""
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
        return "// TODO: 生成代码"
        
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "provider": self.provider,
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens
        }
