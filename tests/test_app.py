from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)

    yield

    activities.clear()
    activities.update(deepcopy(original_activities))


@pytest.fixture()
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activity_data(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert body["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert body["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_returns_not_found_for_missing_activity(client):
    # Arrange
    missing_activity = "Drama Club"

    # Act
    response = client.post(f"/activities/{missing_activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up for this activity"}


def test_unregister_returns_not_found_for_missing_activity(client):
    # Arrange
    missing_activity = "Drama Club"

    # Act
    response = client.delete(f"/activities/{missing_activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}