# 全编程语言代码知识图谱系统

基于第一性原理设计的代码智能分析工具，支持任意编程语言的代码结构理解、知识图谱可视化和智能问答。

## 功能特性

- 多语言支持 (Python, JavaScript/TypeScript, Go, 等)
- 增量更新机制
- 知识图谱可视化
- 智能搜索功能
- AI 代码问答 (集成硅基流动 LLM)

## 技术栈

**后端:**
- Python 3.11+
- FastAPI
- SQLite
- Watchdog

**前端:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- D3.js (图谱可视化)

## 快速开始

### 后端运行

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 前端运行

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
/workspace
├── backend/
│   ├── main.py          # FastAPI 入口
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库操作
│   ├── parsers/         # 语言解析器
│   ├── services/        # 核心服务
│   └── routers/         # API 路由
├── frontend/            # React 前端
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api/
│   └── package.json
└── requirements.txt
```
