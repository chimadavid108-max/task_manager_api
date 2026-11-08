import time


def test_get_task_returns_expected_body(client, make_task):
    task = make_task()

    data = client.get(f"/tasks/{task['id']}").json()

    assert task["title"] == data["title"]
    assert task["description"] == data["description"]
    assert task["status"] == data["status"]
    assert task["due_date"] == data["due_date"]
    assert task["priority"] == data["priority"]
    assert task["completed_at"] == data["completed_at"]
    assert task["updated_at"] == data["updated_at"]


def test_get_unexisting_task_returns_404_and_body(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task 999 not found"


def test_no_filter_returns_every_tasks(client, make_task):
    for i in range(1, 6):
        make_task(title=f"Task {i}")

    data = client.get("/tasks").json()

    assert len(data) == 5


def test_get_tasks_filtered_by_status(client, make_task):
    for i in range(1, 6):
        make_task(title=f"Task {i}")
    for i in range(6, 16):
        make_task(title=f"Task {i}", status="in_progress")

    data = client.get("/tasks?status=in_progress&limit=100").json()

    assert data[0]["status"] == "in_progress"
    assert data[-1]["status"] == "in_progress"
    assert len(data) == 10


def test_get_tasks_filtered_by_priority(client, make_task):
    for i in range(1, 6):
        make_task(title=f"Task {i}")
    for i in range(6, 16):
        make_task(title=f"Task {i}", priority="high")

    data = client.get("/tasks?priority=high&limit=100").json()

    assert data[0]["priority"] == "high"
    assert data[-1]["priority"] == "high"
    assert len(data) == 10


def test_search_queries_returns_task_that_met_all_queries(client, make_task):
    make_task(title="Pay rent")
    make_task(title="Pay school fees", status="done")
    make_task(title="Write report", status="done")

    data = client.get("/tasks?q=pay&status=done").json()

    assert data[0]["title"] == "Pay school fees"
    assert len(data) == 1


def test_get_check_priority_sorting(client, make_task):
    for i in range(1, 6):
        make_task(title=f"Task {i}", priority="low")
    for i in range(6, 11):
        make_task(title=f"Task {i}", priority="medium")
    for i in range(11, 16):
        make_task(title=f"Task {i}", priority="high")

    data = client.get("/tasks?limit=15&sort_by=priority&order=desc").json()

    assert data[0]["priority"] == "high"
    assert data[5]["priority"] == "medium"


def test_get_due_date_sort_puts_None_last(client, make_task):
    make_task()
    make_task(due_date=None)
    make_task()

    data = client.get("/tasks?sort_by=due_date&order=asc").json()

    assert data[2]["due_date"] is None


def test_get_reopen_set_completed_at_to_None(client, make_task):
    task = make_task(status="done")

    data = client.post(f"/tasks/{task['id']}/reopen").json()

    assert task["completed_at"] is not None
    assert data["completed_at"] is None


def test_overdue_excludes_done_tasks(client, make_task):
    make_task(status="done")

    data = client.get("/tasks/overdue").json()

    assert len(data) == 0


def test_overdue_exclude_no_date_task(client, make_task):
    make_task(due_date=None)

    data = client.get("/tasks/overdue").json()

    assert len(data) == 0


def test_overdue_order_shows_first_overdue_task(client, make_task):
    # how do i create a past date when pydantic refuse, and i saw tge idea you agev me. But that means i will create a create_overdue endpoint for the test, because you can only add in crud
    pass


def test_get_overdue_does_not_return_422(client):
    response = client.get("/tasks/overdue")

    assert response.status_code == 200
    assert response.status_code != 422


def test_get_stats_on_empty_database_returns_zero_to_all_values(client):
    stats = client.get("/tasks/stats").json()
    by_status = stats["by_status"]
    by_priority = stats["by_priority"]

    assert stats["total"] == 0
    assert by_status["todo"] == 0
    assert by_status["in_progress"] == 0
    assert by_status["done"] == 0
    assert by_priority["low"] == 0
    assert by_priority["medium"] == 0
    assert by_priority["high"] == 0
    assert stats["overdue"] == 0
    assert stats["completion_rate"] == 0.0


def test_get_stats_counts_completion_rate_correct(client, make_task):
    for _ in range(5):
        make_task(status="done", priority="high")
    for _ in range(5):
        make_task(priority="low")
    make_task(status="in_progress")

    stats = client.get("/tasks/stats").json()
    by_status = stats["by_status"]
    by_priority = stats["by_priority"]

    assert stats["total"] == 11
    assert by_status["todo"] == 5
    assert by_status["in_progress"] == 1
    assert by_status["done"] == 5
    assert by_priority["low"] == 5
    assert by_priority["medium"] == 1
    assert by_priority["high"] == 5
    assert (
        stats["overdue"] == 0
    )  # 6 please help i need to know how to do this overdue thing
    assert stats["completion_rate"] == 0.45


def test_sort_by_nothing_use_default_created_ate_desc(client, make_task):
    make_task()
    time.sleep(0.1)
    make_task(title="The last task")

    data = client.get("/tasks").json()

    assert data[0]["title"] == "The last task"


def test_sort_by_and_order_queries(client, make_task):
    make_task(title="first task")
    time.sleep(0.1)
    make_task(title="second task", due_date="2028-01-01", priority="high")
    time.sleep(0.1)
    make_task(title="last task", due_date="2029-01-01", priority="low")

    created_at = client.get("/tasks?sort_by=created_at&order=asc").json()
    due_date = client.get("/tasks?sort_by=due_date&order=desc").json()
    priority = client.get("/tasks?sort_by=priority&order=asc").json()

    assert created_at[0]["title"] == "first task"
    assert created_at[-1]["title"] == "last task"
    assert due_date[0]["title"] == "last task"
    assert due_date[-1]["title"] == "first task"
    assert priority[0]["priority"] == "high"
    assert priority[-1]["priority"] == "low"
