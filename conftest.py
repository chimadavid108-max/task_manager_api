import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401
from database import Base, get_db
from main import app


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def client(db_session):
    def overrides_get_db():
        yield db_session

    app.dependency_overrides[get_db] = overrides_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_task(client):
    def _make_task(**overrides):
        payload = {
            "title": "build a project",
            "description": "will build a mind blowing project",
            "due_date": "2027-01-01",
            **overrides,
        }
        response = client.post("/tasks", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make_task
