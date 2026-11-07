from fastapi import FastAPI
import models  # noqa: F401
from config import API_NAME
from database import engine, Base
from handlers import register_handlers
from routers.tasks import router as tasks_router

app = FastAPI(title=API_NAME)

Base.metadata.create_all(engine)
app.include_router(tasks_router)
register_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
