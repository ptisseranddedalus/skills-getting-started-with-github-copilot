import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "Chess Club" in response_data
    assert response_data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert isinstance(response_data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    reset_activities()
    activity_name = "Programming Class"
    new_email = "test.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"

    response_after = client.get("/activities")
    assert new_email in response_after.json()[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    # Arrange
    reset_activities()
    activity_name = "Gym Class"
    participant_email = "john@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={participant_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"

    response_after = client.get("/activities")
    assert participant_email not in response_after.json()[activity_name]["participants"]


def test_unregister_unknown_participant_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Gym Class"
    participant_email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={participant_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
