"""
Skill Library - AI技能库系统（参考Voyager）
可复用、可组合、可扩展
"""

import json
import os
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Skill:
    """技能定义"""
    name: str
    description: str
    code: str
    embedding: List[float]  # 用于语义检索
    usage_count: int = 0
    success_rate: float = 1.0
    created_at: str = ""
    
    def get_key(self) -> str:
        """生成唯一key"""
        return hashlib.md5(self.name.encode()).hexdigest()[:12]

class SkillLibrary:
    """技能库 - AI终身学习存储"""
    
    def __init__(self, library_dir: str = "data/skills"):
        self.library_dir = library_dir
        os.makedirs(library_dir, exist_ok=True)
        self.skills: Dict[str, Skill] = {}
        self._load_all()
        
    def _load_all(self):
        """加载所有技能"""
        if not os.path.exists(self.library_dir):
            return
            
        for filename in os.listdir(self.library_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.library_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    skill = Skill(**data)
                    self.skills[skill.get_key()] = skill
                    
    def save_skill(self, skill: Skill) -> str:
        """保存技能"""
        key = skill.get_key()
        self.skills[key] = skill
        
        filepath = os.path.join(self.library_dir, f"{key}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(skill), f, indent=2, ensure_ascii=False)
            
        return key
        
    def retrieve_skill(self, query: str, top_k: int = 3) -> List[Skill]:
        """检索相关技能（简化版：关键词匹配）"""
        query_lower = query.lower()
        scored = []
        
        for skill in self.skills.values():
            score = 0
            if query_lower in skill.name.lower():
                score += 10
            if query_lower in skill.description.lower():
                score += 5
            # 成功率加权
            score += skill.success_rate * 2
            # 使用次数加权
            score += min(skill.usage_count, 10)
            
            if score > 0:
                scored.append((score, skill))
                
        # 排序返回top_k
        scored.sort(reverse=True, key=lambda x: x[0])
        return [s[1] for s in scored[:top_k]]
        
    def update_success(self, skill_key: str, success: bool):
        """更新技能成功率"""
        if skill_key not in self.skills:
            return
            
        skill = self.skills[skill_key]
        skill.usage_count += 1
        
        # 指数移动平均更新成功率
        alpha = 0.3
        if success:
            skill.success_rate = skill.success_rate * (1 - alpha) + 1.0 * alpha
        else:
            skill.success_rate = skill.success_rate * (1 - alpha) + 0.0 * alpha
            
        self.save_skill(skill)
        
    def list_all(self) -> List[Skill]:
        """列出所有技能"""
        return list(self.skills.values())
        
    def get_skill_code(self, skill_key: str) -> Optional[str]:
        """获取技能代码"""
        if skill_key in self.skills:
            return self.skills[skill_key].code
        return None
