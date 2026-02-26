"""
Mineflayer Bridge - Python与Mineflayer的WebSocket桥接
"""

import asyncio
import json
import subprocess
import websockets
from typing import Dict, Callable, Optional

class MineflayerBridge:
    """Mineflayer桥接器 - 通过WebSocket控制Minecraft bot"""
    
    def __init__(self, host: str = "localhost", port: int = 25565, 
                 bridge_port: int = 8765):
        self.mc_host = host
        self.mc_port = port
        self.bridge_port = bridge_port
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        
        # 回调函数
        self.on_message: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Node.js进程
        self.node_process: Optional[subprocess.Popen] = None
        
    async def start(self):
        """启动桥接"""
        # 1. 启动Node.js桥接服务器
        await self._start_node_bridge()
        
        # 2. 等待并连接WebSocket
        await asyncio.sleep(2)  # 等待Node启动
        await self._connect_websocket()
        
    async def _start_node_bridge(self):
        """启动Node.js桥接服务"""
        bridge_code = f'''
const mineflayer = require('mineflayer');
const WebSocket = require('ws');

const wss = new WebSocket.Server({{ port: {self.bridge_port} }});

wss.on('connection', (ws) => {{
    console.log('Python connected');
    
    // 创建Mineflayer bot
    const bot = mineflayer.createBot({{
        host: '{self.mc_host}',
        port: {self.mc_port},
        username: 'AnotherYou_AI',
    }});
    
    bot.on('spawn', () => {{
        console.log('Bot spawned');
        ws.send(JSON.stringify({{ type: 'spawn', message: 'Bot ready' }}));
    }});
    
    bot.on('chat', (username, message) => {{
        ws.send(JSON.stringify({{ type: 'chat', username, message }}));
    }});
    
    bot.on('death', () => {{
        ws.send(JSON.stringify({{ type: 'death' }}));
    }});
    
    // 处理来自Python的命令
    ws.on('message', async (data) => {{
        const cmd = JSON.parse(data);
        
        try {{
            switch(cmd.type) {{
                case 'move':
                    await bot.pathfinder.goto(new bot.pathfinder.goals.GoalBlock(cmd.x, cmd.y, cmd.z));
                    ws.send(JSON.stringify({{ type: 'done', action: 'move' }}));
                    break;
                    
                case 'dig':
                    const block = bot.blockAt(bot.entity.position.offset(cmd.x, cmd.y, cmd.z));
                    if (block) {{
                        await bot.dig(block);
                        ws.send(JSON.stringify({{ type: 'done', action: 'dig', block: block.name }}));
                    }}
                    break;
                    
                case 'place':
                    const referenceBlock = bot.blockAt(bot.entity.position.offset(0, -1, 0));
                    await bot.placeBlock(referenceBlock, new Vec3(cmd.x, cmd.y, cmd.z));
                    ws.send(JSON.stringify({{ type: 'done', action: 'place' }}));
                    break;
                    
                case 'craft':
                    const item = bot.registry.itemsByName[cmd.item];
                    const recipe = bot.recipesFor(item.id, null, 1, null)[0];
                    if (recipe) {{
                        await bot.craft(recipe, cmd.count);
                        ws.send(JSON.stringify({{ type: 'done', action: 'craft', item: cmd.item }}));
                    }}
                    break;
                    
                case 'look':
                    await bot.look(cmd.yaw, cmd.pitch);
                    ws.send(JSON.stringify({{ type: 'done', action: 'look' }}));
                    break;
                    
                case 'get_state':
                    ws.send(JSON.stringify({{
                        type: 'state',
                        position: bot.entity.position,
                        health: bot.health,
                        food: bot.food,
                        inventory: bot.inventory.items(),
                    }}));
                    break;
                    
                default:
                    ws.send(JSON.stringify({{ type: 'error', message: 'Unknown command' }}));
            }}
        }} catch (err) {{
            ws.send(JSON.stringify({{ type: 'error', message: err.message }}));
        }}
    }});
    
    ws.on('close', () => {{
        console.log('Python disconnected');
        bot.quit();
    }});
}});

console.log('Bridge server started on port {self.bridge_port}');
'''
        
        # 保存临时文件
        with open('/tmp/mineflayer_bridge.js', 'w') as f:
            f.write(bridge_code)
            
        # 启动Node进程
        self.node_process = subprocess.Popen(
            ['node', '/tmp/mineflayer_bridge.js'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        print(f"[Bridge] Node.js bridge started on port {self.bridge_port}")
        
    async def _connect_websocket(self):
        """连接WebSocket"""
        try:
            uri = f"ws://localhost:{self.bridge_port}"
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            print("[Bridge] WebSocket connected")
            
            # 启动消息接收循环
            asyncio.create_task(self._receive_loop())
            
        except Exception as e:
            print(f"[Bridge] Connection failed: {e}")
            self.is_connected = False
            
    async def _receive_loop(self):
        """接收消息循环"""
        while self.is_connected and self.websocket:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if self.on_message:
                    self.on_message(data)
                    
            except websockets.exceptions.ConnectionClosed:
                print("[Bridge] Connection closed")
                self.is_connected = False
                break
            except Exception as e:
                print(f"[Bridge] Receive error: {e}")
                
    async def send_command(self, command: Dict) -> bool:
        """发送命令到Mineflayer"""
        if not self.is_connected or not self.websocket:
            return False
            
        try:
            await self.websocket.send(json.dumps(command))
            return True
        except Exception as e:
            print(f"[Bridge] Send error: {e}")
            return False
            
    async def get_state(self) -> Optional[Dict]:
        """获取当前状态"""
        if await self.send_command({"type": "get_state"}):
            # 等待响应（简化版）
            await asyncio.sleep(0.5)
            return {"status": "pending"}
        return None
        
    async def move_to(self, x: int, y: int, z: int):
        """移动到指定位置"""
        return await self.send_command({
            "type": "move",
            "x": x, "y": y, "z": z
        })
        
    async def dig_block(self, x: int, y: int, z: int):
        """挖掘方块"""
        return await self.send_command({
            "type": "dig",
            "x": x, "y": y, "z": z
        })
        
    async def stop(self):
        """停止桥接"""
        self.is_connected = False
        
        if self.websocket:
            await self.websocket.close()
            
        if self.node_process:
            self.node_process.terminate()
            self.node_process.wait()
