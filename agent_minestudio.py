"""
Agent with MineStudio - 使用真实MineStudio模拟器的AI
"""

import sys
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Optional

# 尝试导入MineStudio，如果不可用则使用Mock
try:
    from minestudio.simulator import MinecraftSim
    from minestudio.simulator.callbacks import RecordCallback
    MINESTUDIO_AVAILABLE = True
    print("✅ MineStudio已加载")
except ImportError:
    MINESTUDIO_AVAILABLE = False
    print("⚠️  MineStudio未安装，使用Mock模式")
    
    # Mock类
    class MinecraftSim:
        def __init__(self, **kwargs):
            self.step_count = 0
            self.inventory = {}
            self.location = (0, 64, 0)
            
        def reset(self):
            self.step_count = 0
            obs = {
                "image": None,
                "inventory": self.inventory,
                "location": self.location
            }
            info = {"location": self.location}
            return obs, info
            
        def step(self, action):
            self.step_count += 1
            
            # 模拟动作效果
            if action == "attack":
                self.inventory["wood"] = self.inventory.get("wood", 0) + 1
            elif action in ["forward", "back", "left", "right"]:
                x, y, z = self.location
                if action == "forward": z += 1
                elif action == "back": z -= 1
                elif action == "left": x -= 1
                elif action == "right": x += 1
                self.location = (x, y, z)
                
            obs = {
                "image": None,
                "inventory": self.inventory,
                "location": self.location
            }
            reward = 1.0
            terminated = False
            truncated = self.step_count > 1000
            info = {"location": self.location}
            
            return obs, reward, terminated, truncated, info
            
        def close(self):
            pass


class MineStudioAgent:
    """
    使用MineStudio的AI数字分身
    """
    
    # MineStudio动作空间
    ACTIONS = [
        "forward", "back", "left", "right",  # 移动
        "jump", "sneak", "sprint",           # 动作
        "attack", "use",                     # 交互
        "drop", "craft",                     # 物品
        "inventory",                         # 背包
        "camera_up", "camera_down",          # 视角
        "camera_left", "camera_right",
        "noop",                              # 无操作
    ]
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.agent_id = f"{player_name}_{int(time.time())}"
        
        # MineStudio模拟器
        self.sim = None
        self.obs_size = (224, 224)
        self.render_size = (640, 360)
        
        # 状态
        self.location = {"x": 0, "y": 64, "z": 0}
        self.inventory = {}
        self.energy = 100.0
        self.hunger = 0.0
        
        # 记忆
        self.memories = []
        
        # 统计
        self.birth_time = datetime.now()
        self.total_steps = 0
        self.is_running = False
        
    def start(self):
        """启动AI"""
        print(f"\n{'='*60}")
        print(f"🌟 「另一个你」MineStudio版")
        print(f"   玩家: {self.player_name}")
        print(f"   模式: {'真实MineStudio' if MINESTUDIO_AVAILABLE else 'Mock模拟'}")
        print(f"{'='*60}\n")
        
        # 创建模拟器
        print("[系统] 启动Minecraft模拟器...")
        try:
            self.sim = MinecraftSim(
                obs_size=self.obs_size,
                render_size=self.render_size,
            )
            print("[系统] ✅ 模拟器启动成功！")
        except Exception as e:
            print(f"[系统] ❌ 启动失败: {e}")
            return False
            
        # 重置环境
        obs, info = self.sim.reset()
        self._update_state(obs, info)
        
        print(f"[系统] 初始位置: {self.location}")
        print(f"[系统] 初始背包: {self.inventory}\n")
        
        return True
        
    def run_episode(self, max_steps: int = 100):
        """运行一个 episode"""
        self.is_running = True
        
        print(f"🎮 开始Episode (最多{max_steps}步)\n")
        
        for step in range(max_steps):
            if not self.is_running:
                break
                
            # 1. 观察
            obs = {
                "location": self.location,
                "inventory": self.inventory,
                "energy": self.energy,
            }
            
            # 2. 决策
            action = self._decide(obs)
            
            # 3. 执行
            obs, reward, terminated, truncated, info = self.sim.step(action)
            self.total_steps += 1
            
            # 4. 更新状态
            self._update_state(obs, info)
            
            # 5. 记录
            self._remember(action, reward)
            
            # 6. 输出
            if step % 10 == 0:
                self._report(step)
                
            # 检查结束
            if terminated or truncated:
                print(f"\n🏁 Episode结束于第{step+1}步")
                break
                
        self.is_running = False
        
    def _decide(self, obs: Dict) -> str:
        """决策下一步动作"""
        # 简单规则决策
        
        # 生存优先
        if self.energy < 30:
            return "noop"  # 休息
            
        # 收集资源
        if "wood" not in self.inventory or self.inventory.get("wood", 0) < 10:
            return "attack"  # 砍树/挖矿
            
        # 探索
        move_actions = ["forward", "back", "left", "right"]
        return random.choice(move_actions)
        
    def _update_state(self, obs: Dict, info: Dict):
        """更新状态"""
        # 从观察中提取信息
        if "location" in obs:
            loc = obs["location"]
            if isinstance(loc, tuple):
                self.location = {"x": loc[0], "y": loc[1], "z": loc[2]}
            else:
                self.location = loc
                
        if "inventory" in obs:
            self.inventory = obs["inventory"]
            
        # 能量消耗
        self.energy = max(0, self.energy - 0.5)
        self.hunger = min(100, self.hunger + 0.3)
        
    def _remember(self, action: str, reward: float):
        """记录记忆"""
        self.memories.append({
            "step": self.total_steps,
            "action": action,
            "reward": reward,
            "location": self.location.copy(),
        })
        
        # 只保留最近100条
        if len(self.memories) > 100:
            self.memories.pop(0)
            
    def _report(self, step: int):
        """状态报告"""
        print(f"Step {step:3d} | 位置({self.location['x']:3d}, {self.location['y']:3d}, {self.location['z']:3d}) | "
              f"背包{self.inventory} | 能量{self.energy:.0f}%")
              
    def stop(self):
        """停止"""
        print(f"\n👋 {self.player_name} 停止运行")
        print(f"   总步数: {self.total_steps}")
        print(f"   记忆数: {len(self.memories)}")
        
        if self.sim:
            self.sim.close()
            
        self.is_running = False


def main():
    """主函数"""
    agent = MineStudioAgent(player_name="测试AI")
    
    if agent.start():
        try:
            agent.run_episode(max_steps=50)
        except KeyboardInterrupt:
            print("\n\n收到停止信号...")
        finally:
            agent.stop()


if __name__ == "__main__":
    main()
