"""
Economy System - AI经济系统
资源、交易、市场
"""

import json
from typing import Dict, List
from datetime import datetime

class EconomySystem:
    """
    AI经济系统
    - 资源价值评估
    - 自动交易匹配
    - 市场价格动态
    """
    
    # 基础资源价值
    BASE_VALUES = {
        "wood": 1,
        "stone": 2,
        "iron": 10,
        "gold": 50,
        "diamond": 100,
        "food": 3,
        "tool": 15,
    }
    
    def __init__(self):
        self.market_prices: Dict[str, float] = self.BASE_VALUES.copy()
        self.agent_balances: Dict[str, Dict[str, int]] = {}
        self.trade_history: List[Dict] = []
        
    def evaluate_inventory(self, inventory: Dict[str, int]) -> float:
        """评估背包总价值"""
        total = 0
        for item, count in inventory.items():
            price = self.market_prices.get(item, 1)
            total += price * count
        return total
        
    def should_trade(self, agent_inventory: Dict, need: str) -> bool:
        """判断是否应该交易"""
        # 如果有需求且有多余资源
        if need not in agent_inventory or agent_inventory[need] < 5:
            # 检查是否有可交易的资源
            for item, count in agent_inventory.items():
                if count > 10 and item != need:
                    return True
        return False
        
    def find_trade_partner(self, agent_id: str, need: str, 
                          all_agents: Dict) -> str:
        """寻找交易伙伴"""
        for other_id, other in all_agents.items():
            if other_id == agent_id:
                continue
                
            # 对方有我需要的东西
            if need in other.inventory and other.inventory[need] > 5:
                # 我有对方可能需要的东西
                my_inventory = all_agents[agent_id].inventory
                for my_item, count in my_inventory.items():
                    if count > 10 and my_item != need:
                        return other_id
                        
        return None
        
    def calculate_fair_trade(self, item1: str, item2: str) -> tuple:
        """计算公平交易比例"""
        v1 = self.market_prices.get(item1, 1)
        v2 = self.market_prices.get(item2, 1)
        
        # 比例
        ratio = v1 / v2 if v2 > 0 else 1
        
        # 返回 (item1数量, item2数量)
        if ratio >= 1:
            return (int(ratio), 1)
        else:
            return (1, int(1/ratio))
            
    def update_prices(self):
        """根据交易历史更新市场价格"""
        if not self.trade_history:
            return
            
        # 统计最近交易
        recent = self.trade_history[-20:]
        demand = {}
        
        for trade in recent:
            item = trade.get("item_received")
            if item:
                demand[item] = demand.get(item, 0) + 1
                
        # 需求高的物品涨价
        for item, count in demand.items():
            if count > 5:
                self.market_prices[item] *= 1.1
                
    def record_trade(self, agent1: str, agent2: str, 
                    item_given: str, item_received: str):
        """记录交易"""
        self.trade_history.append({
            "time": datetime.now().isoformat(),
            "agent1": agent1,
            "agent2": agent2,
            "item_given": item_given,
            "item_received": item_received,
        })
        
        # 每10次交易更新价格
        if len(self.trade_history) % 10 == 0:
            self.update_prices()
