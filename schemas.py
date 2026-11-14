from typing import Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict

# sir pleas i don't know how to do that error shape thing. I NEED HELP SIR. THANK YOU FOR TRAINING ME TO TRY NEW GOOD THINGS.


def _strip(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) else value


def _lowercase(value: str | None) -> str | None:
    return value.lower() if isinstance(value, str) else value


def _valid_due_date(value: date | None) -> date | None:
    if value is not None and value < date.today():
        raise ValueError("due_date cannot be in the past")
    return value


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=1000)
    status: Literal["todo", "in_progress", "done"] = Field(default="todo")
    priority: Literal["low", "medium", "high"] = Field(default="medium")
    due_date: date | None = Field(default=None)

    @field_validator("title", "description", "status", "priority", mode="before")
    @classmethod
    def strip_values(cls, value: str | None) -> str | None:
        return _strip(value)

    @field_validator("status", "priority", mode="before")
    @classmethod
    def lowercase_values(cls, value: str | None) -> str | None:
        return _lowercase(value)

    @field_validator("due_date", mode="after")
    @classmethod
    def validate_due_date(cls, value: date | None) -> date | None:
        return _valid_due_date(value)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=1000)
    status: Literal["todo", "in_progress", "done"] | None = Field(default=None)
    priority: Literal["low", "medium", "high"] | None = Field(default=None)
    due_date: date | None = None

    @field_validator("title", "description", "status", "priority", mode="before")
    @classmethod
    def strip_values(cls, value: str | None) -> str | None:
        return _strip(value)

    @field_validator("status", "priority", mode="before")
    @classmethod
    def lowercase_values(cls, value: str | None) -> str | None:
        return _lowercase(value)

    @field_validator("due_date", mode="after")
    @classmethod
    def validate_due_date(cls, value: date | None) -> date | None:
        return _valid_due_date(value)

    @field_validator("title", "status", "priority", mode="after")
    @classmethod
    def validate_empty_update(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("cannot be null; leave the field out")
        return value


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class StatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    overdue: int
    completion_rate: float
