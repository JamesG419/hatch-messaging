import pytest
from messaging.utils import resolve_participant
from messaging.models import Participant  # Adjust import as needed

# test resolve_participant function
@pytest.fixture
def participant_1(db):
    return Participant.objects.create(phone="1234567890", email="test@example.com")

@pytest.fixture
def participant_2(db):
    return Participant.objects.create(phone="0987654321", email="foo@bar.com")

@pytest.mark.django_db
def test_resolve_participant_by_phone(participant_1):
    participant = resolve_participant(phone="1234567890")
    assert participant is not None
    assert participant.phone == "1234567890"

@pytest.mark.django_db
def test_resolve_participant_by_email(participant_2):
    participant = resolve_participant(email="foo@bar.com")
    assert participant is not None
    assert participant.email == "foo@bar.com"

@pytest.mark.django_db
def test_resolve_participant_by_phone_and_email(participant_1):
    participant = resolve_participant(phone="1234567890", email="test@example.com")
    assert participant is not None
    assert participant.phone == "1234567890"
    assert participant.email == "test@example.com"

@pytest.mark.django_db
def test_resolve_participant_non_existent_phone():
    participant = resolve_participant(phone="0000000000")
    print(participant)
    assert participant is None

@pytest.mark.django_db
def test_resolve_participant_non_existent_email():
    participant = resolve_participant(email="foo@baz.com")
    assert participant is None

def test_resolve_participant_no_args_raises():
    with pytest.raises(Exception):
        resolve_participant()

#test resolve_conversation function
