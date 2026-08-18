from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Task API",
    description="A simple in-memory CRUD API for managing tasks.",
    version="1.0"
)

# In-memory "database" pre-filled with 3 tasks
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read FastAPI docs", "done": True},
    {"id": 3, "title": "Build CRUD API", "done": False},
]

@app.get("/", summary="Get API metadata")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check endpoint")
def get_health():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task_data: dict):
    title = task_data.get("title")
    if not title or not str(title).strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )
    
    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id,
        "title": str(title).strip(),
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", summary="Update a task by ID")
def update_task(task_id: int, task_data: dict):
    for task in tasks:
        if task["id"] == task_id:
            if "title" in task_data:
                title = task_data["title"]
                if not title or not str(title).strip():
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Title cannot be empty"}
                    )
                task["title"] = str(title).strip()
            if "done" in task_data:
                task["done"] = bool(task_data["done"])
            return task
            
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.delete("/tasks/{task_id}", summary="Delete a task by ID")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=204)
            
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )