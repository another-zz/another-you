"""
Auto Curriculum - 自动课程系统
AI自主决定学习目标
"""

import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto

class Difficulty(Enum):
    """难度等级"""
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

@dataclass
class Task:
    """学习任务"""
    name: str
    description: str
    difficulty: Difficulty
    prerequisites: List[str]
    verification: str  # 如何验证完成
    completed: bool = False
    attempts: int = 0

class AutoCurriculum:
    """自动课程生成器"""
    
    # 预设任务模板
    TASK_TEMPLATES = [
        {
            "name": "收集木材",
            "description": "找到树木并收集10个原木",
            "difficulty": Difficulty.EASY,
            "prerequisites": [],
            "verification": "背包中有10+原木",
        },
        {
            "name": "制作工作台",
            "description": "用4个木板制作一个工作台",
            "difficulty": Difficulty.EASY,
            "prerequisites": ["收集木材"],
            "verification": "背包中有工作台",
        },
        {
            "name": "建造庇护所",
            "description": "建造一个3x3的封闭空间作为家",
            "difficulty": Difficulty.MEDIUM,
            "prerequisites": ["收集木材", "制作工作台"],
            "verification": "有封闭空间+床",
        },
        {
            "name": "挖矿获取石头",
            "description": "挖到20个圆石",
            "difficulty": Difficulty.MEDIUM,
            "prerequisites": ["制作工作台"],
            "verification": "背包中有20+圆石",
        },
        {
            "name": "制作石制工具",
            "description": "制作石剑、石镐、石斧",
            "difficulty": Difficulty.MEDIUM,
            "prerequisites": ["挖矿获取石头", "制作工作台"],
            "verification": "背包中有石剑+石镐+石斧",
        },
        {
            "name": "找到食物来源",
            "description": "找到动物或种植小麦",
            "difficulty": Difficulty.MEDIUM,
            "prerequisites": [],
            "verification": "有稳定食物来源",
        },
        {
            "name": "建造农场",
            "description": "建造一个9x9的农田",
            "difficulty": Difficulty.HARD,
            "prerequisites": ["找到食物来源", "制作石制工具"],
            "verification": "农田中有作物生长",
        },
        {
            "name": "探索洞穴",
            "description": "深入地下找到铁矿",
            "difficulty": Difficulty.HARD,
            "prerequisites": ["制作石制工具", "建造庇护所"],
            "verification": "背包中有铁矿石",
        },
    ]
    
    def __init__(self):
        self.completed_tasks: List[str] = []
        self.current_task: Optional[Task] = None
        self.task_history: List[Task] = []
        
    def generate_next_task(self, current_inventory: Dict, skills_learned: List[str]) -> Optional[Task]:
        """生成下一个学习任务"""
        
        # 检查当前任务是否完成
        if self.current_task and not self.current_task.completed:
            return self.current_task
            
        # 找到所有可选任务（前置条件满足）
        available = []
        for template in self.TASK_TEMPLATES:
            if template["name"] in self.completed_tasks:
                continue
                
            # 检查前置条件
            prereqs_satisfied = all(
                p in self.completed_tasks or p in skills_learned
                for p in template["prerequisites"]
            )
            
            if prereqs_satisfied:
                available.append(template)
                
        if not available:
            return None
            
        # 优先选择简单任务
        easy_tasks = [t for t in available if t["difficulty"] == Difficulty.EASY]
        if easy_tasks:
            chosen = random.choice(easy_tasks)
        else:
            chosen = random.choice(available)
            
        # 创建任务实例
        task = Task(
            name=chosen["name"],
            description=chosen["description"],
            difficulty=chosen["difficulty"],
            prerequisites=chosen["prerequisites"],
            verification=chosen["verification"],
        )
        
        self.current_task = task
        self.task_history.append(task)
        
        return task
        
    def complete_current_task(self, success: bool = True):
        """完成当前任务"""
        if self.current_task:
            self.current_task.completed = success
            if success:
                self.completed_tasks.append(self.current_task.name)
            self.current_task = None
            
    def get_progress(self) -> Dict:
        """获取学习进度"""
        total = len(self.TASK_TEMPLATES)
        completed = len(self.completed_tasks)
        return {
            "completed": completed,
            "total": total,
            "percentage": (completed / total * 100) if total > 0 else 0,
            "current_task": self.current_task.name if self.current_task else None,
        }
