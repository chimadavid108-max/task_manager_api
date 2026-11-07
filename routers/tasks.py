from typing import Literal
from fastapi import APIRouter, Query, Depends, Response
from sqlalchemy.orm import Session
import crud
from config import LIST_LIMIT, LIST_OFFSET
from database import get_db
from models import Task
from schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def all_tasks(
    q: str | None = None,
    status: Literal["todo", "in_progress", "done"] | None = None,
    priority: Literal["low", "medium", "high"] | None = None,
    limit: int = Query(LIST_LIMIT, ge=1, le=100),
    offset: int = Query(LIST_OFFSET, ge=0),
    db: Session = Depends(get_db),
) -> list[Task]:
    return crud.list_tasks(db, q, status, priority, offset, limit)


@router.get("/overdue", response_model=list[TaskOut])
def get_overdue_tasks(
    limit: int = Query(LIST_LIMIT, ge=1, le=100),
    offset: int = Query(LIST_OFFSET, ge=0),
    db: Session = Depends(get_db),
):
    return crud.overdue_tasks(db, limit, offset)


@router.get("/stats", response_model=dict[str, int | float | dict[str, int]])
def task_statistics(db: Session = Depends(get_db)):
    return crud.tasks_stats(db)


@router.get("/{task_id}", response_model=TaskOut)
def find_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    return crud.get_task(db, task_id)


@router.delete("/{task_id}", status_code=204)
def remove_task(task_id: int, db: Session = Depends(get_db)) -> Response:
    crud.delete_task(db, task_id)
    return Response(status_code=204)


@router.post("", response_model=TaskOut, status_code=201)
def add_task(data: TaskCreate, db: Session = Depends(get_db)) -> Task:
    return crud.create_task(db, data)


@router.post("/{task_id}/complete", response_model=TaskOut, status_code=200)
def complete(task_id: int, db: Session = Depends(get_db)):
    return crud.complete_task(db, task_id)


@router.post("/{task_id}/reopen", response_model=TaskOut, status_code=200)
def reopen(task_id: int, db: Session = Depends(get_db)):
    return crud.reopen_task(db, task_id)


@router.patch("/{task_id}", response_model=TaskOut)
def edit_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    return crud.update_task(db, task_id, data)
