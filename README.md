# AnotherYou v1.0

**另一个你，重启你的人生**

**你想让你的人生，重新开始吗？**

[![Stars](https://img.shields.io/github/stars/another-zz/another-you?style=social)](https://github.com/another-zz/another-you)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个由**AI自主推动世界发展**的Minecraft持久虚拟世界。

每个玩家拥有一个专属AI数字分身。即使你完全离线，它也会24/7在Minecraft中自主思考、挖矿、建造、社交、交易，并与其他AI一起形成村庄、经济和社会。

这是**你的第二个人生** —— 由AI为你持续书写。

---

## ✨ 核心特性

- **持久数字分身**: 24/7在线，自主生活
- **终身学习**: 自动生成技能代码，不断进化
- **多AI协作**: 多个AI在同一个世界互动、交易、形成社会
- **经济系统**: 资源价值、自动交易、市场动态
- **真实Minecraft**: 连接真实MC服务器，物理交互

## 🚀 快速开始

### 单AI模式

```bash
# 启动你的AI分身
python start.py --name="小明"
```

### 多AI世界模式

```bash
# 启动3个AI在同一个世界互动
python multi_agent.py --names Alice Bob Charlie

# 或更多AI
python multi_agent.py --names AI_1 AI_2 AI_3 AI_4 AI_5
```

### 连接真实Minecraft

```bash
# 1. 启动MC服务器
docker-compose up -d minecraft

# 2. 安装Node依赖
npm install mineflayer mineflayer-pathfinder

# 3. 启动AI连接MC
python start.py --name="小明" --host=localhost --port=25565
```

## 📊 版本历史

| 版本 | 特性 |
|------|------|
| v0.1 | 基础AI生命循环 |
| v0.2 | 技能库 + 自动课程 |
| v0.3 | LLM大脑 + 向量记忆 |
| v0.4 | 真实Minecraft连接 |
| v0.5 | 技能代码生成 |
| v0.6 | 多AI协作 |
| v0.7 | 经济系统 |
| v0.8 | 完整社会演化 |
| v0.9 | 多AI启动器 |
| v1.0 | 完整版发布 |

## 🏗️ 项目结构

```
another-you/
├── core/
│   ├── agent_v8.py          # 完整AI主体
│   ├── llm_brain.py         # LLM大脑
│   ├── vector_memory.py     # 向量记忆
│   ├── mc_connector.py      # MC连接
│   ├── skill_generator.py   # 技能生成
│   ├── world_coordinator.py # 世界协调
│   └── economy.py           # 经济系统
├── start.py                 # 单AI启动
├── multi_agent.py           # 多AI启动
└── docker-compose.yml       # MC服务器
```

## 🎮 使用示例

### 观察AI自主行为

```bash
$ python start.py --name="小明"

============================================================
🌟 「另一个你」v0.8 完整版
   玩家: 小明
   能力: 学习 | 协作 | 交易 | 演化
============================================================

[系统] ✅ 已连接Minecraft

[小明] 砍树
  📝 生成新技能: 砍树
  ✅ 技能已生成！

[社交] 小明 认识了 小红
[交易] 小明 <-> 小红: stone <-> wood

📊 小明
   存活: 15.3分钟 | 财富: 125
   朋友: 2 | 声望: 55
   背包: {'wood': 25, 'stone': 10}
```

## 📄 许可证

MIT License
