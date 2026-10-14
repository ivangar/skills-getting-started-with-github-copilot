from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    return TestClient(app_module.app)


def test_root_redirects_to_frontend(client, test_data):
    # Arrange
    expected_location = "/static/index.html"
    test_data.update(expected_status=307, expected_location=expected_location)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client, test_data):
    # Arrange
    expected_activity = "Chess Club"
    expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
    test_data.update(
        expected_status=200,
        activity=expected_activity,
        expected_participants=expected_participants,
    )

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["participants"] == expected_participants


def test_signup_adds_participant(client, test_data):
    # Arrange
    activity_name = "Basketball Team"
    email = "student@mergington.edu"
    test_data.update(activity=activity_name, email=email, expected_status=200)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client, test_data):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = app_module.activities[activity_name]["participants"].copy()
    test_data.update(
        activity=activity_name,
        email=email,
        expected_status=400,
        original_participants=original_participants,
    )

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client, test_data):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"
    test_data.update(activity=activity_name, email=email, expected_status=404)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, test_data):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    test_data.update(activity=activity_name, email=email, expected_status=200)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_rejects_participant_not_signed_up(client, test_data):
    # Arrange
    activity_name = "Chess Club"
    email = "not-signed-up@mergington.edu"
    test_data.update(activity=activity_name, email=email, expected_status=404)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(client, test_data):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"
    test_data.update(activity=activity_name, email=email, expected_status=404)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"