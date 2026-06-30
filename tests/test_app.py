import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }

    for details in activities.values():
        details["participants"] = []

    yield

    for name, details in activities.items():
        details["participants"] = original_participants[name]


def test_unregister_participant_removes_them_from_activity():
    with TestClient(app) as client:
        signup_response = client.post(
            "/activities/Chess Club/signup?email=student@example.com"
        )
        assert signup_response.status_code == 200
        assert "student@example.com" in activities["Chess Club"]["participants"]

        unregister_response = client.delete(
            "/activities/Chess Club/participants/student@example.com"
        )

        assert unregister_response.status_code == 200
        assert "student@example.com" not in activities["Chess Club"]["participants"]
