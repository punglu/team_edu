import os

os.environ["USE_IN_MEMORY_REPOSITORY"] = "true"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_projects() -> None:
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_create_project() -> None:
    response = client.post(
        "/api/projects",
        json={
            "name": "교육용 신규 프로젝트",
            "owner_id": "member-kim",
            "owner_name": "김지훈",
            "description": "테스트 데이터",
            "start_date": "2026-07-15",
            "due_date": "2026-08-15",
            "priority": "MEDIUM",
            "invited_member_ids": [],
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "교육용 신규 프로젝트"
