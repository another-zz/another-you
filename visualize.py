#!/usr/bin/env python3
"""
AnotherYou 可视化仪表板
无需Docker，直接在浏览器中查看
"""

import asyncio
import json
import os
import sys
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import Agent
from core.world_coordinator import WorldCoordinator
from core.social_network import SocialNetwork


# 全局状态存储
world_state = {
    "agents": {},
    "social_network": None,
    "world": None,
    "logs": [],
    "started_at": None
}


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_html()
        elif self.path == '/api/state':
            self.send_json(world_state)
        elif self.path.startswith('/static/'):
            self.send_static()
        else:
            self.send_error(404)
            
    def send_html(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
        
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))
        
    def send_static(self):
        self.send_error(404)
        
    def log_message(self, format, *args):
        pass  # 静默日志


DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnotherYou - AI世界可视化</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px 30px;
            border-bottom: 1px solid #2a2a3e;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 28px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header .status {
            color: #4ade80;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        @media (max-width: 900px) {
            .container { grid-template-columns: 1fr; }
        }
        
        .card {
            background: rgba(18, 18, 26, 0.8);
            border-radius: 16px;
            border: 1px solid #2a2a3e;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        
        .card-header {
            background: rgba(26, 26, 46, 0.8);
            padding: 15px 20px;
            border-bottom: 1px solid #2a2a3e;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-content {
            padding: 20px;
        }
        
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .agent-card {
            background: linear-gradient(135deg, #1a1a2e 0%, #252540 100%);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #3a3a5e;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .agent-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
        }
        
        .agent-name {
            font-size: 18px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .agent-stats {
            font-size: 12px;
            color: #888;
            line-height: 1.6;
        }
        
        .stat-bar {
            height: 6px;
            background: #2a2a3e;
            border-radius: 3px;
            margin: 5px 0;
            overflow: hidden;
        }
        
        .stat-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s;
        }
        
        .stat-bar-fill.energy { background: linear-gradient(90deg, #f59e0b, #4ade80); }
        .stat-bar-fill.health { background: linear-gradient(90deg, #ef4444, #4ade80); }
        
        .network-viz {
            height: 300px;
            position: relative;
            background: radial-gradient(circle at center, #1a1a2e 0%, #0a0a0f 100%);
            border-radius: 12px;
        }
        
        .node {
            position: absolute;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            transition: all 0.3s;
        }
        
        .node:hover {
            transform: scale(1.1);
        }
        
        .node.alice { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .node.bob { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .node.charlie { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        
        .log-container {
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
        }
        
        .log-entry {
            padding: 8px 12px;
            border-bottom: 1px solid #1a1a2e;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .log-time { color: #666; }
        .log-agent { color: #00d4ff; font-weight: bold; }
        .log-action { color: #e0e0e0; }
        .log-social { color: #f59e0b; }
        .log-trade { color: #4ade80; }
        
        .refresh-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        
        .empty-state .icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 AnotherYou - AI世界可视化</h1>
        <div class="status">
            <span class="refresh-indicator"></span>
            实时更新中 | 最后更新: <span id="lastUpdate">--:--:--</span>
        </div>
    </div>
    
    <div class="container">
        <!-- AI状态卡片 -->
        <div class="card">
            <div class="card-header">
                <span>🤖</span>
                <span>AI状态</span>
            </div>
            <div class="card-content">
                <div id="agentList" class="agent-grid">
                    <div class="empty-state">
                        <div class="icon">⏳</div>
                        <div>等待AI数据...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 社会网络 -->
        <div class="card">
            <div class="card-header">
                <span>🕸️</span>
                <span>社会网络</span>
            </div>
            <div class="card-content">
                <div id="networkViz" class="network-viz">
                    <div class="empty-state">
                        <div class="icon">🌐</div>
                        <div>社会网络加载中...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 实时日志 -->
        <div class="card" style="grid-column: 1 / -1;">
            <div class="card-header">
                <span>📝</span>
                <span>实时日志</span>
            </div>
            <div class="card-content">
                <div id="logContainer" class="log-container">
                    <div class="empty-state">
                        <div class="icon">📋</div>
                        <div>等待日志数据...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 状态数据
        let currentState = null;
        let logHistory = [];
        
        // 获取数据
        async function fetchState() {
            try {
                const response = await fetch('/api/state');
                currentState = await response.json();
                updateUI();
            } catch (e) {
                console.error('获取数据失败:', e);
            }
        }
        
        // 更新UI
        function updateUI() {
            if (!currentState) return;
            
            // 更新时间
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
            // 更新AI列表
            updateAgentList();
            
            // 更新网络图
            updateNetworkViz();
            
            // 更新日志
            updateLogs();
        }
        
        // 更新AI列表
        function updateAgentList() {
            const container = document.getElementById('agentList');
            const agents = currentState.agents || {};
            
            if (Object.keys(agents).length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="icon">⏳</div>
                        <div>等待AI数据...</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = Object.entries(agents).map(([name, data]) => `
                <div class="agent-card">
                    <div class="agent-name">${name}</div>
                    <div class="agent-stats">
                        <div>⚡ 能量: ${Math.round(data.energy)}%</div>
                        <div class="stat-bar">
                            <div class="stat-bar-fill energy" style="width: ${data.energy}%"></div>
                        </div>
                        <div>🎯 行动: ${data.total_actions || 0}</div>
                        <div>🧠 记忆: ${data.memory_count || 0}条</div>
                        <div>🎒 背包: ${Object.entries(data.inventory || {}).map(([k,v]) => `${k}:${v}`).join(', ') || '空'}</div>
                        ${data.social ? `
                        <div>👥 社交: ${data.social.friends}友/${data.social.enemies}敌</div>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        // 更新网络可视化
        function updateNetworkViz() {
            const container = document.getElementById('networkViz');
            const agents = currentState.agents || {};
            const agentNames = Object.keys(agents);
            
            if (agentNames.length === 0) return;
            
            // 简单的圆形布局
            const centerX = container.offsetWidth / 2;
            const centerY = container.offsetHeight / 2;
            const radius = Math.min(centerX, centerY) - 50;
            
            const nodes = agentNames.map((name, i) => {
                const angle = (i / agentNames.length) * 2 * Math.PI - Math.PI / 2;
                const x = centerX + radius * Math.cos(angle);
                const y = centerY + radius * Math.sin(angle);
                return { name, x, y };
            });
            
            container.innerHTML = nodes.map(n => `
                <div class="node ${n.name.toLowerCase()}" 
                     style="left: ${n.x - 30}px; top: ${n.y - 30}px;"
                     title="${n.name}">
                    ${n.name[0]}
                </div>
            `).join('');
        }
        
        // 更新日志
        function updateLogs() {
            const container = document.getElementById('logContainer');
            const logs = currentState.logs || [];
            
            if (logs.length === 0) return;
            
            // 只显示最新的20条
            const recentLogs = logs.slice(-20);
            
            container.innerHTML = recentLogs.map(log => `
                <div class="log-entry">
                    <span class="log-time">${log.time}</span>
                    <span class="log-agent">[${log.agent}]</span>
                    <span class="log-${log.type || 'action'}">${log.message}</span>
                </div>
            `).join('');
            
            // 自动滚动到底部
            container.scrollTop = container.scrollHeight;
        }
        
        // 定期刷新
        fetchState();
        setInterval(fetchState, 1000);
    </script>
</body>
</html>
'''


def start_dashboard_server(port=8080):
    """启动仪表板服务器"""
    server = HTTPServer(('localhost', port), DashboardHandler)
    print(f"🌐 可视化面板已启动: http://localhost:{port}")
    webbrowser.open(f'http://localhost:{port}')
    server.serve_forever()


async def run_simulation():
    """运行模拟并更新状态"""
    global world_state
    
    print("="*60)
    print("🌍 AnotherYou 可视化模拟")
    print("="*60)
    
    # 创建组件
    social = SocialNetwork()
    world = WorldCoordinator(world_name='可视化世界')
    
    world_state["social_network"] = social
    world_state["world"] = world
    world_state["started_at"] = datetime.now().isoformat()
    
    # 创建AI
    agents = []
    for name in ['Alice', 'Bob', 'Charlie']:
        agent = Agent(
            player_name=name,
            coordinator=world,
            social_network=social
        )
        agents.append(agent)
        agent.is_running = True
        
        # 初始化状态
        world_state["agents"][name] = {
            "name": name,
            "energy": 100,
            "total_actions": 0,
            "inventory": {},
            "memory_count": 0
        }
        
    print(f"\n✅ 创建了 {len(agents)} 个AI")
    print(f"🌐 打开 http://localhost:8080 查看可视化\n")
    
    # 模拟运行
    tick = 0
    while tick < 100:  # 运行100个tick
        tick += 1
        
        for agent in agents:
            # 执行一个tick
            await agent._life_tick()
            
            # 更新状态
            status = agent.get_status()
            world_state["agents"][agent.player_name] = {
                "name": agent.player_name,
                "energy": status["energy"],
                "total_actions": status["total_actions"],
                "inventory": status["inventory"],
                "memory_count": int(status["memory_summary"].split("总计")[1].split("条")[0]) if "总计" in status["memory_summary"] else 0,
                "social": status.get("social", {})
            }
            
            # 添加日志
            world_state["logs"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "agent": agent.player_name,
                "message": f"执行了行动 #{agent.total_actions}",
                "type": "action"
            })
            
        # 社交事件日志
        if tick % 5 == 0:
            for event in social.social_events[-3:]:
                world_state["logs"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "agent": "系统",
                    "message": f"{event.get('type', 'event')}: {event.get('agent_a', '')} - {event.get('agent_b', '')}",
                    "type": "social"
                })
        
        # 限制日志数量
        if len(world_state["logs"]) > 100:
            world_state["logs"] = world_state["logs"][-50:]
            
        await asyncio.sleep(0.5)  # 每0.5秒一个tick
    
    # 停止
    for agent in agents:
        await agent.stop()
        
    print("\n✅ 模拟完成")


async def main():
    """主函数"""
    # 启动服务器（在后台线程）
    server_thread = threading.Thread(target=start_dashboard_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    await asyncio.sleep(1)
    
    # 运行模拟
    await run_simulation()
    
    print("\n按 Ctrl+C 退出")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 再见")


if __name__ == "__main__":
    asyncio.run(main())
