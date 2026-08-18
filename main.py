from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory "database" pre-filled with 3 tasks
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read FastAPI docs", "done": True},
    {"id": 3, "title": "Build CRUD API", "done": False},
]

@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}

# GET /tasks - Return all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# GET /tasks/{task_id} - Return a single task or 404 error
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )