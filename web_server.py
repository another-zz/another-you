#!/usr/bin/env python3
"""
AnotherYou Web Dashboard Server
提供实时数据API供前端调用
"""

import json
import os
import sys
import asyncio
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 全局状态存储
world_state = {
    "agents": {},
    "logs": [],
    "is_running": False,
    "last_update": None
}

def get_mock_data():
    """获取模拟数据（当没有真实AI运行时）"""
    return {
        "agents": {
            "Alice": {
                "name": "Alice",
                "age_minutes": 12,
                "energy": 85,
                "total_actions": 156,
                "inventory": {"wood": 5, "stone": 3},
                "skills": ["explore", "gather_wood"],
                "current_plan": "探索周围环境，收集资源",
                "memory_count": 15,
                "social": {"friends": 1, "enemies": 0, "reputation": 52}
            },
            "Bob": {
                "name": "Bob",
                "age_minutes": 10,
                "energy": 92,
                "total_actions": 134,
                "inventory": {"wood": 8, "stone": 5},
                "skills": ["explore", "gather_stone"],
                "current_plan": "收集石头，建造庇护所",
                "memory_count": 12,
                "social": {"friends": 1, "enemies": 0, "reputation": 48}
            },
            "Charlie": {
                "name": "Charlie",
                "age_minutes": 8,
                "energy": 78,
                "total_actions": 98,
                "inventory": {"wood": 3},
                "skills": ["explore", "socialize"],
                "current_plan": "社交互动，建立关系",
                "memory_count": 10,
                "social": {"friends": 2, "enemies": 0, "reputation": 55}
            }
        },
        "logs": [
            {"time": "14:32:15", "agent": "Alice", "message": "探索了周围环境", "type": "action"},
            {"time": "14:31:42", "agent": "Bob", "message": "收集了5个木头", "type": "action"},
            {"time": "14:30:08", "agent": "Charlie", "message": "认识了 Alice", "type": "social"},
            {"time": "14:29:30", "agent": "Alice", "message": "反思: 最近我主要在探索这个世界", "type": "reflection"},
            {"time": "14:28:15", "agent": "Bob", "message": "与 Alice 交易: 5木头→3石头", "type": "trade"}
        ]
    }

class APIHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/state':
            self.serve_api()
        else:
            self.send_error(404)
            
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
            
    def serve_html(self):
        """提供前端页面"""
        try:
            with open('ui/web/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
            
    def serve_api(self):
        """提供API数据"""
        # 使用全局状态或模拟数据
        data = world_state if world_state.get("agents") else get_mock_data()
        data["last_update"] = datetime.now().isoformat()
        data["is_running"] = world_state.get("is_running", False)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))
        
    def log_message(self, format, *args):
        """静默日志"""
        pass

def start_server(port=8080):
    """启动服务器"""
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🌐 Web Dashboard: http://localhost:{port}")
    print(f"📊 API Endpoint: http://localhost:{port}/api/state")
    server.serve_forever()

def update_world_state(agents_data, logs_data, is_running=True):
    """更新世界状态（供外部调用）"""
    world_state["agents"] = agents_data
    world_state["logs"] = logs_data
    world_state["is_running"] = is_running
    world_state["last_update"] = datetime.now().isoformat()

if __name__ == '__main__':
    start_server()
