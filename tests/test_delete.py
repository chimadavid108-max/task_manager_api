def test_delete_same_task_twice_returns_404_at_second_delete(client, make_task):
    task = make_task()
    deletion_1 = client.delete(f"/tasks/{task['id']}")
    deletion_2 = client.delete(f"/tasks/{task['id']}")

    assert deletion_1.status_code == 204
    assert deletion_2.status_code == 404
