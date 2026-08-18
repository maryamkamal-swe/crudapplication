# Task API

A lightweight in-memory RESTful CRUD API built with Python and FastAPI for managing a to-do task list.

---

## 🚀 How to Install & Run

1. **Clone the repository:**
   ```bash
   git clone <YOUR-GITHUB-REPO-URL>
   cd task-api
   ```

2. **Set up virtual environment & install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install fastapi uvicorn
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`.

---

## 📑 API Endpoints

| HTTP Method | Endpoint | Description | Expected Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Metadata | 200 |
| `GET` | `/health` | Server Health Check | 200 |
| `GET` | `/tasks` | Retrieve all tasks | 200 |
| `GET` | `/tasks/{id}` | Retrieve a single task by ID | 200, 404 |
| `POST` | `/tasks` | Create a new task (validates `title`) | 201, 400 |
| `PUT` | `/tasks/{id}` | Update an existing task | 200, 400, 404 |
| `DELETE` | `/tasks/{id}` | Delete a task by ID | 204, 404 |

---

## 💻 Sample `curl -i` Request & Response

```http
HTTP/1.1 200 OK
date: Tue, 18 Aug 2026 12:45:00 GMT
server: uvicorn
content-length: 122
content-type: application/json

[
  {"id":1,"title":"Buy groceries","done":false},
  {"id":2,"title":"Read FastAPI docs","done":true},
  {"id":3,"title":"Build CRUD API","done":false}
]
```

---

## 🎨 Interactive Documentation (Swagger UI)

Interactive OpenAPI documentation is generated automatically and accessible at `http://localhost:8000/docs`.

![Swagger UI](swagger-ui.png)