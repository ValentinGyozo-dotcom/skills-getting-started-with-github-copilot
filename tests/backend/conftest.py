import pytest

from src.app import activities


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to a clean state before and after each test.
    This fixture ensures test isolation by clearing all participants.
    """
    # Arrange: Save original state
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }

    # Clear participants for test
    for details in activities.values():
        details["participants"] = []

    yield

    # Cleanup: Restore original state
    for name, details in activities.items():
        details["participants"] = original_participants[name]
