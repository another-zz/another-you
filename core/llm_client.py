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
        if self.provider == "litellm":
            self._init_litellm()
        elif self.provider == "kimi":
            self._init_kimi()
        elif self.provider == "openai":
            self._init_openai()
        else:
            print(f"[LLM] 使用模拟模式")

    def _detect_provider(self) -> str:
        """检测可用的API提供商"""
        if os.getenv("ANTHROPIC_API_KEY") and "moonshot" in (os.getenv("ANTHROPIC_BASE_URL", "")):
            return "kimi"
        elif os.getenv("KIMI_API_KEY"):
            return "kimi"
        elif os.getenv("LITELLM_API_KEY"):
            return "litellm"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        else:
            return "mock"

    def _get_api_key(self) -> Optional[str]:
        """获取API Key"""
        if self.provider == "kimi":
            # 优先使用 ANTHROPIC_API_KEY (Claude Code 方式)
            return os.getenv("ANTHROPIC_API_KEY") or os.getenv("KIMI_API_KEY")
        elif self.provider == "litellm":
            return os.getenv("LITELLM_API_KEY", "dummy-key")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None

    def _init_kimi(self):
        """初始化Kimi客户端 - 使用Anthropic兼容接口"""
        try:
            # 尝试使用 Anthropic SDK
            from anthropic import Anthropic
            
            # 使用环境变量中的 base_url 或默认
            base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.moonshot.cn/anthropic/")
            
            self.client = Anthropic(
                api_key=self.api_key,
                base_url=base_url
            )
            self.model = "claude-sonnet-4-20250514"  # Kimi K2 使用这个模型名
            self.use_anthropic = True
            print(f"[LLM] ✅ Kimi API 已连接 (Anthropic兼容接口)")
            print(f"[LLM] 使用 base_url: {base_url}")
            
        except ImportError:
            # 回退到 OpenAI 接口
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.moonshot.cn/v1"
                )
                self.model = "kimi-k2.5"
                self.use_anthropic = False
                print(f"[LLM] ✅ Kimi API 已连接 (OpenAI兼容接口)")
            except ImportError as e:
                print(f"[LLM] ⚠️ 请安装依赖: pip install anthropic openai")
                print(f"[LLM] 错误: {e}")
                self.provider = "mock"

    def _init_litellm(self):
        """初始化LiteLLM代理客户端"""
        try:
            from openai import OpenAI
            
            # LiteLLM 代理地址
            self.base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1")
            self.model = os.getenv("LITELLM_MODEL", "kimi-coding")
            
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            print(f"[LLM] ✅ LiteLLM 代理已连接: {self.base_url}")
            print(f"[LLM] 使用模型: {self.model}")
        except ImportError as e:
            print(f"[LLM] ⚠️ 请安装openai库: pip install openai")
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

        # Kimi 使用 Anthropic 兼容接口
        if self.provider == "kimi" and hasattr(self, 'use_anthropic') and self.use_anthropic:
            try:
                # 转换消息格式为 Anthropic 格式
                system_msg = ""
                anthropic_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        system_msg = msg["content"]
                    else:
                        anthropic_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                response = self.client.messages.create(
                    model=self.model,
                    messages=anthropic_messages,
                    system=system_msg if system_msg else None,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
                return response.content[0].text
                
            except Exception as e:
                print(f"[LLM] Kimi Anthropic 调用失败: {e}")
                return self._mock_response(messages)

        # OpenAI / LiteLLM 使用 OpenAI SDK
        try:
            # 根据 provider 选择模型
            if self.provider == "litellm":
                model = getattr(self, 'model', 'kimi-coding')
            elif self.provider == "kimi":
                model = getattr(self, 'model', 'kimi-k2.5')
            else:
                model = "gpt-4"

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
