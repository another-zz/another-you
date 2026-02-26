"""
Skill Code Generator - 技能代码生成器
AI描述任务 → LLM生成Mineflayer代码 → 执行
"""

import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime

class SkillCodeGenerator:
    """
    技能代码生成器
    将自然语言任务转换为可执行代码
    """
    
    def __init__(self, skills_dir: str = "data/skills"):
        self.skills_dir = skills_dir
        os.makedirs(skills_dir, exist_ok=True)
        
        # 已生成的技能
        self.generated_skills: Dict[str, Dict] = {}
        self._load_existing()
        
    def _load_existing(self):
        """加载已有技能"""
        for filename in os.listdir(self.skills_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.skills_dir, filename), 'r') as f:
                    skill = json.load(f)
                    self.generated_skills[skill['name']] = skill
                    
    def generate_skill(self, task_description: str, llm_client=None) -> Dict:
        """
        生成技能代码
        
        Args:
            task_description: 任务描述，如"砍树并收集木头"
            llm_client: LLM客户端（可选）
            
        Returns:
            技能定义，包含代码
        """
        # 检查是否已存在
        skill_name = self._extract_skill_name(task_description)
        if skill_name in self.generated_skills:
            return self.generated_skills[skill_name]
            
        # 生成代码（使用LLM或模板）
        if llm_client:
            code = self._generate_with_llm(task_description, llm_client)
        else:
            code = self._generate_with_template(task_description)
            
        # 创建技能定义
        skill = {
            "name": skill_name,
            "description": task_description,
            "code": code,
            "language": "javascript",
            "generated_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_rate": 1.0,
            "verified": False,
        }
        
        # 保存
        self._save_skill(skill)
        self.generated_skills[skill_name] = skill
        
        return skill
        
    def _extract_skill_name(self, description: str) -> str:
        """从描述提取技能名"""
        # 简化处理
        name = description.replace(" ", "_").replace("，", "_").replace("。", "")[:30]
        return name.lower()
        
    def _generate_with_template(self, task: str) -> str:
        """使用模板生成代码"""
        
        # 任务匹配模板
        templates = {
            "砍树": '''async function chopTree(bot, times = 5) {
    const mcData = require('minecraft-data')(bot.version);
    for (let i = 0; i < times; i++) {
        const tree = bot.findBlock({
            matching: block => block.name.includes('log'),
            maxDistance: 32
        });
        if (tree) {
            await bot.pathfinder.goto(new goals.GoalBlock(tree.position.x, tree.position.y, tree.position.z));
            await bot.dig(tree);
            bot.chat("砍了一棵树！");
        }
    }
}''',
            "挖矿": '''async function mineStone(bot, times = 10) {
    for (let i = 0; i < times; i++) {
        const stone = bot.findBlock({
            matching: block => block.name === 'stone',
            maxDistance: 16
        });
        if (stone) {
            await bot.dig(stone);
        }
    }
}''',
            "建造": '''async function buildHouse(bot) {
    const size = 5;
    const startPos = bot.entity.position.clone();
    
    // 建造地板
    for (let x = 0; x < size; x++) {
        for (let z = 0; z < size; z++) {
            const pos = startPos.offset(x, 0, z);
            const block = bot.blockAt(pos);
            if (block && block.name === 'air') {
                // 放置木板
            }
        }
    }
    bot.chat("房子建好了！");
}''',
            "合成": '''async function craftItem(bot, itemName, count = 1) {
    const mcData = require('minecraft-data')(bot.version);
    const item = mcData.itemsByName[itemName];
    if (!item) {
        bot.chat("不知道这个物品");
        return;
    }
    
    const recipe = bot.recipesFor(item.id, null, 1, null)[0];
    if (recipe) {
        await bot.craft(recipe, count);
        bot.chat(`合成了${count}个${itemName}`);
    } else {
        bot.chat("缺少材料");
    }
}''',
        }
        
        # 匹配关键词
        for keyword, code in templates.items():
            if keyword in task:
                return code
                
        # 默认代码
        return f'''async function customTask(bot) {{
    bot.chat("开始执行任务: {task}");
    // TODO: 实现具体逻辑
    await bot.waitForTicks(20);
}}'''
        
    def _generate_with_llm(self, task: str, llm_client) -> str:
        """使用LLM生成代码"""
        # 预留接口
        prompt = f"""生成Mineflayer JavaScript代码来实现以下任务：
{task}

要求：
1. 使用async/await
2. 包含错误处理
3. 添加聊天反馈
4. 代码要完整可运行

只输出代码，不要解释。"""

        # 调用LLM
        # code = llm_client.generate(prompt)
        
        # 暂时使用模板
        return self._generate_with_template(task)
        
    def _save_skill(self, skill: Dict):
        """保存技能"""
        filename = f"{skill['name']}.json"
        filepath = os.path.join(self.skills_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(skill, f, indent=2, ensure_ascii=False)
            
    def get_skill_code(self, skill_name: str) -> Optional[str]:
        """获取技能代码"""
        if skill_name in self.generated_skills:
            skill = self.generated_skills[skill_name]
            return skill['code']
        return None
        
    def execute_skill(self, skill_name: str, mc_connector, **kwargs) -> bool:
        """
        执行技能
        
        实际实现需要将代码发送到Node.js执行
        简化版：发送命令序列
        """
        code = self.get_skill_code(skill_name)
        if not code:
            return False
            
        # 更新使用统计
        self.generated_skills[skill_name]['usage_count'] += 1
        self._save_skill(self.generated_skills[skill_name])
        
        # 发送执行命令（简化版）
        # 实际应该将代码写入临时文件并执行
        return True
        
    def list_skills(self) -> List[str]:
        """列出所有技能"""
        return list(self.generated_skills.keys())
        
    def verify_skill(self, skill_name: str, success: bool):
        """验证技能执行结果"""
        if skill_name not in self.generated_skills:
            return
            
        skill = self.generated_skills[skill_name]
        skill['verified'] = True
        
        # 更新成功率
        alpha = 0.3
        if success:
            skill['success_rate'] = skill['success_rate'] * (1 - alpha) + 1.0 * alpha
        else:
            skill['success_rate'] = skill['success_rate'] * (1 - alpha) + 0.0 * alpha
            
        self._save_skill(skill)
