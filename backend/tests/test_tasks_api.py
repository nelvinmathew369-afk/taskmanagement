import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Isolated in-memory SQLite database for testing with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_empty_database_summary_and_list(client):
    """Verify empty database returns correct summary and empty list."""
    # List tasks
    res = client.get("/tasks")
    assert res.status_code == 200
    assert res.json() == []

    # Summary
    res = client.get("/tasks/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary == {"total": 0, "pending": 0, "in_progress": 0, "completed": 0}


def test_create_task_success(client):
    """Verify task creation returns generated ID and correct fields."""
    payload = {
        "title": "Build FastAPI service",
        "description": "Implement enterprise endpoints",
        "priority": "High",
        "status": "Pending",
        "due_date": "2026-10-15"
    }
    res = client.post("/tasks", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["id"] == 1
    assert data["title"] == "Build FastAPI service"
    assert data["priority"] == "High"
    assert data["status"] == "Pending"
    assert data["due_date"] == "2026-10-15"
    assert "created_at" in data


def test_validation_reject_empty_and_whitespace_title(client):
    """Reject empty titles and whitespace-only text."""
    # Empty string
    res = client.post("/tasks", json={"title": ""})
    assert res.status_code == 422

    # Whitespace-only string
    res = client.post("/tasks", json={"title": "     "})
    assert res.status_code == 422


def test_validation_reject_invalid_priority(client):
    """Reject invalid priority values."""
    res = client.post("/tasks", json={"title": "Test task", "priority": "Urgent"})
    assert res.status_code == 422


def test_validation_reject_invalid_status(client):
    """Reject invalid status values."""
    res = client.post("/tasks", json={"title": "Test task", "status": "Finished"})
    assert res.status_code == 422


def test_validation_reject_malformed_due_date(client):
    """Reject malformed date formats."""
    # Invalid date string
    res = client.post("/tasks", json={"title": "Test task", "due_date": "15-10-2026"})
    assert res.status_code == 422

    # Invalid calendar date
    res = client.post("/tasks", json={"title": "Test task", "due_date": "2026-02-31"})
    assert res.status_code == 422


def test_get_task_by_id_and_not_found(client):
    """Test single task retrieval and 404 for non-existent IDs."""
    # 404 for non-existent ID
    res = client.get("/tasks/999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

    # Create task
    create_res = client.post("/tasks", json={"title": "Test Single Retrieval"})
    task_id = create_res.json()["id"]

    # 200 for valid ID
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Test Single Retrieval"


def test_summary_endpoint_not_intercepted_by_id(client):
    """Ensure /tasks/summary is not interpreted as /tasks/{id} with id='summary'."""
    client.post("/tasks", json={"title": "Task 1", "status": "Pending"})
    client.post("/tasks", json={"title": "Task 2", "status": "In Progress"})
    client.post("/tasks", json={"title": "Task 3", "status": "Completed"})

    res = client.get("/tasks/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total"] == 3
    assert summary["pending"] == 1
    assert summary["in_progress"] == 1
    assert summary["completed"] == 1


def test_filtering_and_search(client):
    """Test filtering by status, priority, and searching title."""
    client.post("/tasks", json={"title": "Alpha report", "priority": "High", "status": "Pending"})
    client.post("/tasks", json={"title": "Beta audit", "priority": "Low", "status": "In Progress"})
    client.post("/tasks", json={"title": "Gamma report", "priority": "High", "status": "Completed"})

    # Filter by priority
    res = client.get("/tasks?priority=High")
    assert res.status_code == 200
    assert len(res.json()) == 2

    # Filter by status
    res = client.get("/tasks?status=In Progress")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["title"] == "Beta audit"

    # Search by title
    res = client.get("/tasks?search=report")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_patch_task(client):
    """Test updating task fields with PATCH."""
    create_res = client.post("/tasks", json={"title": "Initial Title", "status": "Pending"})
    task_id = create_res.json()["id"]

    patch_res = client.patch(f"/tasks/{task_id}", json={
        "title": "Updated Title",
        "status": "In Progress",
        "priority": "High"
    })
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["title"] == "Updated Title"
    assert updated["status"] == "In Progress"
    assert updated["priority"] == "High"

    # Patch with invalid empty title should fail
    fail_res = client.patch(f"/tasks/{task_id}", json={"title": "   "})
    assert fail_res.status_code == 422


def test_delete_task(client):
    """Test deleting task and verifying 404 afterwards."""
    create_res = client.post("/tasks", json={"title": "To be deleted"})
    task_id = create_res.json()["id"]

    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == task_id

    # Second delete or get should return 404
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404
