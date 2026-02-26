"""
Utils - 工具函数
"""

import json
import os
from datetime import datetime

def save_json(data: dict, filepath: str):
    """保存JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath: str) -> dict:
    """加载JSON"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_time(dt: datetime = None) -> str:
    """格式化时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def calculate_distance(pos1: dict, pos2: dict) -> float:
    """计算距离"""
    return ((pos1.get('x', 0) - pos2.get('x', 0)) ** 2 +
            (pos1.get('y', 0) - pos2.get('y', 0)) ** 2 +
            (pos1.get('z', 0) - pos2.get('z', 0)) ** 2) ** 0.5
