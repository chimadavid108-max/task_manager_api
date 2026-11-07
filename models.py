from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Date
from sqlalchemy.orm import validates
from database import Base


def _utc_date():
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(String, default="todo", nullable=False)
    priority = Column(String, default="medium", nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=_utc_date, nullable=False)
    updated_at = Column(DateTime, default=_utc_date, onupdate=_utc_date, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    @validates("status")
    def set_completed_at(self, key: str, value: str) -> str:
        if value == "done" and self.completed_at is None:
            self.completed_at = _utc_date()
        if value != "done" and self.completed_at is not None:
            self.completed_at = None

        return value
