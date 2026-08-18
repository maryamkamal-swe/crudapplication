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
    
    # Create tasks table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    # Seed 3 initial tasks only if table is empty
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

# Initialize database schema on startup
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