"""
World Coordinator - 世界协调器
管理多个AI在同一个世界的协作
"""

import asyncio
import json
import time
from typing import Dict, List
from datetime import datetime

class WorldCoordinator:
    """
    世界协调器
    - 管理多个AI
    - 协调资源分配
    - 促进AI间交互
    """
    
    def __init__(self, world_name: str = "default"):
        self.world_name = world_name
        self.agents: Dict[str, 'Agent'] = {}
        self.global_events: List[Dict] = []
        self.economy = {
            "total_resources": {},
            "transactions": [],
        }
        
    def register_agent(self, agent):
        """注册AI"""
        self.agents[agent.agent_id] = agent
        print(f"[世界] {agent.player_name} 加入了世界")
        
    def unregister_agent(self, agent_id: str):
        """注销AI"""
        if agent_id in self.agents:
            name = self.agents[agent_id].player_name
            del self.agents[agent_id]
            print(f"[世界] {name} 离开了世界")
            
    def broadcast(self, message: str, exclude: str = None):
        """广播消息给所有AI"""
        for aid, agent in self.agents.items():
            if aid != exclude:
                agent.memory.add(f"[广播] {message}", importance=0.3)
                
    def get_nearby_agents(self, position: Dict, radius: int = 50) -> List[str]:
        """获取附近的AI"""
        nearby = []
        for aid, agent in self.agents.items():
            dist = self._distance(position, agent.location)
            if dist <= radius:
                nearby.append(aid)
        return nearby
        
    def _distance(self, p1: Dict, p2: Dict) -> float:
        """计算距离"""
        return ((p1.get('x', 0) - p2.get('x', 0)) ** 2 +
                (p1.get('z', 0) - p2.get('z', 0)) ** 2) ** 0.5
        
    def facilitate_trade(self, agent1_id: str, agent2_id: str, 
                        item1: str, item2: str) -> bool:
        """促成交易"""
        if agent1_id not in self.agents or agent2_id not in self.agents:
            return False
            
        a1 = self.agents[agent1_id]
        a2 = self.agents[agent2_id]
        
        # 记录交易
        transaction = {
            "time": datetime.now().isoformat(),
            "agent1": a1.player_name,
            "agent2": a2.player_name,
            "item1": item1,
            "item2": item2,
        }
        self.economy["transactions"].append(transaction)
        
        # 通知双方
        a1.memory.add(f"与{a2.player_name}交易: 用{item1}换{item2}", importance=0.6)
        a2.memory.add(f"与{a1.player_name}交易: 用{item2}换{item1}", importance=0.6)
        
        print(f"[交易] {a1.player_name} <-> {a2.player_name}: {item1} <-> {item2}")
        return True
        
    def get_world_stats(self) -> Dict:
        """获取世界统计"""
        return {
            "world_name": self.world_name,
            "agent_count": len(self.agents),
            "agents": [a.player_name for a in self.agents.values()],
            "total_transactions": len(self.economy["transactions"]),
            "events": len(self.global_events),
        }
