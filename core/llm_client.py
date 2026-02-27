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

            # 判断是否是 Kimi Code
            is_kimi_code = "kimi" in (self.api_key or "").lower()

            if is_kimi_code:
                # Kimi Code API - 需要特殊处理 User-Agent
                self.base_url = "https://api.kimi.com/coding/v1"
                self.model = "kimi-k2.5"
                self.is_kimi_code = True
                print(f"[LLM] 使用 Kimi Code API: {self.base_url}")

                # 使用 httpx 自定义请求
                import httpx
                self.http_client = httpx.Client(
                    base_url=self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "User-Agent": "Kimi-Code-CLI/1.0",  # 模拟官方 CLI
                        "Content-Type": "application/json"
                    }
                )
                print(f"[LLM] ✅ Kimi Code API 已连接")
            else:
                # 普通 Kimi API
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.moonshot.cn/v1"
                )
                self.is_kimi_code = False
                print(f"[LLM] ✅ Kimi API 已连接")

        except ImportError as e:
            print(f"[LLM] ⚠️ 请安装依赖: pip install openai httpx")
            print(f"[LLM] 错误: {e}")
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
        """
        self.total_calls += 1

        if self.provider == "mock":
            return self._mock_response(messages)

        # Kimi Code 使用 httpx 直接请求
        if hasattr(self, 'is_kimi_code') and self.is_kimi_code:
            try:
                response = self.http_client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[LLM] Kimi Code 调用失败: {e}")
                return self._mock_response(messages)

        # 普通 Kimi 使用 OpenAI SDK
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
            error_msg = str(e)
            if "401" in error_msg or "Authentication" in error_msg:
                print(f"[LLM] API认证失败，切换到mock模式")
                self.provider = "mock"
            else:
                print(f"[LLM] API调用失败: {error_msg[:100]}")
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
        """模拟决策 - 带生存优先级"""
        import random
        import re

        # 从prompt中提取能量和饥饿值
        energy = 100
        hunger = 0

        energy_match = re.search(r'能量[:\s]+(\d+)', prompt)
        hunger_match = re.search(r'饥饿[:\s]+(\d+)', prompt)

        if energy_match:
            energy = int(energy_match.group(1))
        if hunger_match:
            hunger = int(hunger_match.group(1))

        # ===== 生存优先级判断（最高优先级）=====

        # 1. 能量极低 -> 必须休息
        if energy < 20:
            return "rest"

        # 2. 饥饿极高 -> 必须找食物
        if hunger > 80:
            return "gather_food"

        # 3. 能量偏低 -> 优先休息
        if energy < 40:
            return "rest"

        # 4. 饥饿偏高 -> 优先找食物
        if hunger > 50:
            return "gather_food"

        # ===== 资源采集优先级（平衡发展）=====

        # 5. 随机多样化行动（避免一直explore）
        actions = ["gather_wood", "gather_stone", "gather_food", "explore", "socialize"]
        weights = [0.30, 0.30, 0.20, 0.10, 0.10]  # 优先采集资源
        return random.choices(actions, weights=weights)[0]

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
