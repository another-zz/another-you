"""
AnotherYou v1.0 - 完整测试套件
"""

import unittest
import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.vector_memory import VectorMemory
from core.economy import EconomySystem
from core.utils import calculate_distance

class TestVectorMemory(unittest.TestCase):
    """测试向量记忆"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory = VectorMemory("test_agent", self.temp_dir)
        
    def test_add_and_retrieve(self):
        """测试添加和检索"""
        self.memory.add("测试记忆", importance=0.8)
        results = self.memory.retrieve("测试")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "测试记忆")
        
    def test_importance_filtering(self):
        """测试重要性过滤"""
        self.memory.add("重要事件", importance=0.9)
        self.memory.add("普通事件", importance=0.3)
        important = self.memory.get_important(min_importance=0.8)
        self.assertEqual(len(important), 1)
        self.assertEqual(important[0], "重要事件")

class TestEconomy(unittest.TestCase):
    """测试经济系统"""
    
    def setUp(self):
        self.econ = EconomySystem()
        
    def test_evaluate_inventory(self):
        """测试背包评估"""
        inventory = {"wood": 10, "stone": 5}
        value = self.econ.evaluate_inventory(inventory)
        expected = 10 * 1 + 5 * 2  # wood=1, stone=2
        self.assertEqual(value, expected)
        
    def test_trade_calculation(self):
        """测试交易计算"""
        a1, a2 = self.econ.calculate_fair_trade("wood", "stone")
        # wood=1, stone=2
        # 验证返回的是正整数
        self.assertGreater(a1, 0)
        self.assertGreater(a2, 0)

class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_distance(self):
        """测试距离计算"""
        p1 = {"x": 0, "y": 0, "z": 0}
        p2 = {"x": 3, "y": 4, "z": 0}
        dist = calculate_distance(p1, p2)
        self.assertEqual(dist, 5.0)  # 3-4-5三角形

if __name__ == "__main__":
    unittest.main()
