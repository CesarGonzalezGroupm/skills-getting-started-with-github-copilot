import pytest
from fastapi import status


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12
        assert len(data["Chess Club"]["participants"]) >= 0

    def test_get_activities_contains_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Gym%20Class/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Gym%20Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Gym Class"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email(self, client):
        """Test signup with an email already registered"""
        # Michael is already signed up for Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        client.post(
            "/activities/Gym%20Class/signup",
            params={"email": "student1@mergington.edu"}
        )
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response.status_code == status.HTTP_200_OK
        activities_data = client.get("/activities").json()
        assert "student1@mergington.edu" in activities_data["Gym Class"]["participants"]
        assert "student1@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up(self, client):
        """Test unregister for a student not signed up for the activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not registered" in response.json()["detail"]

    def test_signup_after_unregister(self, client):
        """Test that a student can sign up again after unregistering"""
        email = "michael@mergington.edu"
        # First unregister
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        # Then sign up again
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response.status_code == status.HTTP_200_OK
        activities_data = client.get("/activities").json()
        assert email in activities_data["Chess Club"]["participants"]
