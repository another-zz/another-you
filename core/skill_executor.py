"""
Skill Executor - 技能执行引擎

Voyager风格的技能执行：
1. 代码生成
2. 执行验证
3. 错误反馈
4. 迭代优化
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Callable
from datetime import datetime


class SkillExecutor:
    """
    技能执行引擎
    
    执行Mineflayer JavaScript代码
    支持错误处理和迭代优化
    """
    
    def __init__(self, mc_host: str = "localhost", mc_port: int = 25565):
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.execution_history: List[Dict] = []
        
    def execute(self, code: str, skill_name: str = "unnamed", 
                timeout: int = 30) -> Dict:
        """
        执行技能代码
        
        Args:
            code: JavaScript代码
            skill_name: 技能名称
            timeout: 超时时间（秒）
            
        Returns:
            执行结果 {success: bool, output: str, error: str}
        """
        # 包装成完整可执行脚本
        full_code = self._wrap_code(code, skill_name)
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(full_code)
            temp_file = f.name
            
        try:
            # 执行Node.js
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            # 记录历史
            self.execution_history.append({
                "skill_name": skill_name,
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "output": output,
                "error": error
            })
            
            return {
                "success": success,
                "output": output,
                "error": error,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"执行超时（{timeout}秒）",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1
            }
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
                
    def _wrap_code(self, code: str, skill_name: str) -> str:
        """包装代码为可执行脚本"""
        return f'''
const mineflayer = require('mineflayer');
const {{ pathfinder, Movements, goals }} = require('mineflayer-pathfinder');

const bot = mineflayer.createBot({{
    host: '{self.mc_host}',
    port: {self.mc_port},
    username: 'SkillBot_{skill_name}',
}});

bot.loadPlugin(pathfinder);

// 用户代码
{code}

// 执行并退出
bot.on('spawn', async () => {{
    console.log('Bot spawned, executing skill...');
    try {{
        // 调用用户定义的函数
        if (typeof {skill_name.replace(' ', '_')} === 'function') {{
            await {skill_name.replace(' ', '_')}(bot);
        }} else {{
            console.log('Skill function not found');
        }}
        console.log('Skill execution completed');
    }} catch (err) {{
        console.error('Error:', err.message);
    }}
    
    // 等待后退出
    setTimeout(() => {{
        bot.quit();
        process.exit(0);
    }}, 2000);
}});

bot.on('error', (err) => {{
    console.error('Bot error:', err.message);
    process.exit(1);
}});

// 超时保护
setTimeout(() => {{
    console.log('Timeout, exiting...');
    bot.quit();
    process.exit(0);
}}, 25000);
'''
        
    def validate_code(self, code: str) -> List[str]:
        """
        验证代码语法
        
        Returns:
            错误列表（空表示无错误）
        """
        errors = []
        
        # 仅在非模拟模式下严格验证
        if "def " not in code and "function" not in code:
            errors.append("建议包含函数定义")
            
        return errors
        
    def get_execution_stats(self) -> Dict:
        """获取执行统计"""
        if not self.execution_history:
            return {"total": 0, "success_rate": 0}
            
        total = len(self.execution_history)
        success = len([e for e in self.execution_history if e["success"]])
        
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": success / total if total > 0 else 0
        }


class SkillLibrary:
    """
    技能库
    
    存储和管理可复用的技能
    """
    
    def __init__(self, library_dir: str = "data/skills"):
        self.library_dir = library_dir
        os.makedirs(library_dir, exist_ok=True)
        self.skills: Dict[str, Dict] = {}
        self._load()
        
    def _load(self):
        """加载已有技能"""
        for filename in os.listdir(self.library_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.library_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        skill = json.load(f)
                        self.skills[skill['name']] = skill
                except:
                    pass
                    
    def add_skill(self, name: str, code: str, description: str = "",
                  verified: bool = False):
        """添加技能到库"""
        skill = {
            "name": name,
            "code": code,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "verified": verified,
            "usage_count": 0,
            "success_rate": 0.0
        }
        
        self.skills[name] = skill
        self._save_skill(skill)
        
    def _save_skill(self, skill: Dict):
        """保存技能到文件"""
        filename = f"{skill['name'].replace(' ', '_')}.json"
        filepath = os.path.join(self.library_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(skill, f, indent=2, ensure_ascii=False)
            
    def get_skill(self, name: str) -> Optional[Dict]:
        """获取技能"""
        return self.skills.get(name)
        
    def find_similar(self, description: str, top_k: int = 3) -> List[Dict]:
        """
        查找相似技能（简化版：关键词匹配）
        
        实际应使用向量检索
        """
        desc_words = set(description.lower().split())
        scored = []
        
        for name, skill in self.skills.items():
            skill_words = set(skill.get('description', '').lower().split())
            skill_words.update(name.lower().split())
            
            # 计算重叠
            overlap = len(desc_words & skill_words)
            if overlap > 0:
                scored.append((overlap, skill))
                
        scored.sort(reverse=True)
        return [s for _, s in scored[:top_k]]
        
    def update_skill_stats(self, name: str, success: bool):
        """更新技能统计"""
        if name not in self.skills:
            return
            
        skill = self.skills[name]
        skill['usage_count'] += 1
        
        # 更新成功率
        alpha = 0.3
        current = skill.get('success_rate', 0.5)
        if success:
            skill['success_rate'] = current * (1 - alpha) + 1.0 * alpha
        else:
            skill['success_rate'] = current * (1 - alpha) + 0.0 * alpha
            
        self._save_skill(skill)
        
    def list_skills(self) -> List[str]:
        """列出所有技能"""
        return list(self.skills.keys())
