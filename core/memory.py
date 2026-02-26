"""
Memory System - 记忆系统
"""

from datetime import datetime
from typing import List, Dict, Optional


class Memory:
    """单条记忆"""
    
    def __init__(self, content: str, memory_type: str = "event", importance: float = 1.0):
        self.content = content
        self.type = memory_type  # event, skill, preference, social
        self.importance = importance
        self.created_at = datetime.now()
        self.access_count = 0
        
    def access(self):
        """被访问时更新"""
        self.access_count += 1


class MemorySystem:
    """
    AI分身记忆系统
    
    管理：
    - 短期记忆（当前会话）
    - 长期记忆（持久化存储）
    - 用户偏好学习
    """
    
    def __init__(self):
        self.short_term: List[Memory] = []
        self.long_term: List[Memory] = []
        self.preferences: Dict[str, any] = {}
        
    def add(self, content: str, memory_type: str = "event", importance: float = 1.0):
        """添加新记忆"""
        memory = Memory(content, memory_type, importance)
        self.short_term.append(memory)
        
        # 重要记忆存入长期记忆
        if importance >= 0.8:
            self.long_term.append(memory)
    
    def search(self, query: str, limit: int = 10) -> List[Memory]:
        """搜索相关记忆"""
        # TODO: 实现向量检索
        return self.short_term[-limit:]
    
    def get_preferences(self) -> Dict:
        """获取学习到的用户偏好"""
        return self.preferences
    
    def learn_preference(self, key: str, value: any, confidence: float = 1.0):
        """学习用户偏好"""
        self.preferences[key] = {
            "value": value,
            "confidence": confidence,
            "learned_at": datetime.now()
        }
