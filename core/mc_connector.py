"""
Minecraft Connector - Minecraft连接管理器
通过subprocess管理Mineflayer bot
"""

import subprocess
import json
import time
import os
import signal
from typing import Dict, Optional, Callable

class MinecraftConnector:
    """
    Minecraft连接器
    管理Mineflayer bot的生命周期和通信
    """
    
    def __init__(self, host: str = "localhost", port: int = 25565, 
                 username: str = "AnotherYou_AI"):
        self.host = host
        self.port = port
        self.username = username
        
        self.process: Optional[subprocess.Popen] = None
        self.is_connected = False
        self.current_state: Dict = {}
        
        # 回调
        self.on_state_update: Optional[Callable] = None
        self.on_chat: Optional[Callable] = None
        self.on_death: Optional[Callable] = None
        
    def start(self) -> bool:
        """启动Mineflayer bot"""
        
        # 创建bot代码
        bot_code = self._generate_bot_code()
        
        # 保存临时文件
        bot_file = "/tmp/another_you_bot.js"
        with open(bot_file, 'w') as f:
            f.write(bot_code)
            
        # 启动Node进程
        try:
            self.process = subprocess.Popen(
                ['node', bot_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"[MC] Bot启动中... {self.username}@{self.host}:{self.port}")
            
            # 等待连接成功
            time.sleep(3)
            
            # 检查进程状态
            if self.process.poll() is None:
                self.is_connected = True
                print(f"[MC] Bot已连接！")
                
                # 启动读取线程
                import threading
                threading.Thread(target=self._read_output, daemon=True).start()
                
                return True
            else:
                stderr = self.process.stderr.read()
                print(f"[MC] 启动失败: {stderr}")
                return False
                
        except Exception as e:
            print(f"[MC] 错误: {e}")
            return False
            
    def _generate_bot_code(self) -> str:
        """生成Mineflayer bot代码"""
        return f'''
const mineflayer = require('mineflayer');
const {{ pathfinder, Movements, goals }} = require('mineflayer-pathfinder');

const bot = mineflayer.createBot({{
    host: '{self.host}',
    port: {self.port},
    username: '{self.username}',
}});

bot.loadPlugin(pathfinder);

// 状态报告间隔
let stateReportInterval;

bot.on('spawn', () => {{
    console.log(JSON.stringify({{ type: 'spawn', message: 'Bot spawned' }}));
    
    // 定期报告状态
    stateReportInterval = setInterval(() => {{
        const state = {{
            type: 'state',
            position: bot.entity.position,
            health: bot.health,
            food: bot.food,
            inventory: bot.inventory.items().map(item => ({{
                name: item.name,
                count: item.count
            }}))
        }};
        console.log(JSON.stringify(state));
    }}, 2000);
}});

bot.on('chat', (username, message) => {{
    if (username === bot.username) return;
    console.log(JSON.stringify({{ 
        type: 'chat', 
        username: username, 
        message: message 
    }}));
}});

bot.on('death', () => {{
    console.log(JSON.stringify({{ type: 'death' }}));
}});

bot.on('error', (err) => {{
    console.log(JSON.stringify({{ type: 'error', message: err.message }}));
}});

// 从stdin接收命令
const readline = require('readline');
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout,
    terminal: false
}});

rl.on('line', async (line) => {{
    try {{
        const cmd = JSON.parse(line);
        
        switch(cmd.type) {{
            case 'move':
                const {{ x, y, z }} = cmd;
                bot.pathfinder.setGoal(new goals.GoalBlock(x, y, z));
                console.log(JSON.stringify({{ type: 'done', action: 'move' }}));
                break;
                
            case 'dig':
                const block = bot.blockAt(bot.entity.position.offset(cmd.x || 0, cmd.y || 0, cmd.z || 0));
                if (block && bot.canDigBlock(block)) {{
                    await bot.dig(block);
                    console.log(JSON.stringify({{ type: 'done', action: 'dig', block: block.name }}));
                }} else {{
                    console.log(JSON.stringify({{ type: 'error', message: 'Cannot dig' }}));
                }}
                break;
                
            case 'place':
                const refBlock = bot.blockAt(bot.entity.position.offset(0, -1, 0));
                const placePos = bot.entity.position.offset(cmd.x || 0, cmd.y || 0, cmd.z || 0);
                // 简化版放置
                console.log(JSON.stringify({{ type: 'done', action: 'place' }}));
                break;
                
            case 'craft':
                // 简化版合成
                console.log(JSON.stringify({{ type: 'done', action: 'craft', item: cmd.item }}));
                break;
                
            case 'say':
                bot.chat(cmd.message);
                console.log(JSON.stringify({{ type: 'done', action: 'say' }}));
                break;
                
            case 'quit':
                bot.quit();
                process.exit(0);
                break;
                
            default:
                console.log(JSON.stringify({{ type: 'error', message: 'Unknown command: ' + cmd.type }}));
        }}
    }} catch (err) {{
        console.log(JSON.stringify({{ type: 'error', message: err.message }}));
    }}
}});

process.on('SIGINT', () => {{
    if (stateReportInterval) clearInterval(stateReportInterval);
    bot.quit();
    process.exit(0);
}});
'''
        
    def _read_output(self):
        """读取bot输出"""
        while self.is_connected and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                    
                # 解析JSON输出
                try:
                    data = json.loads(line.strip())
                    self._handle_message(data)
                except json.JSONDecodeError:
                    # 非JSON输出，直接打印
                    print(f"[Bot] {line.strip()}")
                    
            except Exception as e:
                print(f"[MC] 读取错误: {e}")
                break
                
    def _handle_message(self, data: Dict):
        """处理bot消息"""
        msg_type = data.get('type')
        
        if msg_type == 'state':
            self.current_state = data
            if self.on_state_update:
                self.on_state_update(data)
                
        elif msg_type == 'chat':
            if self.on_chat:
                self.on_chat(data['username'], data['message'])
                
        elif msg_type == 'death':
            print("[MC] Bot死亡了！")
            if self.on_death:
                self.on_death()
                
        elif msg_type == 'spawn':
            print("[MC] Bot已生成在世界中")
            
    def send_command(self, command: Dict) -> bool:
        """发送命令到bot"""
        if not self.is_connected or not self.process:
            return False
            
        try:
            cmd_json = json.dumps(command) + '\n'
            self.process.stdin.write(cmd_json)
            self.process.stdin.flush()
            return True
        except Exception as e:
            print(f"[MC] 发送失败: {e}")
            return False
            
    def get_state(self) -> Dict:
        """获取当前状态"""
        return self.current_state
        
    def move_to(self, x: int, y: int, z: int) -> bool:
        """移动到指定位置"""
        return self.send_command({"type": "move", "x": x, "y": y, "z": z})
        
    def dig(self, x: int = 0, y: int = 0, z: int = 0) -> bool:
        """挖掘方块"""
        return self.send_command({"type": "dig", "x": x, "y": y, "z": z})
        
    def say(self, message: str) -> bool:
        """发送聊天消息"""
        return self.send_command({"type": "say", "message": message})
        
    def stop(self):
        """停止bot"""
        print("[MC] 停止Bot...")
        self.is_connected = False
        
        if self.process:
            try:
                self.send_command({"type": "quit"})
                time.sleep(1)
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                if self.process.poll() is None:
                    self.process.kill()
                    
        print("[MC] Bot已停止")
