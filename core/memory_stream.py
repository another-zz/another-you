"""
Memory Stream - 基于Stanford Generative Agents的记忆架构

核心组件：
1. Memory Stream: 时间顺序记录所有经历
2. Retrieval: 基于相关性、时效性、重要性的检索
3. Reflection: 定期总结高阶洞察
4. Planning: 日计划/小时计划
"""

import json
import os
import hashlib
import time
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class MemoryRecord:
    """单条记忆记录"""
    id: str
    content: str                    # 自然语言描述
    memory_type: str               # observation/reflection/plan
    importance: float              # 0-1
    timestamp: datetime
    access_count: int = 0
    last_access: Optional[datetime] = None
    
    # 元数据
    source: str = ""               # 来源（感知/反思/计划）
    location: Optional[Dict] = None
    related_memories: List[str] = None  # 关联记忆ID
    
    def __post_init__(self):
        if self.related_memories is None:
            self.related_memories = []


class MemoryStream:
    """
    记忆流系统
    
    设计原则：
    - 所有经历按时间顺序记录
    - 支持语义检索
    - 自动触发反思
    - 支持层次化规划
    """
    
    def __init__(self, agent_id: str, memory_dir: str = "data/memories"):
        self.agent_id = agent_id
        self.memory_dir = memory_dir
        self.memories: List[MemoryRecord] = []
        
        # 反思相关
        self.reflection_threshold = 100  # 多少条记忆触发反思
        self.last_reflection_idx = 0
        
        # 规划相关
        self.current_plan: Optional[Dict] = None
        self.daily_plans: List[Dict] = []
        
        # 确保目录存在
        os.makedirs(memory_dir, exist_ok=True)
        self._load()
        
    def _load(self):
        """加载记忆"""
        filepath = os.path.join(self.memory_dir, f"{self.agent_id}_stream.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for m in data:
                    m['timestamp'] = datetime.fromisoformat(m['timestamp'])
                    if m.get('last_access'):
                        m['last_access'] = datetime.fromisoformat(m['last_access'])
                    self.memories.append(MemoryRecord(**m))
            print(f"💾 [{self.agent_id}] 加载了 {len(self.memories)} 条记忆")
            
    def save(self):
        """保存记忆"""
        filepath = os.path.join(self.memory_dir, f"{self.agent_id}_stream.json")
        data = []
        for m in self.memories:
            d = asdict(m)
            d['timestamp'] = m.timestamp.isoformat()
            d['last_access'] = m.last_access.isoformat() if m.last_access else None
            data.append(d)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def add_observation(self, content: str, importance: float = 0.5, 
                       location: Dict = None, source: str = "") -> str:
        """
        添加观察记忆
        
        Args:
            content: 观察内容描述
            importance: 重要性 0-1
            location: 位置信息 {"x": 0, "y": 64, "z": 0}
            source: 来源标记
        """
        memory_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:12]
        
        memory = MemoryRecord(
            id=memory_id,
            content=content,
            memory_type="observation",
            importance=importance,
            timestamp=datetime.now(),
            source=source,
            location=location
        )
        
        self.memories.append(memory)
        
        # 检查是否需要触发反思
        if len(self.memories) - self.last_reflection_idx >= self.reflection_threshold:
            self._trigger_reflection()
            
        return memory_id
        
    def add_reflection(self, content: str, importance: float = 0.8,
                      related_memories: List[str] = None) -> str:
        """添加反思记忆（高阶洞察）"""
        memory_id = hashlib.md5(f"reflection{content}{time.time()}".encode()).hexdigest()[:12]
        
        memory = MemoryRecord(
            id=memory_id,
            content=content,
            memory_type="reflection",
            importance=importance,
            timestamp=datetime.now(),
            source="reflection",
            related_memories=related_memories or []
        )
        
        self.memories.append(memory)
        return memory_id
        
    def add_plan(self, content: str, plan_type: str = "hourly", 
                importance: float = 0.7) -> str:
        """
        添加计划记忆
        
        Args:
            content: 计划内容
            plan_type: daily/hourly/action
            importance: 重要性
        """
        memory_id = hashlib.md5(f"plan{content}{time.time()}".encode()).hexdigest()[:12]
        
        memory = MemoryRecord(
            id=memory_id,
            content=content,
            memory_type="plan",
            importance=importance,
            timestamp=datetime.now(),
            source="planning"
        )
        
        self.memories.append(memory)
        return memory_id
        
    def retrieve(self, query: str, context: Dict = None, top_k: int = 5) -> List[MemoryRecord]:
        """
        检索相关记忆
        
        评分公式（来自Generative Agents论文）：
        score = relevance * recency * importance
        
        Args:
            query: 查询内容
            context: 当前上下文（时间、位置等）
            top_k: 返回数量
        """
        if not self.memories:
            return []
            
        scored = []
        query_lower = query.lower()
        now = datetime.now()
        
        for memory in self.memories:
            # 1. 相关性分数（简化版：关键词匹配）
            relevance = self._calculate_relevance(query_lower, memory)
            
            # 2. 时效性分数（越新越高）
            hours_ago = (now - memory.timestamp).total_seconds() / 3600
            recency = math.exp(-hours_ago / 24)  # 24小时衰减
            
            # 3. 重要性分数
            importance = memory.importance
            
            # 综合分数
            score = relevance * recency * importance
            
            scored.append((score, memory))
            
            # 更新访问统计
            memory.access_count += 1
            memory.last_access = now
            
        # 排序并返回top_k
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:top_k]]
        
    def _calculate_relevance(self, query_lower: str, memory: MemoryRecord) -> float:
        """计算相关性分数（简化版）"""
        content_lower = memory.content.lower()
        
        # 关键词匹配
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        
        if not query_words:
            return 0.5
            
        # Jaccard相似度
        intersection = query_words & content_words
        union = query_words | content_words
        
        return len(intersection) / len(union) if union else 0.5
        
    def _trigger_reflection(self):
        """触发反思（当记忆积累到一定数量时）"""
        # 获取需要反思的记忆
        recent_memories = self.memories[self.last_reflection_idx:]
        self.last_reflection_idx = len(self.memories)
        
        print(f"🤔 [{self.agent_id}] 触发反思：{len(recent_memories)} 条新记忆")
        
        # 返回需要反思的内容（由LLMBrain处理具体反思生成）
        return recent_memories
        
    def get_recent_observations(self, hours: int = 24) -> List[MemoryRecord]:
        """获取最近N小时的观察"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.memories 
                if m.memory_type == "observation" and m.timestamp > cutoff]
        
    def get_reflections(self) -> List[MemoryRecord]:
        """获取所有反思"""
        return [m for m in self.memories if m.memory_type == "reflection"]
        
    def get_current_plan(self) -> Optional[Dict]:
        """获取当前计划"""
        return self.current_plan
        
    def set_current_plan(self, plan: Dict):
        """设置当前计划"""
        self.current_plan = plan
        
    def get_summary(self) -> str:
        """获取记忆摘要"""
        total = len(self.memories)
        observations = len([m for m in self.memories if m.memory_type == "observation"])
        reflections = len([m for m in self.memories if m.memory_type == "reflection"])
        plans = len([m for m in self.memories if m.memory_type == "plan"])
        
        return f"记忆统计: 总计{total}条 (观察{observations}/反思{reflections}/计划{plans})"


class ReflectionEngine:
    """
    反思引擎
    
    定期分析记忆流，生成高阶洞察
    """
    
    def __init__(self, memory_stream: MemoryStream):
        self.memory_stream = memory_stream
        
    def generate_reflection(self, recent_memories: List[MemoryRecord]) -> Optional[str]:
        """
        基于近期记忆生成反思
        
        返回反思内容的自然语言描述
        """
        if len(recent_memories) < 10:
            return None
            
        # 提取主题（简化版：高频词）
        themes = self._extract_themes(recent_memories)
        
        # 生成反思内容
        reflection_content = f"最近我主要在做：{', '.join(themes[:3])}。"
        
        return reflection_content
        
    def _extract_themes(self, memories: List[MemoryRecord]) -> List[str]:
        """提取主题（简化版实现）"""
        # 统计关键词频率
        word_freq = {}
        for m in memories:
            words = m.content.lower().split()
            for w in words:
                if len(w) > 2:  # 忽略短词
                    word_freq[w] = word_freq.get(w, 0) + 1
                    
        # 返回高频词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:10]]


class PlanningEngine:
    """
    规划引擎
    
    生成日计划和小时计划
    """
    
    def __init__(self, memory_stream: MemoryStream):
        self.memory_stream = memory_stream
        
    def generate_daily_plan(self, agent_state: Dict, world_context: Dict) -> Dict:
        """
        生成日计划
        
        Args:
            agent_state: AI当前状态
            world_context: 世界上下文
            
        Returns:
            日计划结构
        """
        # 获取相关记忆
        relevant = self.memory_stream.retrieve("今天的计划", top_k=10)
        
        # 生成计划（简化版）
        plan = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "overview": "探索世界，收集资源，与其他AI互动",
            "goals": [
                "收集基础资源（木头、石头）",
                "探索周围环境",
                "建立初步庇护所"
            ],
            "hourly_schedule": [
                {"hour": 6, "activity": "起床，检查周围环境"},
                {"hour": 7, "activity": "收集木头"},
                {"hour": 8, "activity": "收集石头"},
                {"hour": 9, "activity": "探索"},
                {"hour": 12, "activity": "休息，进食"},
                {"hour": 13, "activity": "继续探索"},
                {"hour": 18, "activity": "返回基地"},
                {"hour": 20, "activity": "整理资源"},
                {"hour": 22, "activity": "休息"},
            ]
        }
        
        return plan
        
    def get_current_hour_activity(self, daily_plan: Dict) -> str:
        """获取当前小时的计划活动"""
        current_hour = datetime.now().hour
        
        for item in daily_plan.get("hourly_schedule", []):
            if item["hour"] == current_hour:
                return item["activity"]
                
        return "自由探索"
