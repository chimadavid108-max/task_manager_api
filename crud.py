from datetime import date
from sqlalchemy import func, or_, case
from sqlalchemy.orm import Session
from config import LIST_LIMIT, LIST_OFFSET
from exceptions import EmptyUpdateError, TaskNotFoundError
from models import Task
from schemas import TaskCreate, TaskUpdate


def _ordering_query(sort_by, order):
    if sort_by == "priority":
        sort_column = case(
            {"low": 1, "medium": 2, "high": 3}, value=Task.priority, else_=4
        )
    elif sort_by == "due_date":
        sort_column = Task.due_date
    else:
        sort_column = Task.created_at

    if order == "desc":
        primary_sort = sort_column.desc().nulls_last()
    else:
        primary_sort = sort_column.asc().nulls_last()

    return primary_sort


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
    sort_by: str = "created_at",
    order: str = "desc",
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
        query.order_by(_ordering_query(sort_by, order), Task.id.desc())
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
        .filter(Task.due_date < date.today())
        .filter(Task.status.is_not("done"))
    )
    return query.order_by(Task.due_date.asc()).offset(offset).limit(limit).all()


def tasks_stats(db: Session) -> dict[str, int | float | dict[str, int]]:
    total = db.query(func.count(Task.id)).scalar() or 0

    by_status = db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()

    by_priority = (
        db.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )

    overdue = (
        db.query(Task)
        .filter(Task.due_date < date.today())
        .filter(Task.status.is_not("done"))
        .count()
    )

    done = (
        db.query(Task)
        .filter(Task.status == "done")
        .filter(Task.completed_at.is_not(None))
        .count()
    )

    completion_rate = round(done / total, 2) if total else 0.0

    return {
        "total": total,
        "by_status": dict(by_status),
        "by_priority": dict(by_priority),
        "overdue": overdue,
        "completion_rate": completion_rate,
    }
