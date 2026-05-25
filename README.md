# Task Manager API

A lightweight FastAPI-based task and project management system.

## Features

- ✅ User authentication (JWT)
- 📁 Projects management
- ✔️ Tasks with status tracking (todo, in_progress, done)
- 📋 Subtasks under tasks (break down work into smaller items)
- 💬 Comments on tasks
- 🔍 Filter tasks by project and status
- 📅 Due dates for tasks

## Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the application**
```bash
uvicorn main:app --reload
```

3. **Access the API**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Quick Start

### 1. Register a user
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### 2. Login to get access token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

Save the `access_token` from the response.

### 3. Create a project
```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Project",
    "description": "A sample project"
  }'
```

### 4. Create a task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete API documentation",
    "description": "Write comprehensive docs",
    "project_id": 1,
    "status": "todo",
    "due_date": "2024-12-31T23:59:59"
  }'
```

### 5. Add a comment
```bash
curl -X POST "http://localhost:8000/comments" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Started working on this task",
    "task_id": 1
  }'
```

### 6. Add a subtask
```bash
curl -X POST "http://localhost:8000/tasks/1/subtasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Draft outline",
    "description": "First pass at structure",
    "status": "todo"
  }'
```

### 7. List subtasks for a task
```bash
curl -X GET "http://localhost:8000/tasks/1/subtasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login and get JWT token

### Projects
- `POST /projects` - Create project
- `GET /projects` - List all user's projects
- `GET /projects/{id}` - Get project details
- `DELETE /projects/{id}` - Delete project

### Tasks
- `POST /tasks` - Create task
- `GET /tasks` - List tasks (filter by `project_id` and `status`)
- `GET /tasks/{id}` - Get task details (includes nested `subtasks`)
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task (cascades subtasks)

### Subtasks
- `POST /tasks/{id}/subtasks` - Create subtask
- `GET /tasks/{id}/subtasks` - List subtasks for a task
- `GET /tasks/{id}/subtasks/{subtask_id}` - Get subtask details
- `PUT /tasks/{id}/subtasks/{subtask_id}` - Update subtask
- `DELETE /tasks/{id}/subtasks/{subtask_id}` - Delete subtask

### Comments
- `POST /comments` - Add comment to task
- `GET /tasks/{id}/comments` - List task comments

## Task Status Values
- `todo`
- `in_progress`
- `done`

## Project Structure
```
.
├── main.py           # FastAPI app and endpoints
├── database.py       # SQLAlchemy models and DB setup
├── schemas.py        # Pydantic schemas
├── auth.py           # Authentication utilities
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Next Steps

- Add pagination for large datasets
- Implement task assignments to multiple users
- Add file attachments
- Add search with filters
- Implement WebSocket for real-time updates
- Add email notifications
- Create frontend (React/Vue)

## Security Note

**Change the SECRET_KEY in `auth.py` before deploying to production!**
