"""
AnotherYou v0.4 - 持久化 AI 社会
核心：真正的 AI 自主推动世界发展
"""

import pygame
import sys
import random
import json
import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# 初始化
pygame.init()

# 常量
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60
TILE_SIZE = 32

# 颜色主题
COLORS = {
    "grass": (34, 139, 34),
    "forest": (0, 100, 0),
    "water": (65, 105, 225),
    "sand": (238, 214, 175),
    "mountain": (139, 137, 137),
    
    "tree": (101, 67, 33),
    "rock": (128, 128, 128),
    "berry": (220, 20, 60),
    "herb": (50, 205, 50),
    "gold_ore": (255, 215, 0),
    
    "player": (255, 100, 100),
    "ai": (100, 150, 255),
    "ai_friend": (100, 255, 150),
    "ai_enemy": (255, 100, 100),
    
    "house": (180, 140, 100),
    "shop": (255, 200, 100),
    "farm": (154, 205, 50),
    "mine": (105, 105, 105),
    
    "ui_bg": (25, 25, 35),
    "ui_panel": (35, 35, 50),
    "ui_text": (255, 255, 255),
    "ui_gold": (255, 215, 0),
    "ui_green": (100, 255, 100),
    "ui_red": (255, 100, 100),
    "ui_blue": (100, 150, 255),
}


class RelationshipType(Enum):
    STRANGER = "stranger"
    FRIEND = "friend"
    ENEMY = "enemy"
    FAMILY = "family"
    BUSINESS = "business"


@dataclass
class Memory:
    """记忆条目"""
    timestamp: str
    content: str
    importance: float  # 0-10
    memory_type: str  # observation, reflection, conversation
    related_agents: List[str]
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Skill:
    """技能"""
    name: str
    description: str
    level: int = 1
    experience: int = 0
    max_level: int = 10
    
    def gain_exp(self, amount: int):
        self.experience += amount
        if self.experience >= self.level * 100:
            self.experience = 0
            if self.level < self.max_level:
                self.level += 1
                return True
        return False


class PersistentWorld:
    """持久化世界 - SQLite 存储"""
    
    def __init__(self, db_path: str = "data/world.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        
        self.width = 60
        self.height = 50
        self.day = 1
        self.hour = 6
        self.time_speed = 60  # 秒/游戏小时
        self.last_update = datetime.now()
        
        # 加载或生成世界
        self._load_or_init_world()
    
    def _init_db(self):
        """初始化数据库表"""
        c = self.conn.cursor()
        
        # 世界状态表
        c.execute('''CREATE TABLE IF NOT EXISTS world_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        
        # 地形表
        c.execute('''CREATE TABLE IF NOT EXISTS tiles (
            x INTEGER,
            y INTEGER,
            tile_type TEXT,
            PRIMARY KEY (x, y)
        )''')
        
        # 资源表
        c.execute('''CREATE TABLE IF NOT EXISTS resources (
            id TEXT PRIMARY KEY,
            type TEXT,
            x INTEGER,
            y INTEGER,
            amount INTEGER,
            max_amount INTEGER
        )''')
        
        # 建筑表
        c.execute('''CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            type TEXT,
            x INTEGER,
            y INTEGER,
            owner_id TEXT,
            level INTEGER,
            data TEXT
        )''')
        
        # AI Agent 表
        c.execute('''CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT,
            x INTEGER,
            y INTEGER,
            energy REAL,
            max_energy REAL,
            gold INTEGER,
            inventory TEXT,
            skills TEXT,
            personality TEXT,
            current_goal TEXT,
            state TEXT
        )''')
        
        # 记忆表
        c.execute('''CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            timestamp TEXT,
            content TEXT,
            importance REAL,
            memory_type TEXT,
            related_agents TEXT
        )''')
        
        # 关系表
        c.execute('''CREATE TABLE IF NOT EXISTS relationships (
            agent1_id TEXT,
            agent2_id TEXT,
            relationship_type TEXT,
            affinity REAL,
            last_interaction TEXT,
            PRIMARY KEY (agent1_id, agent2_id)
        )''')
        
        # 交易记录表
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            buyer_id TEXT,
            seller_id TEXT,
            item_type TEXT,
            quantity INTEGER,
            price INTEGER
        )''')
        
        # 事件日志表
        c.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            day INTEGER,
            hour INTEGER,
            event_type TEXT,
            description TEXT,
            related_agent TEXT
        )''')
        
        self.conn.commit()
    
    def _load_or_init_world(self):
        """加载或初始化世界"""
        c = self.conn.cursor()
        
        # 检查是否有现有世界
        c.execute("SELECT value FROM world_state WHERE key = 'initialized'")
        if c.fetchone():
            self._load_world()
        else:
            self._generate_new_world()
    
    def _load_world(self):
        """从数据库加载世界"""
        c = self.conn.cursor()
        
        # 加载世界状态
        c.execute("SELECT key, value FROM world_state")
        for key, value in c.fetchall():
            if key == 'day':
                self.day = int(value)
            elif key == 'hour':
                self.hour = int(value)
        
        print(f"🌍 加载世界: Day {self.day} {self.hour:02d}:00")
    
    def _generate_new_world(self):
        """生成新世界"""
        print("🌍 生成新世界...")
        
        # 生成地形
        self._generate_terrain()
        
        # 生成资源
        self._spawn_resources()
        
        # 标记已初始化
        c = self.conn.cursor()
        c.execute("INSERT INTO world_state VALUES ('initialized', 'true')")
        c.execute("INSERT INTO world_state VALUES ('day', '1')")
        c.execute("INSERT INTO world_state VALUES ('hour', '6')")
        self.conn.commit()
    
    def _generate_terrain(self):
        """生成地形"""
        c = self.conn.cursor()
        
        for x in range(self.width):
            for y in range(self.height):
                # 边缘是水
                if x < 3 or x >= self.width - 3 or y < 3 or y >= self.height - 3:
                    tile_type = "water"
                else:
                    noise = random.random()
                    if noise < 0.1:
                        tile_type = "water"
                    elif noise < 0.2:
                        tile_type = "sand"
                    elif noise < 0.35:
                        tile_type = "forest"
                    elif noise < 0.4:
                        tile_type = "mountain"
                    else:
                        tile_type = "grass"
                
                c.execute("INSERT OR REPLACE INTO tiles VALUES (?, ?, ?)",
                         (x, y, tile_type))
        
        self.conn.commit()
    
    def _spawn_resources(self):
        """生成资源"""
        c = self.conn.cursor()
        
        resource_types = [
            ("tree", 0.25, 5, 10),
            ("rock", 0.15, 3, 8),
            ("berry", 0.1, 2, 6),
            ("herb", 0.08, 1, 4),
            ("gold_ore", 0.03, 1, 3),
        ]
        
        for res_type, density, min_amt, max_amt in resource_types:
            count = int(self.width * self.height * density * 0.1)
            for i in range(count):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                
                # 检查地形
                c.execute("SELECT tile_type FROM tiles WHERE x=? AND y=?", (x, y))
                result = c.fetchone()
                if result and result[0] in ["grass", "forest", "mountain"]:
                    res_id = f"{res_type}_{x}_{y}"
                    c.execute('''INSERT OR REPLACE INTO resources 
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             (res_id, res_type, x, y, 
                              random.randint(min_amt, max_amt), max_amt))
        
        self.conn.commit()
    
    def update(self):
        """更新世界时间"""
        now = datetime.now()
        elapsed = (now - self.last_update).total_seconds()
        
        if elapsed >= self.time_speed:
            self.hour += 1
            self.last_update = now
            
            if self.hour >= 24:
                self.hour = 0
                self.day += 1
                self._daily_refresh()
            
            # 保存状态
            self._save_state()
    
    def _daily_refresh(self):
        """每日刷新"""
        c = self.conn.cursor()
        
        # 资源再生
        c.execute("SELECT id, amount, max_amount FROM resources")
        for res_id, amount, max_amount in c.fetchall():
            if amount < max_amount:
                new_amount = min(max_amount, amount + random.randint(1, 3))
                c.execute("UPDATE resources SET amount=? WHERE id=?",
                         (new_amount, res_id))
        
        # 生成新资源
        self._spawn_daily_resources()
        
        self.conn.commit()
        self.log_event("daily_refresh", f"Day {self.day} 开始")
    
    def _spawn_daily_resources(self):
        """每日生成新资源"""
        c = self.conn.cursor()
        
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            c.execute("SELECT tile_type FROM tiles WHERE x=? AND y=?", (x, y))
            result = c.fetchone()
            if result and result[0] in ["grass", "forest"]:
                res_type = random.choice(["tree", "rock", "berry", "herb"])
                res_id = f"{res_type}_{x}_{y}_{self.day}"
                
                # 检查是否已有资源
                c.execute("SELECT 1 FROM resources WHERE x=? AND y=?", (x, y))
                if not c.fetchone():
                    c.execute('''INSERT INTO resources VALUES (?, ?, ?, ?, ?, ?)''',
                             (res_id, res_type, x, y, random.randint(2, 5), 5))
        
        self.conn.commit()
    
    def _save_state(self):
        """保存世界状态"""
        c = self.conn.cursor()
        c.execute("UPDATE world_state SET value=? WHERE key='day'", (str(self.day),))
        c.execute("UPDATE world_state SET value=? WHERE key='hour'", (str(self.hour),))
        self.conn.commit()
    
    def log_event(self, event_type: str, description: str, agent_id: str = None):
        """记录事件"""
        c = self.conn.cursor()
        c.execute('''INSERT INTO events (timestamp, day, hour, event_type, description, related_agent)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                 (datetime.now().isoformat(), self.day, self.hour, 
                  event_type, description, agent_id))
        self.conn.commit()
    
    def get_tile(self, x: int, y: int) -> str:
        """获取地形类型"""
        if 0 <= x < self.width and 0 <= y < self.height:
            c = self.conn.cursor()
            c.execute("SELECT tile_type FROM tiles WHERE x=? AND y=?", (x, y))
            result = c.fetchone()
            return result[0] if result else "grass"
        return "void"
    
    def is_walkable(self, x: int, y: int) -> bool:
        """检查是否可行走"""
        tile = self.get_tile(x, y)
        return tile not in ["water", "void", "mountain"]
    
    def get_resource_at(self, x: int, y: int) -> Optional[Dict]:
        """获取指定位置的资源"""
        c = self.conn.cursor()
        c.execute("SELECT * FROM resources WHERE x=? AND y=? AND amount > 0", (x, y))
        result = c.fetchone()
        if result:
            return {
                "id": result[0],
                "type": result[1],
                "x": result[2],
                "y": result[3],
                "amount": result[4],
                "max_amount": result[5]
            }
        return None
    
    def gather_resource(self, x: int, y: int) -> Tuple[bool, str, Optional[str]]:
        """采集资源"""
        resource = self.get_resource_at(x, y)
        if not resource:
            return False, "这里没有可采集的资源", None
        
        c = self.conn.cursor()
        new_amount = resource["amount"] - 1
        c.execute("UPDATE resources SET amount=? WHERE id=?",
                 (new_amount, resource["id"]))
        self.conn.commit()
        
        if new_amount <= 0:
            self.log_event("resource_depleted", f"{resource['type']} 被采集殆尽")
        
        return True, f"采集了 {resource['type']}", resource["type"]
    
    def get_nearby_resources(self, x: int, y: int, radius: int = 5) -> List[Dict]:
        """获取附近资源"""
        c = self.conn.cursor()
        c.execute('''SELECT * FROM resources 
                     WHERE x BETWEEN ? AND ? AND y BETWEEN ? AND ? AND amount > 0''',
                 (x - radius, x + radius, y - radius, y + radius))
        
        resources = []
        for row in c.fetchall():
            resources.append({
                "id": row[0],
                "type": row[1],
                "x": row[2],
                "y": row[3],
                "amount": row[4],
                "distance": abs(row[2] - x) + abs(row[3] - y)
            })
        
        return sorted(resources, key=lambda r: r["distance"])
    
    def create_building(self, x: int, y: int, building_type: str, owner_id: str) -> Tuple[bool, str]:
        """创建建筑"""
        if not self.is_walkable(x, y):
            return False, "无法在这里建造"
        
        c = self.conn.cursor()
        
        # 检查是否已有建筑
        c.execute("SELECT 1 FROM buildings WHERE x=? AND y=?", (x, y))
        if c.fetchone():
            return False, "这里已经有建筑了"
        
        building_id = f"{building_type}_{x}_{y}"
        c.execute('''INSERT INTO buildings VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (building_id, building_type, x, y, owner_id, 1, "{}"))
        self.conn.commit()
        
        self.log_event("building_created", f"{owner_id} 建造了 {building_type}", owner_id)
        return True, f"成功建造 {building_type}"
    
    def get_buildings(self) -> List[Dict]:
        """获取所有建筑"""
        c = self.conn.cursor()
        c.execute("SELECT * FROM buildings")
        
        buildings = []
        for row in c.fetchall():
            buildings.append({
                "id": row[0],
                "type": row[1],
                "x": row[2],
                "y": row[3],
                "owner_id": row[4],
                "level": row[5],
                "data": json.loads(row[6])
            })
        
        return buildings
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()


class SocialAgent:
    """社交 AI Agent - 拥有记忆、技能、关系"""
    
    def __init__(self, agent_id: str, name: str, x: int, y: int, world: PersistentWorld):
        self.agent_id = agent_id
        self.name = name
        self.x = x
        self.y = y
        self.world = world
        
        # 基础属性
        self.energy = 100.0
        self.max_energy = 100.0
        self.gold = random.randint(50, 150)
        self.inventory = {}
        
        # 个性
        self.personality = {
            "openness": random.random(),
            "conscientiousness": random.random(),
            "extraversion": random.random(),
            "agreeableness": random.random(),
            "neuroticism": random.random(),
        }
        
        # 技能和记忆
        self.skills: Dict[str, Skill] = {}
        self.memories: List[Memory] = []
        
        # 当前状态
        self.current_goal = "explore"
        self.state = "idle"
        self.action_timer = 0
        self.plan = []
        
        # 消息队列
        self.messages = []
        
        # 统计
        self.total_gathered = 0
        self.total_traded = 0
        self.relationships = {}
        
        # 从数据库加载或创建
        self._load_or_create()
    
    def _load_or_create(self):
        """从数据库加载或创建新 Agent"""
        c = self.world.conn.cursor()
        c.execute("SELECT * FROM agents WHERE id=?", (self.agent_id,))
        result = c.fetchone()
        
        if result:
            # 加载现有数据
            self.x = result[2]
            self.y = result[3]
            self.energy = result[4]
            self.max_energy = result[5]
            self.gold = result[6]
            self.inventory = json.loads(result[7])
            self.skills = {k: Skill(**v) for k, v in json.loads(result[8]).items()}
            self.personality = json.loads(result[9])
            self.current_goal = result[10]
            self.state = result[11]
            
            # 加载记忆
            c.execute("SELECT * FROM memories WHERE agent_id=? ORDER BY timestamp DESC LIMIT 50",
                     (self.agent_id,))
            for row in c.fetchall():
                self.memories.append(Memory(
                    timestamp=row[2],
                    content=row[3],
                    importance=row[4],
                    memory_type=row[5],
                    related_agents=json.loads(row[6])
                ))
            
            # 加载关系
            c.execute("SELECT * FROM relationships WHERE agent1_id=?", (self.agent_id,))
            for row in c.fetchall():
                self.relationships[row[1]] = {
                    "type": row[2],
                    "affinity": row[3],
                    "last_interaction": row[4]
                }
        else:
            # 创建新 Agent
            self._save_to_db()
    
    def _save_to_db(self):
        """保存到数据库"""
        c = self.world.conn.cursor()
        c.execute('''INSERT OR REPLACE INTO agents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (self.agent_id, self.name, self.x, self.y, self.energy, self.max_energy,
                  self.gold, json.dumps(self.inventory),
                  json.dumps({k: asdict(v) for k, v in self.skills.items()}),
                  json.dumps(self.personality), self.current_goal, self.state))
        self.world.conn.commit()
    
    def add_memory(self, content: str, importance: float, memory_type: str, 
                   related_agents: List[str] = None):
        """添加记忆"""
        memory = Memory(
            timestamp=datetime.now().isoformat(),
            content=content,
            importance=importance,
            memory_type=memory_type,
            related_agents=related_agents or []
        )
        self.memories.append(memory)
        
        # 保存到数据库
        c = self.world.conn.cursor()
        c.execute('''INSERT INTO memories (agent_id, timestamp, content, importance, 
                     memory_type, related_agents) VALUES (?, ?, ?, ?, ?, ?)''',
                 (self.agent_id, memory.timestamp, memory.content, memory.importance,
                  memory.memory_type, json.dumps(memory.related_agents)))
        self.world.conn.commit()
        
        # 限制记忆数量
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
    
    def get_important_memories(self, limit: int = 5) -> List[Memory]:
        """获取重要记忆"""
        return sorted(self.memories, key=lambda m: m.importance, reverse=True)[:limit]
    
    def learn_skill(self, skill_name: str, description: str) -> bool:
        """学习新技能"""
        if skill_name not in self.skills:
            self.skills[skill_name] = Skill(name=skill_name, description=description)
            self.add_memory(f"学会了新技能: {skill_name}", 8.0, "skill_learning")
            self.messages.append(f"🎓 学会了 {skill_name}!")
            self._save_to_db()
            return True
        return False
    
    def update_relationship(self, other_agent_id: str, interaction_type: str, 
                           affinity_delta: float):
        """更新关系"""
        if other_agent_id not in self.relationships:
            self.relationships[other_agent_id] = {
                "type": RelationshipType.STRANGER.value,
                "affinity": 0.0,
                "last_interaction": datetime.now().isoformat()
            }
        
        rel = self.relationships[other_agent_id]
        rel["affinity"] = max(-1.0, min(1.0, rel["affinity"] + affinity_delta))
        rel["last_interaction"] = datetime.now().isoformat()
        
        # 根据亲密度更新关系类型
        if rel["affinity"] > 0.7:
            rel["type"] = RelationshipType.FRIEND.value
        elif rel["affinity"] < -0.5:
            rel["type"] = RelationshipType.ENEMY.value
        
        # 保存到数据库
        c = self.world.conn.cursor()
        c.execute('''INSERT OR REPLACE INTO relationships VALUES (?, ?, ?, ?, ?)''',
                 (self.agent_id, other_agent_id, rel["type"], rel["affinity"], 
                  rel["last_interaction"]))
        self.world.conn.commit()
    
    def think(self) -> str:
        """AI 思考 - 生成反思"""
        # 简单的基于规则的思考
        thoughts = []
        
        # 基于能量状态
        if self.energy < 30:
            thoughts.append("我很累，需要休息")
        
        # 基于库存
        if sum(self.inventory.values()) > 20:
            thoughts.append("我的背包快满了，应该去交易")
        
        # 基于金币
        if self.gold < 20:
            thoughts.append("我需要赚更多钱")
        
        # 基于技能
        if len(self.skills) < 2:
            thoughts.append("我应该学习新技能")
        
        # 随机反思
        if random.random() < 0.3:
            reflections = [
                f"我已经采集了 {self.total_gathered} 个资源",
                "这个世界很大，有很多东西可以探索",
                "和其他 AI 交流很有趣",
                "我需要制定长期计划",
            ]
            thoughts.append(random.choice(reflections))
        
        if thoughts:
            thought = random.choice(thoughts)
            self.add_memory(thought, 5.0, "reflection")
            return thought
        
        return ""
    
    def plan_actions(self):
        """规划行动"""
        self.plan = []
        
        # 优先级 1: 生存需求
        if self.energy < 20:
            self.plan.append({"action": "rest", "reason": "恢复体力"})
            return
        
        # 优先级 2: 资源采集
        if self.inventory.get("wood", 0) < 5:
            nearby = self.world.get_nearby_resources(self.x, self.y)
            trees = [r for r in nearby if r["type"] == "tree"]
            if trees:
                self.plan.append({"action": "move_to", "target": (trees[0]["x"], trees[0]["y"]), 
                               "reason": "去采集木材"})
                self.plan.append({"action": "gather", "reason": "采集木材"})
                return
        
        # 优先级 3: 探索
        if random.random() < 0.6:
            self.plan.append({"action": "explore", "reason": "探索世界"})
            return
        
        # 优先级 4: 社交
        if random.random() < 0.3:
            self.plan.append({"action": "socialize", "reason": "寻找其他 AI 交流"})
            return
        
        # 默认: 休息
        self.plan.append({"action": "rest", "reason": "休息恢复"})
    
    def execute_action(self):
        """执行计划中的行动"""
        if not self.plan:
            self.plan_actions()
        
        if not self.plan:
            return
        
        action = self.plan.pop(0)
        action_type = action["action"]
        
        if action_type == "rest":
            self.energy = min(self.max_energy, self.energy + 15)
            self.add_memory("休息恢复体力", 3.0, "action")
        
        elif action_type == "move_to":
            tx, ty = action["target"]
            dx = max(-1, min(1, tx - self.x))
            dy = max(-1, min(1, ty - self.y))
            
            if self.world.is_walkable(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                self.energy -= 0.5
        
        elif action_type == "gather":
            success, msg, res_type = self.world.gather_resource(self.x, self.y)
            if success:
                self.inventory[res_type] = self.inventory.get(res_type, 0) + 1
                self.energy -= 5
                self.total_gathered += 1
                self.add_memory(f"采集了 {res_type}", 4.0, "action")
                
                # 学习技能
                if res_type == "wood" and self.inventory["wood"] >= 5:
                    self.learn_skill("伐木", "更高效地采集木材")
        
        elif action_type == "explore":
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            if self.world.is_walkable(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                self.energy -= 0.5
                
                # 发现新事物
                resource = self.world.get_resource_at(self.x, self.y)
                if resource and random.random() < 0.3:
                    self.add_memory(f"发现了 {resource['type']}", 5.0, "observation")
        
        elif action_type == "socialize":
            # 简化的社交 - 实际应该查找附近的 AI
            self.energy -= 2
            self.add_memory("尝试与其他 AI 社交", 4.0, "social")
        
        # 保存状态
        self._save_to_db()
    
    def step(self):
        """执行一个完整的思考-行动循环"""
        self.action_timer += 1
        
        # 每 60 步进行一次反思
        if self.action_timer % 60 == 0:
            thought = self.think()
            if thought:
                self.messages.append(f"💭 {thought}")
        
        # 每 30 步重新规划
        if self.action_timer % 30 == 0 or not self.plan:
            self.plan_actions()
        
        # 执行行动
        self.execute_action()
    
    def get_display_messages(self) -> List[str]:
        """获取并清空消息队列"""
        msgs = self.messages.copy()
        self.messages = []
        return msgs


class Game:
    """游戏主类"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AnotherYou v0.4 - 持久化 AI 社会")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("microsoftyahei", 14)
        self.font_large = pygame.font.SysFont("microsoftyahei", 18)
        
        # 初始化世界
        self.world = PersistentWorld()
        
        # 创建玩家
        self.player = SocialAgent("player", "玩家", 30, 25, self.world)
        
        # 创建 AI 社会
        self.agents: List[SocialAgent] = []
        ai_names = ["小蓝", "小红", "小绿", "小黄", "小紫", "小青", "小橙", "小粉"]
        
        for i, name in enumerate(ai_names):
            x = random.randint(10, self.world.width - 10)
            y = random.randint(10, self.world.height - 10)
            agent = SocialAgent(f"ai_{i}", name, x, y, self.world)
            self.agents.append(agent)
        
        # 相机
        self.camera_x = 0
        self.camera_y = 0
        
        # UI 状态
        self.show_inventory = False
        self.show_memory = False
        self.show_relations = False
        self.selected_agent = 0
        
        # 消息日志
        self.messages = []
        
        # 统计
        self.steps = 0
        
        self._log("🌍 AnotherYou v0.4 启动")
        self._log(f"💾 世界已持久化到: {self.world.db_path}")
        self._log(f"🤖 {len(self.agents)} 个 AI 已加载")
        self._log("💡 按 H 查看帮助")
    
    def _log(self, msg: str):
        """添加日志"""
        self.messages.append(msg)
        if len(self.messages) > 25:
            self.messages = self.messages[-25:]
    
    def handle_input(self):
        """处理输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_h:
                    self._show_help()
                
                elif event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.show_memory = False
                    self.show_relations = False
                
                elif event.key == pygame.K_m:
                    self.show_memory = not self.show_memory
                    self.show_inventory = False
                    self.show_relations = False
                
                elif event.key == pygame.K_r:
                    self.show_relations = not self.show_relations
                    self.show_inventory = False
                    self.show_memory = False
                
                elif event.key == pygame.K_SPACE:
                    self._player_gather()
                
                elif event.key == pygame.K_b:
                    self._player_build()
                
                elif event.key == pygame.K_TAB:
                    self.selected_agent = (self.selected_agent + 1) % len(self.agents)
                    self._log(f"👁️ 观察: {self.agents[self.selected_agent].name}")
                
                elif event.key == pygame.K_s:
                    self._force_save()
        
        # 移动
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        if dx != 0 or dy != 0:
            self._move_player(dx, dy)
        
        return True
    
    def _move_player(self, dx: int, dy: int):
        """移动玩家"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if self.world.is_walkable(new_x, new_y):
            self.player.x = new_x
            self.player.y = new_y
            self.player.energy = max(0, self.player.energy - 0.5)
            self.player._save_to_db()
    
    def _player_gather(self):
        """玩家采集"""
        success, msg, res_type = self.world.gather_resource(self.player.x, self.player.y)
        if success:
            self.player.inventory[res_type] = self.player.inventory.get(res_type, 0) + 1
            self.player.energy -= 5
            self.player.total_gathered += 1
            self.player._save_to_db()
            self._log(f"✅ {msg}")
        else:
            self._log(f"❌ {msg}")
    
    def _player_build(self):
        """玩家建造"""
        if self.player.inventory.get("wood", 0) >= 5:
            success, msg = self.world.create_building(
                self.player.x, self.player.y, "house", self.player.agent_id
            )
            if success:
                self.player.inventory["wood"] -= 5
                self.player._save_to_db()
                self._log(f"🏠 {msg}")
            else:
                self._log(f"❌ {msg}")
        else:
            self._log("❌ 需要 5 个木材才能建造")
    
    def _force_save(self):
        """强制保存"""
        for agent in self.agents:
            agent._save_to_db()
        self._log("💾 所有数据已保存")
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
=== AnotherYou v0.4 - 持久化 AI 社会 ===

控制:
  WASD/方向键 - 移动
  空格 - 采集资源
  B - 建造（需要5木材）
  I - 背包
  M - 记忆面板
  R - 关系面板
  TAB - 切换观察的 AI
  S - 强制保存
  H - 帮助
  ESC - 退出

特性:
  💾 自动持久化到 SQLite
  🧠 AI 拥有长期记忆
  🤝 AI 之间形成关系
  🎓 AI 学习技能
  💰 经济系统
  🏠 建造系统

AI 自主推动世界:
  - 24/7 自动运行
  - 采集资源
  - 建造房屋
  - 学习技能
  - 形成社会关系
"""
        print(help_text)
        self._log("📖 帮助已打印到控制台")
    
    def update(self):
        """更新游戏状态"""
        self.steps += 1
        
        # 更新世界时间
        self.world.update()
        
        # 更新 AI（每 30 帧）
        if self.steps % 30 == 0:
            for agent in self.agents:
                agent.step()
                
                # 收集 AI 消息
                for msg in agent.get_display_messages():
                    self._log(f"[{agent.name}] {msg}")
        
        # 相机跟随玩家
        target_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2
        target_y = self.player.y * TILE_SIZE - SCREEN_HEIGHT // 2
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
    
    def render(self):
        """渲染画面"""
        self.screen.fill((20, 20, 30))
        
        # 绘制世界
        self._render_world()
        
        # 绘制 UI
        self._render_ui()
        
        pygame.display.flip()
    
    def _render_world(self):
        """绘制世界"""
        start_x = int(self.camera_x // TILE_SIZE)
        start_y = int(self.camera_y // TILE_SIZE)
        end_x = start_x + SCREEN_WIDTH // TILE_SIZE + 2
        end_y = start_y + SCREEN_HEIGHT // TILE_SIZE + 2
        
        # 绘制地形
        for x in range(max(0, start_x), min(self.world.width, end_x)):
            for y in range(max(0, start_y), min(self.world.height, end_y)):
                screen_x = int(x * TILE_SIZE - self.camera_x)
                screen_y = int(y * TILE_SIZE - self.camera_y)
                
                tile = self.world.get_tile(x, y)
                color = COLORS.get(tile, COLORS["grass"])
                
                pygame.draw.rect(self.screen, color, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, (40, 40, 40), 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
        
        # 绘制资源
        for x in range(max(0, start_x), min(self.world.width, end_x)):
            for y in range(max(0, start_y), min(self.world.height, end_y)):
                resource = self.world.get_resource_at(x, y)
                if resource:
                    screen_x = int(x * TILE_SIZE - self.camera_x)
                    screen_y = int(y * TILE_SIZE - self.camera_y)
                    
                    color = COLORS.get(resource["type"], (200, 200, 200))
                    pygame.draw.circle(self.screen, color,
                                     (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2),
                                     TILE_SIZE//3)
        
        # 绘制建筑
        for building in self.world.get_buildings():
            screen_x = int(building["x"] * TILE_SIZE - self.camera_x)
            screen_y = int(building["y"] * TILE_SIZE - self.camera_y)
            
            if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                color = COLORS.get(building["type"], COLORS["house"])
                pygame.draw.rect(self.screen, color,
                               (screen_x + 2, screen_y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
        
        # 绘制 AI
        for i, agent in enumerate(self.agents):
            screen_x = int(agent.x * TILE_SIZE - self.camera_x)
            screen_y = int(agent.y * TILE_SIZE - self.camera_y)
            
            if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                # 根据关系选择颜色
                color = COLORS["ai"]
                if self.player.agent_id in agent.relationships:
                    rel = agent.relationships[self.player.agent_id]
                    if rel["type"] == RelationshipType.FRIEND.value:
                        color = COLORS["ai_friend"]
                    elif rel["type"] == RelationshipType.ENEMY.value:
                        color = COLORS["ai_enemy"]
                
                pygame.draw.rect(self.screen, color,
                               (screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8),
                               border_radius=4)
                
                # 名字
                name_text = self.font.render(agent.name, True, (255, 255, 255))
                self.screen.blit(name_text, (screen_x, screen_y - 15))
                
                # 选中标记
                if i == self.selected_agent:
                    pygame.draw.rect(self.screen, (255, 255, 0),
                                   (screen_x - 2, screen_y - 2, TILE_SIZE + 4, TILE_SIZE + 4),
                                   2, border_radius=4)
        
        # 绘制玩家
        px = int(self.player.x * TILE_SIZE - self.camera_x)
        py = int(self.player.y * TILE_SIZE - self.camera_y)
        pygame.draw.rect(self.screen, COLORS["player"],
                       (px + 4, py + 4, TILE_SIZE - 8, TILE_SIZE - 8),
                       border_radius=4)
        name_text = self.font.render(self.player.name, True, (255, 255, 255))
        self.screen.blit(name_text, (px, py - 15))
    
    def _render_ui(self):
        """绘制 UI"""
        # 顶部信息栏
        pygame.draw.rect(self.screen, COLORS["ui_bg"], (0, 0, SCREEN_WIDTH, 50))
        
        time_text = f"Day {self.world.day} {self.world.hour:02d}:00"
        self.screen.blit(self.font_large.render(time_text, True, COLORS["ui_text"]), (10, 10))
        
        player_info = f"体力: {self.player.energy:.0f} | 金币: {self.player.gold}"
        self.screen.blit(self.font_large.render(player_info, True, COLORS["ui_gold"]), (150, 10))
        
        ai_info = f"AI: {len(self.agents)} | 观察: {self.agents[self.selected_agent].name}"
        self.screen.blit(self.font_large.render(ai_info, True, COLORS["ui_blue"]), (400, 10))
        
        # 消息日志
        log_y = SCREEN_HEIGHT - 200
        pygame.draw.rect(self.screen, COLORS["ui_panel"], (10, log_y, 450, 190))
        
        for i, msg in enumerate(self.messages[-10:]):
            msg_surface = self.font.render(msg[:60], True, (200, 200, 200))
            self.screen.blit(msg_surface, (15, log_y + 5 + i * 18))
        
        # 面板
        if self.show_inventory:
            self._render_panel(SCREEN_WIDTH - 250, 60, 240, 250, "📦 背包",
                             [f"{k}: {v}" for k, v in self.player.inventory.items() if v > 0] +
                             ["", f"金币: {self.player.gold}"])
        
        if self.show_memory:
            agent = self.agents[self.selected_agent]
            memories = agent.get_important_memories(8)
            content = [f"• {m.content[:35]}" for m in memories]
            self._render_panel(SCREEN_WIDTH - 500, 60, 490, 300, f"🧠 {agent.name} 的记忆", content)
        
        if self.show_relations:
            agent = self.agents[self.selected_agent]
            content = []
            for other_id, rel in agent.relationships.items():
                other_name = other_id
                for a in self.agents:
                    if a.agent_id == other_id:
                        other_name = a.name
                        break
                content.append(f"{other_name}: {rel['type']} ({rel['affinity']:+.2f})")
            if not content:
                content = ["还没有建立关系..."]
            self._render_panel(SCREEN_WIDTH - 250, 320, 240, 200, f"🤝 {agent.name} 的关系", content)
        
        # 底部提示
        hint = "WASD移动 | 空格采集 | B建造 | I背包 | M记忆 | R关系 | TAB切换 | S保存 | H帮助 | ESC退出"
        hint_surface = self.font.render(hint, True, (150, 150, 150))
        self.screen.blit(hint_surface, (10, SCREEN_HEIGHT - 20))
    
    def _render_panel(self, x: int, y: int, w: int, h: int, title: str, items: List[str]):
        """绘制面板"""
        pygame.draw.rect(self.screen, COLORS["ui_panel"], (x, y, w, h))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h), 2)
        
        title_surface = self.font_large.render(title, True, COLORS["ui_gold"])
        self.screen.blit(title_surface, (x + 10, y + 10))
        
        for i, item in enumerate(items):
            text_surface = self.font.render(item, True, COLORS["ui_text"])
            self.screen.blit(text_surface, (x + 15, y + 35 + i * 18))
    
    def run(self):
        """主循环"""
        running = True
        
        try:
            while running:
                running = self.handle_input()
                self.update()
                self.render()
                self.clock.tick(FPS)
        finally:
            # 确保保存所有数据
            self._force_save()
            self.world.close()
            pygame.quit()


if __name__ == "__main__":
    print("🌍 AnotherYou v0.4 - 持久化 AI 社会")
    print("=" * 50)
    Game().run()
