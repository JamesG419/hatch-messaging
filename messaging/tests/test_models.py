import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from messaging.models import Participant


@pytest.mark.django_db
def test_create_participant_with_valid_phone_and_email():
    participant = Participant.objects.create(
        phone="+11234567890", email="test@example.com"
    )
    assert participant.phone == "+11234567890"
    assert participant.email == "test@example.com"


@pytest.mark.django_db
def test_create_participant_with_invalid_phone():
    participant = Participant(
        phone="1234567890", email="test2@example.com"  # Missing +1
    )
    with pytest.raises(ValidationError):
        participant.full_clean()


@pytest.mark.django_db
def test_create_participant_with_invalid_email():
    participant = Participant(phone="+11234567891", email="invalid-email")
    with pytest.raises(ValidationError):
        participant.full_clean()


@pytest.mark.django_db
def test_create_participant_with_null_phone_and_email():
    participant = Participant.objects.create(phone=None, email=None)
    assert participant.phone is None
    assert participant.email is None


@pytest.mark.django_db
def test_unique_phone_constraint():
    Participant.objects.create(phone="+11234567892", email="unique1@example.com")
    with pytest.raises(IntegrityError):
        Participant.objects.create(phone="+11234567892", email="unique2@example.com")


@pytest.mark.django_db
def test_unique_email_constraint():
    Participant.objects.create(phone="+11234567893", email="unique3@example.com")
    with pytest.raises(IntegrityError):
        Participant.objects.create(phone="+11234567894", email="unique3@example.com")
