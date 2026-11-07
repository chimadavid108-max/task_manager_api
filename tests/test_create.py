def test_post_valid_task_returns_201(client):
    payload = {
        "title": "build a project",
        "description": "will build a mind blowing project",
        "due_date": "2027-01-01",
    }
    response = client.post("/tasks", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["completed_at"] is None


def test_post_return_stripped_title(make_task):
    task = make_task(title="  debug  ")

    assert task["title"] != "  debug  "
    assert task["title"] == "debug"


def test_post_duplicate_title_returns_201(client):
    payload = {
        "title": "build project",
        "description": "will build a mind blowing project",
        "due_date": "2027-01-01",
    }
    response1 = client.post("/tasks", json=payload)
    response2 = client.post("/tasks", json=payload)

    assert response1.status_code == 201
    assert response2.status_code == 201


def test_post_blank_title_returns_422(client):
    payload = {
        "title": "  ",
        "description": "will build a mind blowing project",
        "due_date": "2027-01-01",
    }
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_post_invalid_priority_returns_422(client):
    payload = {
        "title": "build project",
        "description": "will build a mind blowing project",
        "priority": "so_urgent",
        "due_date": "2027-01-01",
    }
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_post_invalid_status_returns_422(client):
    payload = {
        "title": "build project",
        "description": "will build a mind blowing project",
        "status": "almost_done",
        "due_date": "2027-01-01",
    }
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_post_past_due_date_return_422(client):
    payload = {
        "title": "build project",
        "description": "will build a mind blowing project",
        "due_date": "2026-01-01",
    }
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_post_empty_body_returns_400(client):
    response = client.post("/tasks", json={})

    assert response.status_code == 400


def test_complete_twice_keep_same_completed_at(client, make_task):
    task = make_task()
    complete_1 = client.post(f"/tasks/{task['id']}/complete").json()
    complete_2 = client.post(f"/tasks/{task['id']}/complete").json()

    assert complete_1["completed_at"] == complete_2["completed_at"]


def test_post_with_status_done_has_completed_at_set(make_task):
    task = make_task(status="done")

    assert task["completed_at"] is not None
