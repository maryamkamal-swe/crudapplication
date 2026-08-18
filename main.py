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

# POST /tasks - Create a new task with validation
@app.post("/tasks", status_code=201)
def create_task(task_data: dict):
    title = task_data.get("title")
    
    # Input validation: return 400 if title is missing or empty
    if not title or not str(title).strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )
    
    # Generate the next free ID
    new_id = max([t["id"] for t in tasks], default=0) + 1
    
    new_task = {
        "id": new_id,
        "title": str(title).strip(),
        "done": False
    }
    
    tasks.append(new_task)
    return new_task