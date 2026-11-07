from datetime import date
from sqlalchemy import func, or_, case
from sqlalchemy.orm import Session
from sqlalchemy.util import b
from config import LIST_LIMIT, LIST_OFFSET
from exceptions import EmptyUpdateError, TaskNotFoundError
from models import Task
from schemas import TaskCreate, TaskUpdate

priority_order = case({"high": 1, "medium": 2, "low": 3}, value=Task.priority, else_=4)


def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task:
    task = db.query(Task).filter_by(id=task_id).first()
    if task is None:
        raise TaskNotFoundError(task_id)
    return task


def list_tasks(
    db: Session,
    q: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    offset: int = LIST_OFFSET,
    limit: int = LIST_LIMIT,
) -> list[Task]:
    pattern = f"%{q}%"
    query = db.query(Task)

    if q is not None:
        query = query.filter(
            or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
        )
    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    return (
        query.order_by(
            priority_order.asc(),
            Task.due_date.nulls_last(),
            Task.created_at.desc(),
            Task.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_task(db: Session, task_id: int, data: TaskUpdate) -> Task:
    task = get_task(db, task_id)
    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise EmptyUpdateError("No fields to update")
    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id):
    task = get_task(db, task_id)
    db.delete(task)
    db.commit()


def complete_task(db: Session, task_id: int) -> Task:
    task = get_task(db, task_id)
    setattr(task, "status", "done")
    db.commit()
    db.refresh(task)
    return task


def reopen_task(db: Session, task_id: int) -> Task:
    task = get_task(db, task_id)
    setattr(task, "status", "todo")
    db.commit()
    db.refresh(task)
    return task


def overdue_tasks(
    db: Session, limit: int = LIST_LIMIT, offset: int = LIST_OFFSET
) -> list[Task]:
    query = (
        db.query(Task)
        .filter(Task.due_date is not None)
        .filter(Task.due_date < date.today())
        .filter(Task.status != "done")
    )
    return query.order_by(Task.due_date.asc()).offset(offset).limit(limit).all()


def tasks_stats(db: Session) -> dict[str, int | float | dict[str, int]]:
    total = len(db.query(Task).all())
    by_status = db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    by_priority = (
        db.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )
    overdue = len(
        db.query(Task)
        .filter(Task.due_date is not None)
        .filter(Task.due_date < date.today())
        .filter(Task.status != "done")
        .all()
    )
    done = len(
        db.query(Task)
        .filter(Task.status == "done")
        .filter(Task.completed_at is not None)
        .all()
    )
    completion_rate = round(done / total, 2) if total == 1 and done == 1 else 0.0

    return {
        "total": total,
        "by_status": dict(by_status),
        "by_priority": dict(by_priority),
        "overdue": overdue,
        "completion_rate": completion_rate,
    }
