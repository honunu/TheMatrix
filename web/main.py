"""The Matrix Web API - FastAPI 后端"""
import sys
import json
import asyncio
import threading
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import yaml

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(title="The Matrix Web UI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# 全局状态
class MatrixState:
    """Matrix 系统状态"""
    def __init__(self):
        self.agents = {}
        self.tasks = []
        self.logs = []
        self.config = {}
        self.matrix_instance = None
        self._lock = threading.Lock()

    def update_agent_status(self, name: str, status: str, current_task: str = ""):
        with self._lock:
            self.agents[name] = {
                "name": name,
                "status": status,
                "current_task": current_task,
                "last_update": datetime.now().isoformat()
            }

    def add_log(self, level: str, message: str, agent: str = ""):
        with self._lock:
            self.logs.insert(0, {
                "time": datetime.now().isoformat(),
                "level": level,
                "agent": agent,
                "message": message
            })
            # 只保留最近500条
            if len(self.logs) > 500:
                self.logs = self.logs[:500]

    def add_task(self, task_id: str, content: str, status: str = "pending"):
        with self._lock:
            self.tasks.insert(0, {
                "id": task_id,
                "content": content,
                "status": status,
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
                "result": ""
            })

    def update_task(self, task_id: str, status: str = None, result: str = None):
        with self._lock:
            for task in self.tasks:
                if task["id"] == task_id:
                    if status:
                        task["status"] = status
                    if result is not None:
                        task["result"] = result
                    if status == "completed":
                        task["completed_at"] = datetime.now().isoformat()
                    break

    def load_config(self):
        config_path = project_root / "config" / "settings.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        return self.config

    def save_config(self, new_config: dict):
        config_path = project_root / "config" / "settings.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(new_config, f, allow_unicode=True)
        self.config = new_config

state = MatrixState()

# 数据库初始化
DB_PATH = Path(__file__).parent / "chat_history.db"

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_message(role: str, content: str):
    """保存对话消息"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_history(limit: int = 100):
    """获取对话历史"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "SELECT role, content, created_at FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]

def clear_history():
    """清空对话历史"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

def extract_final_answer(text: str) -> str:
    """从完整输出中提取关键结果"""
    if not text:
        return ""
    
    lines = text.strip().split('\n')
    
    # 移除空行
    lines = [l.strip() for l in lines if l.strip()]
    
    if not lines:
        return ""
    
    # 如果输出很长，只取最后 500 字
    if len(text) > 500:
        return text[-500:]
    
    return text

# 初始化数据库
init_db()

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# 初始化 TheMatrix
def init_matrix():
    """初始化 TheMatrix 实例"""
    from the_matrix import TheMatrix
    try:
        state.matrix_instance = TheMatrix()
        state.add_log("info", "TheMatrix 系统已启动")
        
        # 初始化 Agent 状态 (暂不使用 Smith)
        for name in ["Architect", "Morpheus", "Oracle", "Neo", "Trinity", "Cypher"]:
            state.update_agent_status(name, "idle")
        
        return True
    except Exception as e:
        state.add_log("error", f"初始化失败: {str(e)}")
        return False

# API 路由
@app.get("/")
async def root():
    """返回前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse(str(Path(__file__).parent / "static" / "index.html"))

@app.get("/api/config")
async def get_config():
    """获取配置"""
    config = state.load_config()
    # 隐藏敏感信息
    if "api_key" in config.get("llm", {}):
        config["llm"]["api_key"] = "***" + config["llm"]["api_key"][-4:]
    return config

@app.post("/api/config")
async def update_config(config: dict):
    """更新配置"""
    # 获取原始配置，保留 api_key
    original = state.load_config()
    if "api_key" in config.get("llm", {}):
        if config["llm"]["api_key"].startswith("***"):
            config["llm"]["api_key"] = original["llm"]["api_key"]
    
    state.save_config(config)
    state.add_log("info", "配置已更新", "System")
    return {"status": "ok", "message": "配置已更新"}

@app.get("/api/agents")
async def get_agents():
    """获取所有 Agent 状态"""
    return state.agents

@app.get("/api/tasks")
async def get_tasks():
    """获取任务列表"""
    return state.tasks

@app.post("/api/tasks")
async def create_task(task: dict):
    """创建新任务"""
    import uuid
    task_id = str(uuid.uuid4())[:8]
    content = task.get("content", "")
    
    state.add_task(task_id, content, "running")
    state.add_log("info", f"新任务: {content[:50]}...", "System")
    
    # 在后台执行任务
    def run_task():
        try:
            if state.matrix_instance is None:
                init_matrix()
            
            # 更新 Agent 状态
            state.update_agent_status("Architect", "processing", content)
            
            result = state.matrix_instance.run(content)
            
            state.update_task(task_id, "completed", result)
            state.update_agent_status("Architect", "idle")
            state.add_log("info", f"任务完成: {content[:30]}...", "Architect")
            
            # 广播更新
            asyncio.run(manager.broadcast({
                "type": "task_update",
                "task_id": task_id,
                "status": "completed"
            }))
            
        except Exception as e:
            state.update_task(task_id, "failed", str(e))
            state.update_agent_status("Architect", "idle")
            state.add_log("error", f"任务失败: {str(e)}")
    
    thread = threading.Thread(target=run_task)
    thread.start()
    
    return {"task_id": task_id, "status": "running"}

@app.post("/api/chat")
async def chat(message: dict):
    """对话接口 - 直接与 AI 对话"""
    content = message.get("content", "")
    if not content:
        return {"error": "内容不能为空"}
    
    # 保存用户消息
    save_message("user", content)
    state.add_log("info", f"对话: {content[:30]}...", "User")
    
    # 广播开始
    await manager.broadcast({
        "type": "agent_start",
        "agent": "Morpheus",
        "message": "正在理解用户意图..."
    })
    
    try:
        # 初始化 matrix 如果需要
        if state.matrix_instance is None:
            init_matrix()
        
        # 分阶段更新状态并广播
        stages = [
            ("Morpheus", "正在分析用户意图..."),
            ("Architect", "正在分解任务..."),
            ("Neo", "正在处理..."),
            ("Oracle", "正在评估结果..."),
        ]
        
        for agent_name, status_msg in stages:
            state.update_agent_status(agent_name, "processing", content)
            await manager.broadcast({
                "type": "agent_stage",
                "agent": agent_name,
                "message": status_msg
            })
            await asyncio.sleep(0.1)  # 短暂延迟让前端更新
        
        # 直接运行任务
        raw_result = state.matrix_instance.run(content)
        
        # 提取关键结果 - 只返回最后的总结部分
        result = extract_final_answer(raw_result)
        
        # 更新状态为空闲
        for name in ["Morpheus", "Architect", "Neo", "Oracle", "Trinity", "Cypher"]:
            state.update_agent_status(name, "idle")
        
        state.add_log("info", f"对话完成", "Morpheus")
        
        # 广播完成
        await manager.broadcast({
            "type": "agent_done",
            "message": "处理完成"
        })
        
        # 保存 AI 回复
        save_message("assistant", result)
        
        return {"content": result}
    
    except Exception as e:
        for name in ["Morpheus", "Architect", "Neo", "Oracle"]:
            state.update_agent_status(name, "idle")
        state.add_log("error", f"对话失败: {str(e)}")
        return {"error": str(e)}

@app.get("/api/chat/history")
async def get_chat_history(limit: int = 100):
    """获取对话历史"""
    history = get_history(limit)
    return list(reversed(history))  # 按时间正序

@app.delete("/api/chat/history")
async def clear_chat_history():
    """清空对话历史"""
    clear_history()
    return {"status": "ok"}

@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """获取执行日志"""
    return state.logs[:limit]

@app.get("/api/status")
async def get_status():
    """获取系统状态 - 精简版"""
    # 只返回必要的 Agent 信息
    agents_info = {}
    for name, agent in state.agents.items():
        agents_info[name] = {
            "name": agent.get("name", name),
            "status": agent.get("status", "idle"),
            "current_task": agent.get("current_task", "")[:50] if agent.get("current_task") else "",
            "last_update": agent.get("last_update", "")
        }
    
    # 只返回必要的任务信息
    tasks_info = []
    for task in state.tasks[:10]:
        tasks_info.append({
            "id": task.get("id", ""),
            "content": task.get("content", "")[:80],
            "status": task.get("status", ""),
            "created_at": task.get("created_at", "")
        })
    
    return {
        "agents": agents_info,
        "tasks": tasks_info,
        "active_tasks": len([t for t in state.tasks if t["status"] == "running"]),
        "total_tasks": len(state.tasks)
    }

@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """WebSocket 实时推送"""
    await manager.connect(websocket)
    try:
        # 立即发送当前状态
        await websocket.send_json({
            "type": "init",
            "agents": state.agents,
            "tasks": state.tasks[:10]
        })
        
        while True:
            # 保持连接，定期发送心跳
            await asyncio.sleep(5)
            await websocket.send_json({"type": "heartbeat", "time": datetime.now().isoformat()})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 启动时初始化
@app.on_event("startup")
async def startup():
    """应用启动"""
    state.load_config()
    # 延迟初始化 matrix
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
