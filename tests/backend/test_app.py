"""
FastAPI backend tests for the Activities API.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity.
"""
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


class TestActivitiesEndpoints:
    """Test suite for activities API endpoints."""

    def test_get_activities_returns_all_activities(self):
        """
        Test that GET /activities returns all available activities.
        
        AAA Pattern:
        - Arrange: Initialize test client
        - Act: Call GET /activities
        - Assert: Verify response contains activities with correct structure
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        payload = response.json()
        assert "Chess Club" in payload
        assert payload["Chess Club"]["max_participants"] == 12
        assert payload["Chess Club"]["description"] is not None
        assert isinstance(payload["Chess Club"]["participants"], list)

    def test_root_path_redirects_to_static_index(self):
        """
        Test that GET / redirects to the static index.html.
        
        AAA Pattern:
        - Arrange: Initialize test client
        - Act: Call GET /
        - Assert: Verify redirect to static index
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in {307, 308}
        assert response.headers["location"] == "/static/index.html"


class TestSignupFlow:
    """Test suite for signup functionality."""

    def test_signup_adds_participant_to_activity(self):
        """
        Test that POST /activities/{name}/signup adds a student to an activity.
        
        AAA Pattern:
        - Arrange: Prepare test email and activity name
        - Act: Call POST /activities/Chess Club/signup with email
        - Assert: Verify participant was added and response is successful
        """
        # Arrange
        client = TestClient(app)
        test_email = "alice@school.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert test_email in activities[activity_name]["participants"]
        result = response.json()
        assert "Signed up" in result["message"]

    def test_signup_prevents_duplicate_registration(self):
        """
        Test that a student cannot sign up for the same activity twice.
        
        AAA Pattern:
        - Arrange: Sign up a student once
        - Act: Attempt to sign up the same student again
        - Assert: Verify second signup fails with 400 status
        """
        # Arrange
        client = TestClient(app)
        test_email = "bob@school.edu"
        activity_name = "Programming Class"
        
        # First signup succeeds
        first_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert first_response.status_code == 200

        # Act
        second_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"]
        # Verify only one entry in participants
        assert activities[activity_name]["participants"].count(test_email) == 1

    def test_signup_to_nonexistent_activity_fails(self):
        """
        Test that signup to a nonexistent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare invalid activity name
        - Act: Call POST with nonexistent activity
        - Assert: Verify 404 response
        """
        # Arrange
        client = TestClient(app)
        test_email = "charlie@school.edu"
        invalid_activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFlow:
    """Test suite for participant removal functionality."""

    def test_unregister_removes_participant_from_activity(self):
        """
        Test that DELETE /activities/{name}/participants/{email} removes a student.
        
        AAA Pattern:
        - Arrange: Sign up a participant
        - Act: Call DELETE to remove that participant
        - Assert: Verify participant was removed
        """
        # Arrange
        client = TestClient(app)
        test_email = "dave@school.edu"
        activity_name = "Gym Class"
        
        # Sign up first
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert unregister_response.status_code == 200
        assert test_email not in activities[activity_name]["participants"]
        result = unregister_response.json()
        assert "Removed" in result["message"]

    def test_unregister_nonexistent_participant_fails(self):
        """
        Test that unregistering a participant not signed up returns 404.
        
        AAA Pattern:
        - Arrange: Prepare email that was never signed up
        - Act: Call DELETE for that email
        - Assert: Verify 404 response
        """
        # Arrange
        client = TestClient(app)
        test_email = "eve@school.edu"
        activity_name = "Basketball Team"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_fails(self):
        """
        Test that unregistering from a nonexistent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare invalid activity name
        - Act: Call DELETE with nonexistent activity
        - Assert: Verify 404 response
        """
        # Arrange
        client = TestClient(app)
        test_email = "frank@school.edu"
        invalid_activity = "Nonexistent Club"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
