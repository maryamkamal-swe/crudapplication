import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Task API",
    description="A SQLite-backed CRUD API for managing tasks.",
    version="2.0"
)

DB_FILE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_tasks = [
            ("Buy groceries", 0),
            ("Read FastAPI docs", 1),
            ("Build CRUD API", 0)
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            initial_tasks
        )
        conn.commit()
        
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", summary="Get API metadata")
def get_root():
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check endpoint")
def get_health():
    return {"status": "ok"}

# GET /tasks - Read all tasks from SQLite
@app.get("/tasks", summary="List all tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]

# GET /tasks/{task_id} - Read a single task by ID from SQLite
@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )
    
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}