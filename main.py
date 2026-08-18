import sqlite3
from fastapi import FastAPI, Response
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
    
    # Create tasks table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Seed 3 initial tasks only if table is empty
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

# GET /tasks - Read all tasks
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

# GET /tasks/{task_id} - Read single task
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

# POST /tasks - Create a new task
@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task_data: dict):
    title = task_data.get("title")
    if not title or not str(title).strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )
    
    clean_title = str(title).strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (clean_title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {"id": new_id, "title": clean_title, "done": False}

# PUT /tasks/{task_id} - Update a task
@app.put("/tasks/{task_id}", summary="Update a task by ID")
def update_task(task_id: int, task_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()
    
    if existing_task is None:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )
    
    current_title = existing_task["title"]
    current_done = existing_task["done"]
    
    if "title" in task_data:
        title = task_data["title"]
        if not title or not str(title).strip():
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Title cannot be empty"}
            )
        current_title = str(title).strip()
        
    if "done" in task_data:
        current_done = 1 if bool(task_data["done"]) else 0
        
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (current_title, current_done, task_id)
    )
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": current_title, "done": bool(current_done)}

# DELETE /tasks/{task_id} - Delete a task
@app.delete("/tasks/{task_id}", summary="Delete a task by ID")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )
        
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    return Response(status_code=204)