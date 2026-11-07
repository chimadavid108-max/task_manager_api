from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exceptions import TaskError, TaskNotFoundError


async def task_error(request: Request, exc: TaskError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def task_not_found(request: Request, exc: TaskNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


def register_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TaskNotFoundError, task_not_found)
    app.add_exception_handler(TaskError, task_error)
