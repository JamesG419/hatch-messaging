import pytest
from messaging.utils import resolve_conversation, resolve_participant


# test resolve_participant function
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


@pytest.mark.django_db
def test_resolve_participant_with_both_none():
    with pytest.raises(ValueError):
        resolve_participant(phone=None, email=None)


# Tests for resolve_conversation
@pytest.mark.django_db
def test_resolve_conversation_symmetry(participant_1, participant_2):
    conv1 = resolve_conversation(participant_1, participant_2)
    conv2 = resolve_conversation(participant_2, participant_1)
    assert conv1[0] == conv2[0]


@pytest.mark.django_db
def test_resolve_conversation_with_self(participant_1):
    conv = resolve_conversation(participant_1, participant_1)
    assert conv is not None
