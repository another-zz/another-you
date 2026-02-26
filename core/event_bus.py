"""
Event Bus - 事件总线
AI间通信机制
"""

from typing import Dict, List, Callable
from datetime import datetime

class EventBus:
    """事件总线 - 解耦AI间通信"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict] = []
        
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def publish(self, event_type: str, data: dict):
        """发布事件"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self.event_history.append(event)
        
        # 通知订阅者
        for callback in self.subscribers.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Event handler error: {e}")
                
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """获取事件历史"""
        events = self.event_history
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]
