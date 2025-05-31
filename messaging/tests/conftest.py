import pytest
from messaging.models import Participant


@pytest.fixture
def participant_1(db):
    return Participant.objects.create(phone="1234567890", email="test@example.com")


@pytest.fixture
def participant_2(db):
    return Participant.objects.create(phone="0987654321", email="foo@bar.com")
