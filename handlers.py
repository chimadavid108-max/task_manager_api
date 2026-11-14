from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from exceptions import TaskError, TaskNotFoundError


async def task_error(request: Request, exc: TaskError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def task_not_found(request: Request, exc: TaskNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def validation_error(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(p) for p in first["loc"] if p not in ("body", "query"))
    return JSONResponse(status_code=422, content={"detail": f"{field}: {first['msg']}"})


def register_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TaskNotFoundError, task_not_found)
    app.add_exception_handler(TaskError, task_error)
    app.add_exception_handler(RequestValidationError, validation_error)
