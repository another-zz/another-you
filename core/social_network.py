"""
Social Network - 社会网络系统

Project Sid风格的社会关系：
- 关系图（朋友/敌人/中立）
- 声望系统
- 派系/群体形成
- 社交记忆
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import math


@dataclass
class Relationship:
    """两个AI之间的关系"""
    agent_a: str
    agent_b: str
    
    # 关系值 -100(敌人) ~ +100(挚友)
    value: float = 0.0
    
    # 关系类型
    relation_type: str = "neutral"  # friend/enemy/rival/ally/neutral
    
    # 互动历史
    interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    # 首次和最后互动
    first_met: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    
    # 共享记忆
    shared_memories: List[str] = None
    
    def __post_init__(self):
        if self.shared_memories is None:
            self.shared_memories = []
        if self.first_met is None:
            self.first_met = datetime.now()
            
    def update(self, delta: float, interaction_type: str = "neutral"):
        """更新关系值"""
        self.value = max(-100, min(100, self.value + delta))
        self.interactions += 1
        self.last_interaction = datetime.now()
        
        if delta > 0:
            self.positive_interactions += 1
        elif delta < 0:
            self.negative_interactions += 1
            
        # 更新关系类型
        if self.value >= 50:
            self.relation_type = "friend"
        elif self.value >= 20:
            self.relation_type = "ally"
        elif self.value <= -50:
            self.relation_type = "enemy"
        elif self.value <= -20:
            self.relation_type = "rival"
        else:
            self.relation_type = "neutral"


class SocialNetwork:
    """
    社会网络
    
    管理所有AI之间的社会关系
    """
    
    def __init__(self, network_dir: str = "data/social"):
        self.network_dir = network_dir
        os.makedirs(network_dir, exist_ok=True)
        
        # 关系图: {(agent_a, agent_b): Relationship}
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        
        # 声望系统: {agent_id: reputation_score}
        self.reputation: Dict[str, float] = {}
        
        # 派系: {faction_name: {member_ids}}
        self.factions: Dict[str, Set[str]] = {}
        
        # 社交事件历史
        self.social_events: List[Dict] = []
        
        self._load()
        
    def _get_key(self, agent_a: str, agent_b: str) -> Tuple[str, str]:
        """获取关系键（确保顺序一致）"""
        return tuple(sorted([agent_a, agent_b]))
        
    def _load(self):
        """加载社会关系数据"""
        filepath = os.path.join(self.network_dir, "network.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 加载关系
                for rel_data in data.get('relationships', []):
                    key = (rel_data['agent_a'], rel_data['agent_b'])
                    rel = Relationship(
                        agent_a=rel_data['agent_a'],
                        agent_b=rel_data['agent_b'],
                        value=rel_data.get('value', 0),
                        relation_type=rel_data.get('relation_type', 'neutral'),
                        interactions=rel_data.get('interactions', 0),
                        positive_interactions=rel_data.get('positive_interactions', 0),
                        negative_interactions=rel_data.get('negative_interactions', 0),
                        shared_memories=rel_data.get('shared_memories', [])
                    )
                    if rel_data.get('first_met'):
                        rel.first_met = datetime.fromisoformat(rel_data['first_met'])
                    if rel_data.get('last_interaction'):
                        rel.last_interaction = datetime.fromisoformat(rel_data['last_interaction'])
                    self.relationships[key] = rel
                    
                # 加载声望
                self.reputation = data.get('reputation', {})
                
                # 加载派系
                self.factions = {
                    k: set(v) for k, v in data.get('factions', {}).items()
                }
                
    def save(self):
        """保存社会关系数据"""
        filepath = os.path.join(self.network_dir, "network.json")
        
        data = {
            'relationships': [],
            'reputation': self.reputation,
            'factions': {k: list(v) for k, v in self.factions.items()},
            'saved_at': datetime.now().isoformat()
        }
        
        for rel in self.relationships.values():
            rel_data = {
                'agent_a': rel.agent_a,
                'agent_b': rel.agent_b,
                'value': rel.value,
                'relation_type': rel.relation_type,
                'interactions': rel.interactions,
                'positive_interactions': rel.positive_interactions,
                'negative_interactions': rel.negative_interactions,
                'first_met': rel.first_met.isoformat() if rel.first_met else None,
                'last_interaction': rel.last_interaction.isoformat() if rel.last_interaction else None,
                'shared_memories': rel.shared_memories
            }
            data['relationships'].append(rel_data)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def get_relationship(self, agent_a: str, agent_b: str) -> Optional[Relationship]:
        """获取两个AI之间的关系"""
        key = self._get_key(agent_a, agent_b)
        return self.relationships.get(key)
        
    def create_relationship(self, agent_a: str, agent_b: str) -> Relationship:
        """创建新关系"""
        key = self._get_key(agent_a, agent_b)
        
        if key not in self.relationships:
            rel = Relationship(agent_a=key[0], agent_b=key[1])
            self.relationships[key] = rel
            
            # 记录社交事件
            self.social_events.append({
                'type': 'first_meet',
                'agent_a': agent_a,
                'agent_b': agent_b,
                'timestamp': datetime.now().isoformat()
            })
            
        return self.relationships[key]
        
    def update_relationship(self, agent_a: str, agent_b: str, 
                           delta: float, interaction_type: str = "neutral"):
        """更新关系值"""
        rel = self.get_relationship(agent_a, agent_b)
        if not rel:
            rel = self.create_relationship(agent_a, agent_b)
            
        old_type = rel.relation_type
        rel.update(delta, interaction_type)
        
        # 关系类型变化时记录事件
        if old_type != rel.relation_type:
            self.social_events.append({
                'type': 'relation_change',
                'agent_a': agent_a,
                'agent_b': agent_b,
                'from': old_type,
                'to': rel.relation_type,
                'timestamp': datetime.now().isoformat()
            })
            
    def get_friends(self, agent_id: str) -> List[str]:
        """获取AI的朋友列表"""
        friends = []
        for key, rel in self.relationships.items():
            if agent_id in key and rel.relation_type == "friend":
                other = key[0] if key[1] == agent_id else key[1]
                friends.append(other)
        return friends
        
    def get_enemies(self, agent_id: str) -> List[str]:
        """获取AI的敌人列表"""
        enemies = []
        for key, rel in self.relationships.items():
            if agent_id in key and rel.relation_type == "enemy":
                other = key[0] if key[1] == agent_id else key[1]
                enemies.append(other)
        return enemies
        
    def get_allies(self, agent_id: str) -> List[str]:
        """获取AI的盟友列表"""
        allies = []
        for key, rel in self.relationships.items():
            if agent_id in key and rel.relation_type in ["ally", "friend"]:
                other = key[0] if key[1] == agent_id else key[1]
                allies.append(other)
        return allies
        
    def update_reputation(self, agent_id: str, delta: float):
        """更新声望"""
        current = self.reputation.get(agent_id, 50)
        self.reputation[agent_id] = max(0, min(100, current + delta))
        
    def get_reputation(self, agent_id: str) -> float:
        """获取声望"""
        return self.reputation.get(agent_id, 50)
        
    def create_faction(self, name: str, founder: str) -> bool:
        """创建派系"""
        if name in self.factions:
            return False
            
        self.factions[name] = {founder}
        
        self.social_events.append({
            'type': 'faction_created',
            'faction': name,
            'founder': founder,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
        
    def join_faction(self, faction_name: str, agent_id: str) -> bool:
        """加入派系"""
        if faction_name not in self.factions:
            return False
            
        self.factions[faction_name].add(agent_id)
        
        self.social_events.append({
            'type': 'faction_join',
            'faction': faction_name,
            'agent': agent_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
        
    def leave_faction(self, faction_name: str, agent_id: str):
        """离开派系"""
        if faction_name in self.factions:
            self.factions[faction_name].discard(agent_id)
            
    def get_faction_members(self, faction_name: str) -> List[str]:
        """获取派系成员"""
        return list(self.factions.get(faction_name, []))
        
    def get_agent_factions(self, agent_id: str) -> List[str]:
        """获取AI所属的所有派系"""
        return [name for name, members in self.factions.items() if agent_id in members]
        
    def get_social_summary(self, agent_id: str) -> Dict:
        """获取AI的社交摘要"""
        return {
            'friends': len(self.get_friends(agent_id)),
            'enemies': len(self.get_enemies(agent_id)),
            'allies': len(self.get_allies(agent_id)),
            'reputation': self.get_reputation(agent_id),
            'factions': self.get_agent_factions(agent_id)
        }
        
    def get_network_stats(self) -> Dict:
        """获取整个网络的统计"""
        return {
            'total_relationships': len(self.relationships),
            'total_agents': len(set(
                agent for key in self.relationships.keys() for agent in key
            )),
            'total_factions': len(self.factions),
            'total_events': len(self.social_events)
        }
