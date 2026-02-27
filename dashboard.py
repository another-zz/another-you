#!/usr/bin/env python3
"""
AnotherYou 实时观测系统
集成 Web Dashboard + 真实AI数据
"""

import asyncio
import argparse
import sys
import os
import threading
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import Agent
from core.world_coordinator import WorldCoordinator
from core.social_network import SocialNetwork

# 全局状态（共享给Web服务器）
world_state = {
    "agents": {},
    "logs": [],
    "is_running": False,
    "last_update": None
}

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_file('ui/web/index.html', 'text/html')
        elif self.path == '/api/state':
            self.serve_json()
        else:
            self.send_error(404)
    
    def serve_file(self, path, content_type):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except:
            self.send_error(404)
    
    def serve_json(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        data = world_state.copy()
        data["last_update"] = datetime.now().isoformat()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))
    
    def log_message(self, *args): pass

def start_web_server(port=8080):
    """在后台启动Web服务器"""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"🌐 Web Dashboard: http://localhost:{port}")
    server.serve_forever()

def update_agent_state(agent):
    """更新单个AI的状态到全局状态"""
    status = agent.get_status()
    world_state["agents"][agent.player_name] = {
        "name": agent.player_name,
        "energy": status.get("energy", 0),
        "total_actions": status.get("total_actions", 0),
        "inventory": status.get("inventory", {}),
        "current_plan": status.get("current_plan", ""),
        "memory_count": 0,  # 从status解析
        "social": status.get("social", {})
    }

def add_log(agent_name, message, log_type="action"):
    """添加日志"""
    world_state["logs"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": agent_name,
        "message": message,
        "type": log_type
    })
    # 只保留最近50条
    if len(world_state["logs"]) > 50:
        world_state["logs"] = world_state["logs"][-50:]

async def run_world(agent_names, mc_host, mc_port, api_key=None, provider=None):
    """运行多AI世界"""
    
    social_network = SocialNetwork()
    world = WorldCoordinator(world_name="AI文明世界")
    
    agents = []
    for name in agent_names:
        agent = Agent(
            player_name=name,
            coordinator=world,
            social_network=social_network,
            mc_host=mc_host,
            mc_port=mc_port,
            api_key=api_key,
            provider=provider
        )
        agents.append(agent)
    
    print(f"\n{'='*60}")
    print(f"🌍 AnotherYou - AI实时观测系统")
    print(f"{'='*60}")
    print(f"AI数量: {len(agents)}")
    print(f"AI列表: {', '.join(agent_names)}")
    print(f"Web面板: http://localhost:8080")
    print(f"{'='*60}\n")
    
    # 启动所有AI
    for agent in agents:
        agent.is_running = True
        add_log(agent.player_name, "加入了世界", "system")
    
    world_state["is_running"] = True
    
    # 主循环
    tick = 0
    try:
        while tick < 1000:  # 最多1000个tick
            tick += 1
            
            for agent in agents:
                # 执行一个tick
                await agent._life_tick()
                
                # 更新状态到全局
                update_agent_state(agent)
                
                # 记录行动日志
                if agent.total_actions % 5 == 0:
                    add_log(agent.player_name, f"执行了行动 #{agent.total_actions}")
            
            # 记录社交事件
            if tick % 10 == 0:
                for event in social_network.social_events[-2:]:
                    add_log(
                        "系统", 
                        f"{event.get('agent_a', '')} {event.get('type', 'event')} {event.get('agent_b', '')}",
                        "social"
                    )
            
            await asyncio.sleep(2)  # 每2秒一个tick
            
    except KeyboardInterrupt:
        print("\n\n🛑 停止所有AI...")
    
    # 停止
    for agent in agents:
        await agent.stop()
        add_log(agent.player_name, "离开了世界", "system")
    
    world_state["is_running"] = False
    
    print(f"\n{'='*60}")
    print(f"📊 世界统计")
    print(f"{'='*60}")
    print(f"总tick: {tick}")
    print(f"AI数量: {len(agents)}")

async def main():
    parser = argparse.ArgumentParser(description="AnotherYou - AI实时观测系统")
    parser.add_argument("--names", nargs="+", default=["Alice", "Bob", "Charlie"], help="AI名称列表")
    parser.add_argument("--host", default="localhost", help="Minecraft服务器地址")
    parser.add_argument("--port", type=int, default=25565, help="Minecraft服务器端口")
    parser.add_argument("--api-key", default=None, help="API Key")
    parser.add_argument("--web-port", type=int, default=8080, help="Web面板端口")
    
    args = parser.parse_args()
    
    # 启动Web服务器（后台线程）
    web_thread = threading.Thread(target=start_web_server, args=(args.web_port,), daemon=True)
    web_thread.start()
    
    # 等待Web服务器启动
    await asyncio.sleep(1)
    
    # 运行AI世界
    await run_world(args.names, args.host, args.port, args.api_key)

if __name__ == "__main__":
    asyncio.run(main())
