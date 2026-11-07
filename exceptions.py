class TaskError(Exception):
    pass


class TaskNotFoundError(TaskError):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task {self.task_id} not found")


class EmptyUpdateError(TaskError):
    pass
