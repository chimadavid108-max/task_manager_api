# Task Manager API

A REST API for creating, organizing and tracking tasks, built with Python, FastAPI, SQLAlchemy and SQLite.

## ✨ Features

### Task Management
- Create tasks with a title, description, priority, status and due date.
- Retrieve a single task by ID.
- Update tasks with partial updates (`PATCH`).
- Delete tasks.
- Mark tasks as completed and reopen them.

### Task Organization
- Filter by status and priority.
- Search the title and description.
- Sort by creation date, due date or priority, ascending or descending.
- Paginate with `limit` and `offset`.

### Productivity Tracking
- Total task count.
- Counts by status (`todo`, `in_progress`, `done`) and by priority (`low`, `medium`, `high`).
- List overdue tasks.
- Completion rate.

### Validation and Error Handling
- Validates titles and descriptions (trimmed, length limits).
- Restricts status and priority to supported values.
- Rejects past due dates on create and update.
- Manages `completed_at` automatically.
- Returns one consistent error shape: `{"detail": "..."}`.

## 🛠️ Technologies

| Technology | Purpose |
| --- | --- |
| Python | Core language |
| FastAPI | REST framework |
| SQLAlchemy | ORM |
| SQLite | Database |
| Pydantic | Validation |
| Uvicorn | ASGI server |
| Pytest, pytest-cov | Testing and coverage |
| HTTPX | Test client transport |
| Flake8, Black | Linting and formatting |

## 📁 Project Structure

```text
task_manager_api/
├── routers/
│   ├── __init__.py
│   └── tasks.py
├── tests/
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   └── test_delete.py
├── config.py
├── conftest.py
├── crud.py
├── database.py
├── exceptions.py
├── handlers.py
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
├── pytest.ini
├── .flake8
├── .gitignore
└── README.md
```

### Architecture

| File | Responsibility |
| --- | --- |
| `main.py` | Creates the app, the tables, the router and the error handlers |
| `config.py` | Reads environment variables |
| `database.py` | SQLAlchemy engine and sessions |
| `models.py` | Database model |
| `schemas.py` | Pydantic schemas and validation rules |
| `crud.py` | Database operations and business rules |
| `routers/tasks.py` | The `/tasks` endpoints |
| `exceptions.py` | Custom exceptions |
| `handlers.py` | Turns exceptions into HTTP responses |
| `conftest.py` | Shared pytest fixtures |

## 🚀 Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/chimadavid108-max/task_manager_api
cd task_manager_api
```

2. **Create a virtual environment**

```bash
python -m venv .venv
```

Activate it:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure (optional)**

Create a `.env` file in the project root:

```env
DB_PATH=task.db
LIST_LIMIT=10
LIST_OFFSET=0
```

Defaults work without a `.env` file.

5. **Run the API**

```bash
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

## 📖 Interactive Documentation

| Page | URL |
| --- | --- |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Health check | http://127.0.0.1:8000/health |

## 🔗 Endpoints

| Method | Endpoint | Description | Success | Errors |
| --- | --- | --- | --- | --- |
| POST | `/tasks` | Create a task | 201 | 422 |
| GET | `/tasks` | List tasks (filter, search, sort, paginate) | 200 | 422 |
| GET | `/tasks/overdue` | List overdue tasks | 200 | 422 |
| GET | `/tasks/stats` | Task statistics | 200 | |
| GET | `/tasks/{task_id}` | Get one task | 200 | 404, 422 |
| PATCH | `/tasks/{task_id}` | Update fields | 200 | 400, 404, 422 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 | 404 |
| POST | `/tasks/{task_id}/complete` | Mark as done | 200 | 404 |
| POST | `/tasks/{task_id}/reopen` | Set back to `todo` | 200 | 404 |
| GET | `/health` | Health check | 200 | |

### Create a task

```http
POST /tasks
Content-Type: application/json

{
  "title": "Learn FastAPI",
  "description": "Build a task management API",
  "priority": "high",
  "due_date": "2027-01-15"
}
```

Response `201 Created`:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Build a task management API",
  "status": "todo",
  "priority": "high",
  "due_date": "2027-01-15",
  "created_at": "2026-11-14T10:00:00.123456",
  "updated_at": "2026-11-14T10:00:00.123456",
  "completed_at": null
}
```

### List tasks

`GET /tasks` accepts these query parameters:

| Parameter | Description | Default |
| --- | --- | --- |
| `q` | Search title and description | none |
| `status` | `todo`, `in_progress` or `done` | none |
| `priority` | `low`, `medium` or `high` | none |
| `sort_by` | `created_at`, `due_date` or `priority` | `created_at` |
| `order` | `asc` or `desc` | `desc` |
| `limit` | Results per page (1 to 100) | 10 |
| `offset` | Results to skip | 0 |

```text
GET /tasks?status=todo
GET /tasks?q=fastapi
GET /tasks?sort_by=priority&order=desc
GET /tasks?limit=20&offset=10
GET /tasks?q=project&status=todo&priority=high&sort_by=due_date&order=asc
```

### Update a task

Send at least one field. Only the fields you send change.

```http
PATCH /tasks/1
Content-Type: application/json

{ "title": "Finish the FastAPI project", "status": "in_progress" }
```

### Complete and reopen

```text
POST /tasks/1/complete
POST /tasks/1/reopen
```

### Overdue tasks

`GET /tasks/overdue` returns unfinished tasks whose due date has passed, most overdue first. Tasks without a due date are never overdue.

### Statistics

`GET /tasks/stats`

```json
{
  "total": 14,
  "by_status": { "todo": 8, "in_progress": 1, "done": 5 },
  "by_priority": { "low": 5, "medium": 4, "high": 5 },
  "overdue": 3,
  "completion_rate": 0.36
}
```

Every status and priority key is always present, even when its count is 0. `completion_rate` is `done / total` rounded to 2 decimals (`0.0` when there are no tasks).

## 📏 Business Rules

- Titles are **not** unique.
- `completed_at` is set only while `status` is `done`. Moving to `done` sets it, moving away clears it, completing twice keeps the original time, and clients can never send it.
- `due_date` cannot be in the past on create or update.
- In `PATCH`, `title`, `status` and `priority` cannot be `null`. `description` and `due_date` can be `null` to clear them.
- Priority sorts `low < medium < high`, so `order=desc` returns `high` first.
- Tasks without a due date always sort last when sorting by `due_date`. Ties are broken by newest ID.

## 📌 Task Fields

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Unique identifier |
| `title` | string | 1 to 100 characters |
| `description` | string or null | Up to 1000 characters |
| `status` | string | `todo`, `in_progress` or `done` |
| `priority` | string | `low`, `medium` or `high` |
| `due_date` | date or null | Deadline, `YYYY-MM-DD` |
| `created_at` | datetime | Creation time (UTC) |
| `updated_at` | datetime | Last update time (UTC) |
| `completed_at` | datetime or null | Completion time (UTC) |

## 🔒 Error Responses

Every error returns `{"detail": "..."}`.

| Status | Meaning |
| --- | --- |
| 200 | OK |
| 201 | Created |
| 204 | Deleted, no body |
| 400 | Invalid operation (for example an empty `PATCH`) |
| 404 | Task not found |
| 422 | Validation failed |

```json
{ "detail": "Task 999 not found" }
```

```json
{ "detail": "title: String should have at least 1 character" }
```

```json
{ "detail": "No fields to update" }
```

## ⚙️ Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `DB_PATH` | SQLite file name, resolved inside the project folder so the database never moves with your working directory | `task.db` |
| `DATABASE_URL` | Full SQLAlchemy URL. Overrides `DB_PATH` | SQLite file from `DB_PATH` |
| `LIST_LIMIT` | Default page size | `10` |
| `LIST_OFFSET` | Default offset | `0` |

## 🧪 Running Tests

```bash
pytest                # run everything
pytest -v             # verbose
pytest tests/test_create.py -v

# coverage for the application code
pytest --cov=crud --cov=schemas --cov=routers --cov-report=term-missing
```

Tests use an isolated in-memory SQLite database, so your real `task.db` is never touched. Overdue tasks are created directly through the database session, because the API refuses past due dates.

## 🧹 Code Quality

```bash
black .
black --check .
flake8 .
```

## ⚠️ Limitations

- **No authentication.** Anyone who can reach the server can read and delete every task. Do not expose it publicly.
- Timestamps are stored and returned in UTC without a timezone suffix.
- `due_date` checks use the server's local date.
- In `q`, the characters `%` and `_` act as SQL wildcards.
- Case-insensitive search is reliable for ASCII text only (SQLite limitation).

## 🔮 Future Improvements

- User accounts and JWT authentication.
- Database migrations with Alembic.
- Docker and cloud deployment.
- Recurring tasks and reminders.

## 👨‍💻 Author

Built as a Python backend project to practice REST design, databases, validation and testing.
