"""
Vector Memory - 向量记忆系统
使用ChromaDB实现长期语义记忆
"""

import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime

class VectorMemory:
    """
    向量记忆系统
    支持语义检索的长期记忆
    """
    
    def __init__(self, agent_id: str, memory_dir: str = "data/memories"):
        self.agent_id = agent_id
        self.memory_dir = memory_dir
        self.memories: List[Dict] = []
        
        # 确保目录存在
        os.makedirs(memory_dir, exist_ok=True)
        
        # 加载已有记忆
        self._load()
        
    def _load(self):
        """加载记忆"""
        filepath = os.path.join(self.memory_dir, f"{self.agent_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.memories = json.load(f)
                print(f"💾 加载了 {len(self.memories)} 条记忆")
                
    def save(self):
        """保存记忆"""
        filepath = os.path.join(self.memory_dir, f"{self.agent_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)
            
    def add(self, content: str, memory_type: str = "event", importance: float = 0.5):
        """
        添加记忆
        
        Args:
            content: 记忆内容
            memory_type: 类型 (event, skill, location, social)
            importance: 重要性 (0-1)
        """
        memory = {
            "id": hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:12],
            "content": content,
            "type": memory_type,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        
        self.memories.append(memory)
        
        # 自动保存
        if len(self.memories) % 10 == 0:
            self.save()
            
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """
        检索相关记忆
        
        简化版：使用关键词匹配
        实际部署时使用ChromaDB向量检索
        """
        query_lower = query.lower()
        scored = []
        
        for memory in self.memories:
            score = 0
            content = memory["content"].lower()
            
            # 关键词匹配
            query_words = query_lower.split()
            for word in query_words:
                if word in content:
                    score += 10
                    
            # 重要性加权
            score += memory["importance"] * 20
            
            # 时间衰减（越新的记忆分越高）
            try:
                mem_time = datetime.fromisoformat(memory["timestamp"])
                days_ago = (datetime.now() - mem_time).days
                score += max(0, 30 - days_ago)  # 30天内的新记忆加分
            except:
                pass
                
            if score > 0:
                scored.append((score, memory))
                memory["access_count"] += 1
                
        # 排序并返回
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m["content"] for _, m in scored[:top_k]]
        
    def get_recent(self, n: int = 10) -> List[str]:
        """获取最近记忆"""
        recent = sorted(self.memories, 
                       key=lambda x: x["timestamp"], 
                       reverse=True)[:n]
        return [m["content"] for m in recent]
        
    def get_important(self, min_importance: float = 0.7) -> List[str]:
        """获取重要记忆"""
        important = [m for m in self.memories 
                    if m["importance"] >= min_importance]
        return [m["content"] for m in important]
        
    def consolidate(self):
        """
        记忆整合
        压缩冗余记忆，提取重要信息
        """
        if len(self.memories) < 50:
            return
            
        # 保留重要记忆
        important = [m for m in self.memories if m["importance"] >= 0.6]
        
        # 保留最近记忆
        recent = sorted(self.memories, 
                       key=lambda x: x["timestamp"],
                       reverse=True)[:30]
        
        # 合并去重
        seen_ids = set()
        consolidated = []
        for m in important + recent:
            if m["id"] not in seen_ids:
                consolidated.append(m)
                seen_ids.add(m["id"])
                
        self.memories = consolidated
        self.save()
        
        print(f"🧹 记忆整合完成: {len(self.memories)} 条")


import time
