from datetime import date, timedelta


def test_patch_changes_only_the_changed_fields(client, make_task):
    task = make_task()
    updated = client.patch(
        f"/tasks/{task['id']}",
        json={"title": "packing code haha", "status": "in_progress"},
    ).json()

    assert task["title"] != updated["title"]
    assert task["status"] != updated["status"]
    assert task["updated_at"] != updated["updated_at"]
    assert task["description"] == updated["description"]
    assert task["due_date"] == updated["due_date"]


def test_patch_title_None_returns_422(client, make_task):
    task = make_task()
    updated = client.patch(f"/tasks/{task['id']}", json={"title": None})

    assert updated.status_code == 422


def test_patch_description_None_clears_it(client, make_task):
    task = make_task()
    updated = client.patch(f"/tasks/{task['id']}", json={"description": None}).json()

    assert updated["description"] is None


def test_patch_status_done_set_completed_at(client, make_task):
    task = make_task(status="done")
    updated = client.patch(f"/tasks/{task['id']}", json={"status": "todo"}).json()

    assert task["completed_at"] is not None
    assert updated["completed_at"] is None


def test_patch_empty_body_returns_400(client, make_task):
    task = make_task()
    response = client.patch(f"/tasks/{task['id']}", json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_patch_with_past_due_date_returns_422(client, make_task):
    task = make_task()

    response = client.patch(
        f"/tasks/{task['id']}",
        json={"due_date": (date.today() - timedelta(days=3)).isoformat()},
    )

    assert response.status_code == 422
