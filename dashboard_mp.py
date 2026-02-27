#!/usr/bin/env python3
"""
AnotherYou Multi-Process Dashboard
每个AI独立进程运行
"""

import json
import os
import sys
import time
import threading
import multiprocessing as mp
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 全局状态（主进程共享）
manager = mp.Manager()
world_state = manager.dict()
world_state["agents"] = manager.dict()
world_state["logs"] = manager.list()
world_state["is_running"] = manager.Value('b', False)

def run_agent_process(agent_name, api_key, shared_state):
    """每个AI的独立进程"""
    import asyncio
    from core.agent import Agent
    from core.world_coordinator import WorldCoordinator
    from core.social_network import SocialNetwork
    
    # 每个进程有自己的世界和社交网络
    social_network = SocialNetwork()
    world = WorldCoordinator(world_name=f"{agent_name}的世界")
    
    agent = Agent(
        player_name=agent_name,
        coordinator=world,
        social_network=social_network,
        api_key=api_key,
        provider="kimi" if api_key else "mock"
    )
    agent.is_running = True
    
    print(f"🤖 {agent_name} 进程启动")
    
    async def agent_loop():
        while agent.is_running:
            await agent._life_tick()
            
            # 更新共享状态
            status = agent.get_status()
            shared_state["agents"][agent_name] = {
                "name": agent_name,
                "energy": status.get("energy", 0),
                "hunger": status.get("hunger", 0),
                "total_actions": status.get("total_actions", 0),
                "inventory": dict(status.get("inventory", {})),
                "location": dict(status.get("location", {"x": 0, "y": 0, "z": 0})),
                "current_plan": status.get("current_plan", "无计划"),
                "skills": list(status.get("skills", [])),
                "social": dict(status.get("social", {}))
            }
            
            # 添加日志
            if agent.total_actions % 5 == 0:
                shared_state["logs"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "agent": agent_name,
                    "message": f"执行了行动 #{agent.total_actions}",
                    "type": "action"
                })
            
            await asyncio.sleep(2)
    
    try:
        asyncio.run(agent_loop())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(agent.stop())
        print(f"👋 {agent_name} 进程停止")

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
        self.end_headers()
        
        # 转换Manager对象为标准Python对象
        data = {
            "agents": dict(world_state["agents"]),
            "logs": list(world_state["logs"])[-50:],  # 最近50条
            "is_running": world_state["is_running"].value,
            "last_update": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))
    
    def log_message(self, *args): pass

def start_web_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"🌐 Web Dashboard: http://localhost:{port}")
    server.serve_forever()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AnotherYou - 多进程AI观测系统")
    parser.add_argument("--names", nargs="+", default=["Alice", "Bob", "Charlie"], help="AI名称列表")
    parser.add_argument("--api-key", default=os.getenv("KIMI_API_KEY"), help="Kimi API Key")
    parser.add_argument("--web-port", type=int, default=8080, help="Web面板端口")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("⚠️  未提供 API Key，将使用 mock 模式")
        print("   设置方法: export KIMI_API_KEY='sk-your-key'")
        print("   或: python3 dashboard_mp.py --api-key 'sk-your-key'")
    else:
        print(f"✅ 使用 Kimi API: {args.api_key[:10]}...")
    
    print(f"\n{'='*60}")
    print(f"🌍 AnotherYou - 多进程AI观测系统")
    print(f"{'='*60}")
    print(f"AI数量: {len(args.names)}")
    print(f"AI列表: {', '.join(args.names)}")
    print(f"Web面板: http://localhost:{args.web_port}")
    print(f"{'='*60}\n")
    
    # 启动Web服务器（后台线程）
    web_thread = threading.Thread(target=start_web_server, args=(args.web_port,), daemon=True)
    web_thread.start()
    
    # 启动AI进程
    world_state["is_running"].value = True
    processes = []
    
    for name in args.names:
        p = mp.Process(target=run_agent_process, args=(name, args.api_key, world_state))
        p.start()
        processes.append(p)
    
    print(f"✅ 启动了 {len(processes)} 个AI进程\n")
    
    try:
        # 等待所有进程
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n\n🛑 停止所有AI...")
        world_state["is_running"].value = False
        for p in processes:
            p.terminate()
            p.join()
    
    print("\n✅ 所有AI已停止")

if __name__ == "__main__":
    main()
