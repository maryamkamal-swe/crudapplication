import os
import sqlite3
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

load_dotenv()

DB_FILE = os.getenv("DB_FILE", "tasks.db")

# Automatically create subdirectories if DB_FILE path includes folders (e.g., /app/data/tasks.db)
db_dir = os.path.dirname(DB_FILE)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

app = FastAPI(
    title="Task API",
    description="A SQLite-backed CRUD API running inside Docker.",
    version="3.0"
)


# --- Pydantic Schemas ---

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, example="Buy groceries")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, example="Read FastAPI docs")
    done: Optional[bool] = Field(None, example=True)


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


# --- Database Helpers ---

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
    if cursor.fetchone()[0] == 0:
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


# --- Endpoints ---

@app.get("/", summary="Get API metadata")
def get_root():
    return {
        "name": "Task API",
        "version": "3.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Server Health Check")
def get_health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskResponse], summary="Retrieve all tasks")
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


@app.get("/tasks/{task_id}", response_model=TaskResponse, summary="Retrieve a single task by ID")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.post("/tasks", response_model=TaskResponse, status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    clean_title = task.title.strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (clean_title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": clean_title, "done": False}


@app.put("/tasks/{task_id}", response_model=TaskResponse, summary="Update an existing task")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()

    if existing_task is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    current_title = existing_task["title"]
    current_done = existing_task["done"]

    if task.title is not None:
        clean_title = task.title.strip()
        if not clean_title:
            conn.close()
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        current_title = clean_title

    if task.done is not None:
        current_done = 1 if task.done else 0

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (current_title, current_done, task_id)
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": current_title, "done": bool(current_done)}


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task by ID")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return Response(status_code=204)